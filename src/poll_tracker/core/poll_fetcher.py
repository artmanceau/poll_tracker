import re
from io import StringIO
import polars as pl
import numpy as np
import pandas as pd
import ast
import requests
from bs4 import BeautifulSoup
from loguru import logger
from poll_tracker.assets.candidates import alias_to_id
from poll_tracker.assets.date_utils import MONTHS
from poll_tracker.assets.polling_institute import INSTITUTE_LOOKUP
import polars.selectors as cs
from poll_tracker.assets.bloc_mapping import blocs, blocs_level_1, blocs_level_2, blocs_level_3
from poll_tracker.assets.scrapping_asset import table_selector, links

RESULTATS = ['Résultats', 'Résultats officiels']

def _normalize_period(expr: pl.Expr) -> pl.Expr:
    """Normalize a raw French date-range string into a canonical form.

    Handles the many shapes seen in the source tables:
      "12-13 avr."        -> "12-13 avril"
      "5 avr."            -> "5 avril"
      "28 fév. - 2 mars"  -> "28 février-2 mars"
      "du 8 au 10"        -> "8-10"            (month recovered from title later)
      "du 20 au 25 juin 1986" -> "20-25 juin 1986"
      "le 20"             -> "20"
      "11–16 mai 1987"    -> "11-16 mai 1987"  (Unicode en/em dashes)
      "14 et 15 avril"    -> "14-15 avril"     ("et" connector)
      "28 février–1er mars 1995" -> "28 février-1 mars 1995"
    """
    return (
        expr.str.to_lowercase()
        # Normalize Unicode dashes (en/em/figure dash, minus sign) to ASCII "-".
        .str.replace_all(r"[‒–—―−]", "-")
        # Drop trailing periods on abbreviations ("avr." -> "avr") and any stray dots.
        .str.replace_all(r"\.", " ")
        # "1er" / "1 er" -> "1"
        .str.replace_all(r"\b1\s*er\b", "1")
        # Range/connector words: "du X au Y" -> "X-Y", "X et Y" -> "X-Y",
        # drop "le"/"les".
        .str.replace_all(r"\bdu\b", " ")
        .str.replace_all(r"\bau\b", "-")
        .str.replace_all(r"\bet\b", "-")
        .str.replace_all(r"\bles?\b", " ")
        # Expand month abbreviations to their canonical full names. Word
        # boundaries stop these from corrupting the already-full names
        # (e.g. "\boct\b" does not match inside "octobre").
        .str.replace_all(r"\bjanv\b", "janvier")
        .str.replace_all(r"\bfévr?\b", "février")
        .str.replace_all(r"\bfevr?\b", "février")
        .str.replace_all(r"\bavr\b", "avril")
        .str.replace_all(r"\bjuil?l?\b", "juillet")
        .str.replace_all(r"\baout\b", "août")
        .str.replace_all(r"\bsept\b", "septembre")
        .str.replace_all(r"\boct\b", "octobre")
        .str.replace_all(r"\bnov\b", "novembre")
        .str.replace_all(r"\bdéc\b", "décembre")
        .str.replace_all(r"\bdec\b", "décembre")
        # Collapse separators and whitespace.
        .str.replace_all(r"\s*-\s*", "-")
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
        .str.strip_chars("-")
    )


def parse_period(expr: pl.Expr, year: int | pl.Expr, title: pl.Expr):
    expr = _normalize_period(expr)

    # month is optional so "8-10" / "20" (month comes from the title) still match.
    pattern = (
        r"^(?P<day1>\d{1,2})"
        r"(?:-(?P<day2>\d{1,2}))?"
        r"(?:\s+(?P<month>[[:alpha:]éûôàî]+))?"
        r"(?:-(?P<day3>\d{1,2})\s+(?P<month2>[[:alpha:]éûôàî]+))?"
        r"(?:\s+(?P<year>\d{4}))?$"
    )

    parts = expr.str.extract_groups(pattern)

    year_from_title = (
        title.str.extract(r"(\d{4})", group_index=1)
        if title is not None
        else pl.lit(None, dtype=pl.String)
    )

    month_from_title = (
        title.str.to_lowercase().str.extract(
            r"(janvier|février|mars|avril|mai|juin|juillet|"
            r"août|septembre|octobre|novembre|décembre)",
            group_index=1,
        )
        if title is not None
        else pl.lit(None, dtype=pl.String)
    )

    year_expr = (
        pl.coalesce(
            parts.struct.field("year"),
            year_from_title,
            year if isinstance(year, pl.Expr) else pl.lit(str(year)),
        )
        .cast(pl.Int32, strict=False)
    )

    month1_num = parts.struct.field("month").replace_strict(MONTHS, default=None)
    month2_num = parts.struct.field("month2").replace_strict(MONTHS, default=None)
    title_month_num = month_from_title.replace_strict(MONTHS, default=None)

    # Fall back to the month named in the table title when the cell omits it.
    start_month = pl.coalesce(month1_num, title_month_num).cast(pl.Int8, strict=False)
    end_month = pl.coalesce(month2_num, month1_num, title_month_num).cast(
        pl.Int8, strict=False
    )

    start_day = parts.struct.field("day1").cast(pl.Int8, strict=False)

    end_day = (
        pl.coalesce(
            parts.struct.field("day3"),
            parts.struct.field("day2"),
            parts.struct.field("day1"),
        )
        .cast(pl.Int8, strict=False)
    )

    return [
        pl.date(year_expr, start_month, start_day).alias("start_date"),
        pl.date(year_expr, end_month, end_day).alias("end_date"),
    ]


class PollFetcher:

    def __init__(self):
        self.headers = {"User-Agent": "PollFetcher/1.0 (contact@example.com)"}
        self.events = []

    @staticmethod
    def _normalize_one_col(col, idx):
                # Case 1: actual tuple column, e.g. ('Sondeur', None)
                if isinstance(col, tuple):
                    name = col[0]

                # Case 2: stringified tuple, possibly with suffix, e.g. "('', None).3"
                elif isinstance(col, str):
                    m = re.match(r"^(.*?)(\.\d+)?$", col)
                    raw = m.group(1)
                    suffix = m.group(2) or ""

                    try:
                        parsed = ast.literal_eval(raw)
                        if isinstance(parsed, tuple):
                            name = parsed[0]
                        else:
                            name = raw
                    except Exception:
                        name = raw

                    name = (name or "").strip()
                    if not name:
                        name = f"col_{idx}"
                    return f"{name}{suffix}"

                else:
                    name = str(col)

                name = (name or "").strip()
                return name if name else f"col_{idx}"

    @staticmethod
    def normalize_columns(columns):
        cleaned = [PollFetcher._normalize_one_col(col, i) for i, col in enumerate(columns)]
        seen = {}
        out = []

        for name in cleaned:
            if name in seen:
                seen[name] += 1
                out.append(f"{name}_{seen[name]}")

            else:
                seen[name] = 0
                out.append(name)

        return out

    def fetch_page(self, url):
        """Fetching page through BeautifulSoup"""
        # 1. Request page
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        html = r.text

        # 2. Tables is the table content already parsed by beautiful soup
        tables = pd.read_html(
            StringIO(html),
            skiprows=[0],
            header=0,
            extract_links="body"
        )
        # 3. We collect the additional html info (title and position in page)
        soup_tables = BeautifulSoup(html, "lxml").find_all("table")
        return tables, soup_tables

    def parse_page(self, tables, soup_tables):
        """"Create a clean parsed dict with the table and all the info needed"""
        table_dict = {}
        for idx, (df, tag) in enumerate(zip(tables, soup_tables), start=1):

            # 1. titre de la table : <caption>
            caption = tag.find("caption")
            if caption and caption.get_text(strip=True):
                title = caption.get_text(" ", strip=True)
            else:
                # sinon chercher le titre de section précédent (h1..h6)
                prev = tag.find_previous(["h1", "h2", "h3", "h4", "h5", "h6"])
                title = prev.get_text(" ", strip=True) if prev else f"table_{idx}"

            # nettoyage simple
            title = re.sub(r"\s+", " ", title).strip()

            # garantir clé unique
            key = title
            i = 1
            while key in table_dict:
                i += 1
                key = f"{title} ({i})"

            # 2. Get the table and clean it
            if getattr(df.columns, "nlevels", 1) > 1:
                df.columns = df.columns.get_level_values(1)

            # 1) normalize column names first
            df.columns = PollFetcher.normalize_columns(df.columns)

            # 2) Unnest link/elements
            for col in df.columns:
                if df[col].map(lambda x: isinstance(x, tuple)).any():
                    df[f"{col}_href"] = df[col].map(lambda x: x[1] if isinstance(x, tuple) else None)
                    df[col] = df[col].map(lambda x: x[0] if isinstance(x, tuple) else x)

            # Drop rows with only missing values
            df = df.dropna(how="all")

            # Handle events — collected as lines without variations in the cell values
            mask_rows = df.apply(lambda r: r.dropna().nunique() <= 3, axis=1)
            self.events += (
                df[mask_rows].apply(lambda r: r.dropna().iat[0], axis=1).values
            ).tolist()
            df = df[~mask_rows].reset_index(drop=True)

            # Convert to polars
            data = pl.from_pandas(df)
            
            # Normalize columns names
            # Date, Dates -> date
            # Sondeur -> source
            # Échantillon -> sample_size

            # Candidates -> candidate_id

            # Drop href

            # Replace [N x]
            if 'Candidat EPR.1' in data.columns:
                data = data.drop('Candidat EPR.1')
            if "Candidat ENS.1" in data.columns:
                data = data.drop('Candidat ENS.1')

            # Remove line Sondeur, Date, Echantillon
            # Add rolling column
            data = data.rename({
                    'Sondeur': 'source',
                    'Sondeur_href': 'source_link',
                    'Date': 'date',
                    "Dernier jour du sondage": 'date',
                    'Dates': 'date',
                    'Échantillon': 'sample_size'},
                    strict=False
                ).rename({
                    col: alias_to_id.get(col.lower(), col)
                    for col in data.columns
                }).with_columns(
                    pl.lit(key).alias('title'),
                ).drop(
                    cs.contains("href")
                ).with_columns(
                    cs.string().str.replace_all(r"\[N \d+\]", ""),
            )
            

            if 'source' in data.columns: 
                data = data.filter(pl.col('source') != 'Sondeur')

            table_dict[key] = data

        return table_dict

    @staticmethod
    def adjust_blocs(df: pl.DataFrame, blocs: list[str]) -> pl.DataFrame:
        row_sums_expr = pl.sum_horizontal([f"BR_{b}" for b in blocs])
        delta = df.select(
            ((100 - row_sums_expr) / len(blocs)).alias("delta")
        ).get_column("delta")
        return df.with_columns([
            (pl.col(f"BR_{b}") + pl.lit(delta)).alias(f'BP_{b}')
            for b in blocs
        ])

    def _add_political_trend(self, X, year, blocs):
        bloc = blocs[year]
        X = X.with_columns(
                all_scores_candidates_sum=pl.sum_horizontal(
                    cs.starts_with("C_") & cs.ends_with("_processed")
                )
            ).with_columns([
                pl.sum_horizontal([
                    pl.col(f"C_{candidate}_processed")
                    for candidate in candidates
                ]).alias(f"BR_{b}")
                for b, candidates in bloc.items()
            ]).with_columns(
                BR_GCG=(pl.col("BR_G") + pl.col("BR_CG")).round(2),
                BR_DCD=(pl.col("BR_D") + pl.col("BR_CD")).round(2),
                BR_CGCCD=(pl.col("BR_CG") + pl.col("BR_C") + pl.col("BR_CD")).round(2),
                BR_TG=(pl.col("BR_G") + pl.col("BR_CG") + pl.col("BR_C") / 2).round(2),
                BR_TD=(pl.col("BR_D") + pl.col("BR_CD") + pl.col("BR_C") / 2).round(2),
            ).with_columns(
                all_scores_bloc_sum=pl.sum_horizontal(
                    [pl.col(f'BR_{b}') for b in bloc.keys()]
                )
            ).with_columns(
                missing=100 - pl.col('all_scores_bloc_sum')
        )

        for blocs_levels in [blocs_level_1, blocs_level_2, blocs_level_3]:
            mean = X.select(
                pl.sum_horizontal([f"BR_{b}" for b in blocs_levels]).mean()
            ).item()
            assert 50 < mean < 100, f"mean {mean} not in (50, 100)"

        # Adjust each bloc level to sum to 100
        # Candidates not in bloc vote are split evenly between the blocs
        X = self.adjust_blocs(X, bloc.keys())

        # Derived adjusted columns
        X = X.with_columns(
            BP_GCG=(pl.col("BP_G") + pl.col("BP_CG")).round(2),
            BP_DCD=(pl.col("BP_D") + pl.col("BP_CD")).round(2),
            BP_CGCCD=(pl.col("BP_CG") + pl.col("BP_C") + pl.col("BP_CD")).round(2),
            BP_TG=(pl.col("BP_G") + pl.col("BP_CG") + pl.col("BP_C") / 2).round(2),
            BP_TD=(pl.col("BP_D") + pl.col("BP_CD") + pl.col("BP_C") / 2).round(2),
        )
        # Final assertions
        for blocs in [blocs_level_1, blocs_level_2, blocs_level_3]:
            mean = X.select(
                pl.sum_horizontal([f"BP_{b}" for b in blocs]).mean()
            ).item()
            assert np.isclose(mean, 100), f"mean {mean} not close to 100"

        return X

    def concat_tour(self, year, table_dict, tour):
        selector = table_selector[year][tour]
        frames = []
        started = False

        for key, df in table_dict.items():
            if key != selector["start"] and not started:
                continue

            if key == selector["start"]:
                started = True

            frames.append(
                df.unique()
                if len(df.columns) == len(set(df.columns))
                else df.select(pl.all().unique())
            )

            if key == selector["end"]:
                break

        return pl.concat(frames, how="diagonal_relaxed")

    def _parse_source(self, X):
        return X.with_columns(
            source_raw=pl.col('source')
        ).with_columns(
            pl.col("source").str.contains("(rolling)", literal=True).alias("rolling"),
            pl.col("source").str.replace_all("(rolling)", "", literal=True).str.strip_chars()
        ).with_columns(
            pl.col("source")
            .str.to_uppercase()
            .replace_strict(INSTITUTE_LOOKUP, default=None)
            .alias("source")
        )

    def _parse_sample_size(self, X):
        if 'sample_size' in X.columns:
            return X.with_columns(pl.col('sample_size').str.replace_all('\xa0', '').cast(pl.Int64, strict=False))
        else:
            return X.with_columns(sample_size=pl.lit(None))

    def _parse_date(self, X, year):
        return X.with_columns(
                parse_period(pl.col('date'), year=year, title=pl.col('title'))
            ).sort('end_date', descending=True)

    @staticmethod
    def parse_c_col(col_expr: pl.Expr) -> pl.Expr:
        return pl.struct(
            raw=col_expr,
            processed=col_expr.str.replace(r"^<\s*", "", literal=False).str.replace('-', '').str.replace(",", ".", literal=True).str.extract(r"(\d+\.?\d*)", group_index=1).cast(pl.Float64, strict=False).fill_null(0.0),
            label=col_expr.str.extract(r"^[<>~\s]*[\d.,]+\s*%?\s*(\p{L}.*)$", group_index=1).str.strip_chars(),
            sign=col_expr.str.contains(r"^<", literal=False),
        )

    def _parse_results(self, X):
        c_cols = X.select(cs.starts_with("C_")).columns
        return X.with_columns(
                self.parse_c_col(pl.col(col)).alias(col)
                for col in c_cols
            ).unnest(*c_cols, separator="_")

    def formate(self, X, year):
        # 1. Institute
        X = self._parse_source(X)
        # 2. Sample size
        X = self._parse_sample_size(X)
        # 3. Date
        X = self._parse_date(X, year)
        # 4. Candidates results
        X = self._parse_results(X)
        return X

    def add_error(self, X):
        # 1. Select all cols starting with C_, BR_, BP_
        score_cols = (
            cs.starts_with("BR_", "BP_")
            | (cs.starts_with("C_") & cs.ends_with("_processed"))
        )

        # 2. Extract the results row as a reference Series per column
        results_row = (
            X
            .filter(pl.col('source').is_in(RESULTATS))
            .select(score_cols)
        )

        # 3. Compute error columns (difference with results row) for each matching col
        matching_cols = X.select(score_cols).columns

        if results_row.height > 0:
            X = X.with_columns([
                (pl.col(c) - pl.lit(results_row.get_column(c)[0])).alias(f"E_{c}")
                for c in matching_cols
            ])

        return X

    def fetch_polls(self, year):
        """Method to get polling data for a given year"""
        logger.info(f"Getting poll data for year: {year}")

        # Fetch all tables from page
        logger.debug('Fetching from wikipedia')
        wikipedia_page_url = links[year]
        tables, soup_tables = self.fetch_page(wikipedia_page_url)
        table_dict = self.parse_page(tables, soup_tables)
        # Instantiate the datasets
        logger.debug('Concat all tables')

        poll_dataset_t1, poll_dataset_t2 = (
            self.concat_tour(year, table_dict,  "tour 1"),
            self.concat_tour(year, table_dict,  "tour 2"),
        )
        logger.debug('Reformatting')
        poll_dataset_t1 = self.formate(poll_dataset_t1, year)
        poll_dataset_t2 = self.formate(poll_dataset_t2, year)

        logger.debug("Adding political groups...")
        poll_dataset_t1 = self._add_political_trend(poll_dataset_t1, year, blocs=blocs)

        poll_dataset_t1 = self.add_error(poll_dataset_t1)
        poll_dataset_t2 = self.add_error(poll_dataset_t2)

        # Add metadata
        poll_dataset_t1 = poll_dataset_t1.with_columns(
            year=pl.lit(year),
            type=pl.lit('pres'),
            tour=pl.lit('t1')
        )
        poll_dataset_t2 = poll_dataset_t2.with_columns(
            year=pl.lit(year),
            type=pl.lit('pres'),
            tour=pl.lit('t2')
        )

        return {'t1': poll_dataset_t1, 't2': poll_dataset_t2}

    def save_s3(self, data_path, datasets, year):
        election_type = "presidentiel"
        logger.debug("Saving to S3")
        for tour in ['t1', 't2']:
            datasets[tour].write_parquet(data_path + f"{election_type}/{year}/{tour}/polls.parquet",
            storage_options={
                "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
                "aws_region": "us-east-1",
            },
            credential_provider=pl.CredentialProviderAWS(
                profile_name="default",
                region_name="us-east-1",
            ))
