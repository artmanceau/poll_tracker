import os
import re
from datetime import date
from io import StringIO

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

from poll_tracker.utils.data_loader import DataLoader, DataUtils

from poll_tracker.assets.bloc_mapping import * 
from poll_tracker.assets.candidates import *
from poll_tracker.assets.date_utils import FRENCH_MONTHS
from poll_tracker.assets.scrapping_asset import *

class FetcherUtils:

    SEP = r"\s*[-–—]\s*"

    @staticmethod
    def _norm(s: str) -> str:
        s = s.replace("\xa0", " ").replace("\u202f", " ")
        s = s.replace(".", "")
        return " ".join(s.lower().strip().split())

    @staticmethod
    def _int_day(tok: str) -> int:
        tok = re.sub(r"[^\d]", "", tok)  # remove "er" and any nondigits
        return int(tok)

    @staticmethod
    def reference_year_for_month(month: int, year: int) -> int:
        # previous heuristic: months < May -> year 2022 else 2021
        return year if month < 5 else year - 1

    @staticmethod
    def parse_french_date_range(
        s: str, default_year: int | None = None
    ) -> tuple[date, date]:
        """
        Parse French date strings and ranges returning (start_date, end_date) as datetime.date.
        Handles:
        - single:     "8 avril" or "8 avril 2022" or "1er avril"
        - same-month: "6-8 avril" or "6 - 8 avril 2022"
        - cross-month:"31 mars - 4 avril" or "31 mars 2021 - 4 avril 2022"
        If an explicit year is present in the string it is used. If not, the function
        uses `default_year` if provided, otherwise falls back to reference_year_for_month().
        """
        if s is None:
            raise ValueError("Input is None")
        s0 = FetcherUtils._norm(str(s))

        # cross-month range: "31 mars 2021 - 4 avril 2022" (years optional per side)
        m = re.match(
            rf"^(\d{{1,2}}(?:er)?)\s+([a-zéèêûàôùç]+)(?:\s+(\d{{4}}))?\s*{FetcherUtils.SEP}\s*(\d{{1,2}}(?:er)?)\s+([a-zéèêûàôùç]+)(?:\s+(\d{{4}}))?$",
            s0,
        )
        if m:
            d1, mon1, y1_str, d2, mon2, y2_str = m.groups()
            m1 = FRENCH_MONTHS.get(mon1)
            m2 = FRENCH_MONTHS.get(mon2)
            if not m1 or not m2:
                raise ValueError(f"Unknown month: {mon1} or {mon2}")
            y1 = (
                int(y1_str)
                if y1_str
                else (
                    default_year
                    if default_year is not None
                    else FetcherUtils.reference_year_for_month(m1)
                )
            )
            y2 = (
                int(y2_str)
                if y2_str
                else (
                    default_year
                    if default_year is not None
                    else FetcherUtils.reference_year_for_month(m2)
                )
            )
            # if no explicit years and month2 < month1 assume range crosses year boundary
            if (not y1_str and not y2_str) and (m2 < m1):
                # assume year2 = year1 + 1
                y2 = y1 + 1
            start = date(y1, m1, FetcherUtils._int_day(d1))
            end = date(y2, m2, FetcherUtils._int_day(d2))
            return end

        # same-month range: "6-8 avril 2022" or "6-8 avril"
        m = re.match(
            r"^(\d{{1,2}}(?:er)?)\s*[-–—]\s*(\d{{1,2}}(?:er)?)\s+([a-zéèêûàôùç]+)(?:\s+(\d{{4}}))?$",
            s0,
        )
        if m:
            d1, d2, mon, y_str = m.groups()
            mnum = FRENCH_MONTHS.get(mon)
            if not mnum:
                raise ValueError(f"Unknown month: {mon}")
            y = (
                int(y_str)
                if y_str
                else (
                    default_year
                    if default_year is not None
                    else FetcherUtils.reference_year_for_month(mnum)
                )
            )
            start = date(y, mnum, FetcherUtils._int_day(d1))
            end = date(y, mnum, FetcherUtils._int_day(d2))
            if end < start:
                # assume end in next month/year
                em = mnum + 1
                ey = y
                if em > 12:
                    em = 1
                    ey += 1
                end = date(ey, em, FetcherUtils._int_day(d2))
            return end

        # single date: "8 avril 2022" or "1er avril"
        m = re.match(r"^(\d{{1,2}}(?:er)?)\s+([a-zéèêûàôùç]+)(?:\s+(\d{{4}}))?$", s0)
        if m:
            d, mon, y_str = m.groups()
            mnum = FRENCH_MONTHS.get(mon)
            if not mnum:
                raise ValueError(f"Unknown month: {mon}")
            y = (
                int(y_str)
                if y_str
                else (
                    default_year
                    if default_year is not None
                    else FetcherUtils.reference_year_for_month(mnum)
                )
            )
            dt = date(y, mnum, FetcherUtils._int_day(d))
            return dt

        logger.warning(f"Unrecognized date format: {s}")
        return pd.NaT

    @staticmethod
    def clean_numeric_percent(s: pd.Series) -> pd.Series:
        s = s.astype(str).str.replace("\u00a0", "", regex=False).str.strip()
        is_lt = s.str.startswith("<", na=False)
        # pct_mask = s.str.contains("%", na=False)

        # remove % and leading '<', normalize decimal comma
        t = s.str.replace("%", "", regex=False)
        t = t.str.replace(r"^[<\s]+", "", regex=True)
        t = t.str.replace(",", ".", regex=False)
        t = t.str.replace(r"[^\d\.\-]", "", regex=True)

        num = pd.to_numeric(t, errors="coerce")

        # wherever original value began with '<', divide that numeric value by 2
        num = num.where(~is_lt, num / 2.0)

        return num

    @staticmethod
    def clean_number(s):
        s = re.sub(r"\s+", " ", s.replace("\xa0", " "))
        s = re.sub(r"\[.*?\]", "", s)
        s = re.sub(r"[^\d\.\-]", "", s)
        try:
            x = int(s)
            return x
        except:
            logger.warning(f"Could not conver to valid number: {s}")
            return np.nan

