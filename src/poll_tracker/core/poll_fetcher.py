import os
import re
from datetime import date
from io import StringIO
import polars as pl
import numpy as np
import pandas as pd
import ast
import requests
from bs4 import BeautifulSoup
from loguru import logger
from poll_tracker.assets.candidates import candidate_map, alias_to_id
from poll_tracker.assets.polling_institute import INSTITUTE_LOOKUP
import polars.selectors as cs
from poll_tracker.utils.data_loader import DataLoader, DataUtils

from poll_tracker.assets.bloc_mapping import * 
from poll_tracker.assets.candidates import *
from poll_tracker.assets.date_utils import FRENCH_MONTHS
from poll_tracker.assets.scrapping_asset import table_selector, links
from poll_tracker.core.fetcher_utils import FetcherUtils



MONTHS = {
    "janvier": "01",
    "février": "02",
    "mars": "03",
    "avril": "04",
    "mai": "05",
    "juin": "06",
    "juillet": "07",
    "août": "08",
    "septembre": "09",
    "octobre": "10",
    "novembre": "11",
    "décembre": "12",
}

MONTH_EXPR = pl.col("month").replace(MONTHS)
MONTH2_EXPR = pl.col("month2").replace(MONTHS)


def parse_period(expr: pl.Expr, year: int | pl.Expr, title:pl.Expr):
    expr = (
        expr.str.to_lowercase()
        .str.replace_all("1er", "1")
        .str.replace_all(r"\s*-\s*", "-")
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
    )

    pattern = (
        r"^(?P<day1>\d{1,2})"
        r"(?:-(?P<day2>\d{1,2}))?"
        r"\s+(?P<month>[[:alpha:]éûôàî]+)"
        r"(?:-(?P<day3>\d{1,2})\s+(?P<month2>[[:alpha:]éûôàî]+))?"
        r"(?:\s+(?P<year>\d{4}))?$"
    )

    parts = expr.str.extract_groups(pattern)

    year_from_title = (
        title.str.extract(r"(\d{4})", group_index=1)
        if title is not None
        else pl.lit(None, dtype=pl.String)
    )

    year_expr = (
        pl.coalesce(
            parts.struct.field("year"),       
            year_from_title,             
            year if isinstance(year, pl.Expr) else pl.lit(str(year)),
        )
        .cast(pl.Int32)
    )

    start_month = parts.struct.field("month").replace(MONTHS).cast(pl.Int8)

    end_month = (
        pl.when(parts.struct.field("month2").is_not_null())
        .then(parts.struct.field("month2").replace(MONTHS))
        .otherwise(parts.struct.field("month").replace(MONTHS))
        .cast(pl.Int8)
    )

    start_day = parts.struct.field("day1").cast(pl.Int8)

    end_day = (
        pl.when(parts.struct.field("day3").is_not_null())
        .then(parts.struct.field("day3"))
        .when(parts.struct.field("day2").is_not_null())
        .then(parts.struct.field("day2"))
        .otherwise(parts.struct.field("day1"))
        .cast(pl.Int8)
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

            # Remove line Sondeur, Date, Echantillon

            # Add rolling column
            data = data.rename({
                'Sondeur': 'source',
                'Sondeur_href': 'source_link',
                'Date': 'date',
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

    # Dep
    def _formate(self, X, year):
        logger.debug("Reformating...")
        X = X.copy(deep=True)
        X[["Sondeur", "Dates"]] = X[["Sondeur", "Dates"]].astype(str)
        X.loc[X["Sondeur"] == "Harris Interractive", "Sondeur"] = "Harris Interactive"
        X.loc[X["Sondeur"] == "Cluster 17", "Sondeur"] = "Cluster17"
        X.loc[X["Sondeur"] == "Opinionway", "Sondeur"] = "OpinionWay"
        X.loc[:, "Dates_pd"] = X.loc[:, "Dates"].apply(
            lambda s: FetcherUtils.parse_french_date_range(s, default_year=int(year))
        )
        if "Échantillon" in X.columns:
            X.loc[0, "Échantillon"] = FetcherUtils.clean_number(X.loc[0, "Échantillon"])
            X["Échantillon"] = (
                X["Échantillon"].astype(str).str.replace("\u00a0", "", regex=False)
            )
        for col in X.columns:
            if col not in ["Sondeur", "Dates", "Échantillon", "Dates_pd"]:
                X[col] = FetcherUtils.clean_numeric_percent(X[col])
        return X

    # Dep
    def _restrict_candidates(self, X, year):
        logger.debug("Restricting the candidate list to the actual candidates")
        X = X.copy(deep=True)
        candidates = candidates_list[year]
        if "Abstention" in X.columns:
            X = X.drop(columns="Abstention")
        if "Indécis (échantillon)" in X.columns:
            X = X.drop(columns="Indécis (échantillon)")
        if "Indécis" in X.columns:
            X = X.drop(columns="Indécis")
        not_candidate_cols = list(
            set(X.columns)
            - set(
                candidates + ["Dates", "Dates_pd", "Échantillon", "Sondeur", "Autres"]
            )
        )
        X["Autres"] = X[not_candidate_cols].sum(axis=1)
        X.drop(columns=[c for c in not_candidate_cols if c in X.columns], inplace=True)

        mask = np.abs(X[candidates + ["Autres"]].sum(axis=1) - 100) > 10
        X.drop(index=X[mask].index, inplace=True)
        logger.warning(
            f"Dropping {mask.astype(int).sum()} because of inconsistent results"
        )

        assert np.abs(X[candidates + ["Autres"]].sum(axis=1).mean() - 100.0) < 2
        return X

    # Refactor
    def _add_political_trend(self, X, year):
        logger.debug("Adding political groups...")
        bloc = blocs[year]
        X = X.copy(deep=True)
        for b, canditates in bloc.items():
            X[f"{b}_raw"] = X[canditates].sum(axis=1)

        X["GCG_raw"] = X["G_raw"] + X["CG_raw"] / 2
        X["DCD_raw"] = X["D_raw"] + X["CD_raw"] / 2
        X["TG_raw"] = X["G_raw"] + X["CG_raw"] + X["C_raw"] / 2
        X["TD_raw"] = X["D_raw"] + X["CD_raw"] + X["C_raw"] / 2

        assert 50 < X[[f"{b}_raw" for b in blocs_level_1]].sum(axis=1).mean() < 100
        assert 50 < X[[f"{b}_raw" for b in blocs_level_2]].sum(axis=1).mean() < 100
        assert 50 < X[[f"{b}_raw" for b in blocs_level_3]].sum(axis=1).mean() < 100

        # Adjust to make them sum to 1
        delta_1 = (
            100 - X[[f"{b}_raw" for b in blocs_level_1]].sum(axis=1).mean()
        ) / len(blocs_level_1)
        for bloc in blocs_level_1:
            X[bloc] = X[f"{bloc}_raw"] + delta_1

        X["GCG"] = X["G"] + X["CG"]
        X["DCD"] = X["D"] + X["CD"]
        X["TG"] = X["G"] + X["CG"] + X["C"] / 2
        X["TD"] = X["D"] + X["CD"] + X["C"] / 2

        assert np.isclose(X[blocs_level_1].sum(axis=1).mean(), 100)
        assert np.isclose(X[blocs_level_2].sum(axis=1).mean(), 100)
        assert np.isclose(X[blocs_level_3].sum(axis=1).mean(), 100)

        return X

    # Dep
    def _note_col_handling(self, X: pl.DataFrame) -> pl.DataFrame:
        X = X.drop([c for c in X.columns if c.startswith("Unnamed")])

        n5_cols = [c for c in X.columns if re.search(r"\[N\s*5\]", c)]

        for col in n5_cols:
            matching_col = re.sub(r"\s*\[N\s*5\]\s*", " ", col).strip()

            if matching_col in X.columns:
                X = X.with_columns(
                    pl.coalesce(
                        [pl.col(matching_col), pl.col(col)]
                    ).alias(matching_col)
                ).drop(col)

        return X

    # Dep
    def _note_col_handling_(self, X):
        X = X.copy(deep=True)
        X = X.loc[:, ~X.columns.str.startswith("Unnamed")]
        # Reconcile columns with almosth the same name
        n5_cols = X.columns[X.columns.str.contains(r"\[N 5\]")]
        for col in n5_cols:
            matching_col = re.sub(r"\s*\[N\s*5\]\s*", " ", str(col))
            print(matching_col in X.columns)
            idx = X[col].dropna().index
            X.loc[idx, matching_col] = X.loc[idx, col].values
        return X

    # Dep
    def concat_t2(self, year, table_dict):
        if table_selector[year]["tour 2"]["element2"] is not None:
            return pd.concat(
                [
                    table_dict[table_selector[year]["tour 2"]["element1"]],
                    table_dict[table_selector[year]["tour 2"]["element2"]],
                ],
                ignore_index=True,
            )
        else:
            return table_dict[table_selector[year]["tour 2"]["element1"]]

    # Dep
    def concat_t1(self, year, table_dict):
        X = pd.DataFrame()
        started = False
        for key, df in table_dict.items():
            if key != table_selector[year]["tour 1"]["start"] and (not started):
                continue
            elif key == table_selector[year]["tour 1"]["start"]:
                started = True

            X = X.loc[:, ~X.columns.duplicated()]
            df = df.loc[:, ~df.columns.duplicated()]
            X = pd.concat([X, df], ignore_index=True)

            if key == table_selector[year]["tour 1"]["end"]:
                break
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
        return X.with_columns(pl.col('sample_size').str.replace_all('\xa0', '').cast(pl.Int64, strict=False))

    def _parse_date(self, X):
        return X.with_columns(
                parse_period(pl.col('date'), year=2022, title=pl.col('title'))
            ).sort('end_date')

    @staticmethod
    def parse_c_col(col_expr: pl.Expr) -> pl.Expr:
        return pl.struct(
            raw=col_expr,
            processed=col_expr.str.replace(r"^<\s*", "", literal=False).str.replace(",", ".", literal=True).str.extract(r"(\d+\.?\d*)", group_index=1).cast(pl.Float64, strict=False),
            label=col_expr.str.extract(r"%\s*([A-Za-z].+)$", group_index=1).str.strip_chars(),
            sign=col_expr.str.contains(r"^<", literal=False),
        )

    def _parse_results(self, X):
        c_cols = X.select(cs.starts_with("C_")).columns
        return X.with_columns(
                self.parse_c_col(pl.col(col)).alias(col)
                for col in c_cols
            ).unnest(*c_cols, separator="_")

    def formate(self, X):
        # 1. Institute
        X = self._parse_source(X)
        # 2. Sample size
        X = self._parse_sample_size(X)
        # 3. Date
        X = self._parse_date(X)
        # 4. Candidates results
        X = self._parse_results(X)
        return X

    def fetch_polls(self, year):
        """Method to get polling data for a given year"""
        logger.info(f"Getting poll data for year: {year}")

        # Fetch all tables from page
        wikipedia_page_url = links[year]
        tables, soup_tables = self.fetch_page(wikipedia_page_url)
        table_dict = self.parse_page(tables, soup_tables)

        # Instantiate the datasets
        poll_dataset_t1, poll_dataset_t2 = (
            self.concat_tour(year, table_dict,  "tour 1"),
            self.concat_tour(year, table_dict,  "tour 2"),
        )

        poll_dataset_t1 = self.formate(poll_dataset_t1)
        poll_dataset_t2 = self.formate(poll_dataset_t2)

        poll_dataset_t1 = self._add_political_trend(poll_dataset_t1, year)

        return {'t1': poll_dataset_t1, 't2': poll_dataset_t2}

    def save_s3(self, data_path, datasets, year):
        election_type = "presidentiel"
        logger.debug("Saving to S3")
        t1, t2 = datasets
        for tour in ['t1', 't2']:
            if not DataUtils._detect_s3(data_path):
                os.makedirs(f"{data_path}/{election_type}/{year}/{tour}", exist_ok=True)

            DataLoader.write_dataset(
                datasets['tour'],
                data_path + f"{election_type}/{year}/{tour}/polls.parquet",
            )
