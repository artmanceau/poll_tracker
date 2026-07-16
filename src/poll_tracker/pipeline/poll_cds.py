from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import polars as pl
import re
from pathlib import Path
from datetime import date
import json
from poll_tracker.assets.date_utils import MONTHS
from poll_tracker.assets.polling_institute import INSTITUTE_LOOKUP


# Longest variations first (e.g. "HARRIS INTERACTIVE" before "HARRIS")
INSTITUTE_VARIATIONS = sorted(
    INSTITUTE_LOOKUP.items(),
    key=lambda x: len(x[0]),
    reverse=True,
)

def extract_institute_media(title):
    upper = title.upper()

    institute = ""
    matched_variation = ""

    for variation, canonical in INSTITUTE_VARIATIONS:
        if variation in upper:
            institute = canonical
            matched_variation = variation
            break

    media = ""
    if matched_variation:
        pos = upper.find(matched_variation)
        media = title[pos + len(matched_variation):].strip()

    media = re.sub(
        r"\b\d{1,2}\s*(?:er)?\s*"
        r"(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|"
        r"septembre|octobre|novembre|décembre|decembre)\b.*",
        "",
        media,
        flags=re.IGNORECASE,
    ).strip()

    media = re.sub(r"^[\s\-–—:|,/]+", "", media).strip()

    return institute, media


def scrape_year(page, year, base_url):
    rows = []

    page.goto(
        f"{base_url}/notices/medias/dossiers/view/{year}",
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
            month_ = potential_month if potential_month in MONTHS.keys() else ""
            day = potential_day if potential_day.isdigit() else ""
            date_ = (
                date(year, int(MONTHS[month_.lower()]), int(day))
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

                    "url": urljoin(base_url, link["href"]),
                    'url_title': urljoin(base_url, path)
                }
            )

    return rows


def scrape_notices(start_year=2016, end_year=2026, base_url="https://www.commission-des-sondages.fr"):
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for year in range(start_year, end_year + 1):
            print(f"Processing {year}")
            rows.extend(scrape_year(page, year, base_url))

        browser.close()

    return rows


if __name__ == "__main__":

    # Load config
    config_path = Path("config/cds_extraction_config.json")

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    df = (
        pl.DataFrame(scrape_notices(start_year=2016, end_year=2026, base_url=config['base_url']), infer_schema_length=None)
        .sort(["year", "month", "sondage_id"])
    )
    df.write_parquet(config['data_path'] + "commission_des_sondages_notices.parquet",
            storage_options={
                "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
                "aws_region": "us-east-1",
            },
            credential_provider=pl.CredentialProviderAWS(
                profile_name="default",
                region_name="us-east-1",
    ))
