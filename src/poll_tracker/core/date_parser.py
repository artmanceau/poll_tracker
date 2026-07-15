import polars as pl

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


def parse_period(expr: pl.Expr, year: int | pl.Expr):
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

    year_expr = (
        pl.coalesce(
            parts.struct.field("year"),
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