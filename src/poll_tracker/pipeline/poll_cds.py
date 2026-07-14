from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import polars as pl
import re
from datetime import date

BASE = "https://www.commission-des-sondages.fr"

INSTITUTES = [
    "HARRIS INTERACTIVE",
    "OPINION WAY",
    "OPINIONWAY",
    "CLUSTER 17",
    "CLUSTER17",
    "IFOP",
    "ELABE",
    "IPSOS",
    "BVA",
    "CSA",
    "ODOXA",
    "VERIAN",
    "TOLUNA",
    "YOUGOV",
    "SAGIS",
    "PIGE",
]
MONTHS_FR = [
    "janvier",
    "fevrier",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "aout",
    "septembre",
    "octobre",
    "novembre",
    "decembre",
]

MONTHS = {
    "janvier": 1,
    "février": 2,
    "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12,
    "decembre": 12,
}


def extract_institute_media(title):
    upper = title.upper()

    institute = next(
        (
            inst
            for inst in sorted(INSTITUTES, key=len, reverse=True)
            if inst in upper
        ),
        "",
    )

    media = ""

    if institute:
        pos = upper.find(institute)
        media = title[pos + len(institute):].strip()

    media = re.sub(
        r"\b\d{1,2}\s*(er)?\s*(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b.*",
        "",
        media,
        flags=re.IGNORECASE,
    ).strip()

    return institute, media


def scrape_year(page, year):
    rows = []

    page.goto(
        f"{BASE}/notices/medias/dossiers/view/{year}",
        wait_until="networkidle",
    )

    soup = BeautifulSoup(page.content(), "html.parser")

    for block in soup.select("dl.accordion"):

        month_tag = block.select_one("h2.notices-mois-titre")

        if not month_tag:
            continue

        month = month_tag.get_text(strip=True)

        for link in block.select("a.pdf_download"):
            title = link.get_text(" ", strip=True)

            title_parts = title.split(' ')
            sondage_id = title_parts[0]
            processed_title = '-'.join(title_parts[1:])
            theme = title_parts[1] if len(title_parts) > 2 else ""
            institute, media = extract_institute_media(processed_title)

            potential_day = title_parts[-2] if len(title_parts) > 2 else ""
            potential_month = title_parts[-1] if len(title_parts) > 2 else ""
            month_ = potential_month if potential_month in MONTHS_FR else ""
            day = potential_day if potential_day.isdigit() else ""

            date_ = (
                date(year, MONTHS[month_.lower()], int(day))
                if day != "" and month_ != ''
                else None
            )
            path = (
                f"/notices/files/notices/"
                f"{year}/{month.split()[0].lower().replace('é', 'e')}/"
                f"{(re.sub(r"-+", "-", title.lower().replace(" ", "-").replace('.pdf', "").replace(',', "").replace(".", "")))}.pdf"
            )

            rows.append(
                {
                    "date_month": month,
                    "year": year,
                    "month": month.split()[0],
                    "day": day,
                    "month_": month_,
                    "date": date_,

                    "raw_title": title,

                    "sondage_id": sondage_id,
                    "theme": theme,
                    "title": processed_title,
                    "institute": institute,
                    "media": media,

                    "url": urljoin(BASE, link["href"]),
                    'url_title': urljoin(BASE, path)
                }
            )

    return rows


def scrape_notices(start_year=2016, end_year=2026):
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for year in range(start_year, end_year + 1):
            print(f"Processing {year}")
            rows.extend(scrape_year(page, year))

        browser.close()

    return rows


def main():
    df = (
        pl.DataFrame(scrape_notices(), infer_schema_length=None)
        .sort(["year", "month", "sondage_id"])
    )
    df.write_parquet(
        "commission_des_sondages_notices.parquet"
    )
    df.write_csv(
        "commission_des_sondages_notices.csv"
    )
    breakpoint()
    print(f"Documents: {df.height}")
    print(df.head(20))


if __name__ == "__main__":
    main()