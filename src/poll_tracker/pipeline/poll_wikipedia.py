from poll_tracker.core.poll_fetcher import PollFetcher
from pathlib import Path
import json
import polars as pl

if __name__ == "__main__":
    # Load class
    fetcher = PollFetcher()

    # Load config
    config_path = Path("config/wiki_extraction_config.json")
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    for year in config["years"]:
        datasets = fetcher.fetch_polls(year)
        events = fetcher.get_events(year)

        election_type = "presidentiel"

        for tour in ["t1", "t2"]:
            datasets[tour].write_parquet(
                config["data_path"] + f"{election_type}/{year}/{tour}/polls.parquet",
                storage_options={
                    "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
                    "aws_region": "us-east-1",
                },
                credential_provider=pl.CredentialProviderAWS(
                    profile_name="default",
                    region_name="us-east-1",
                ),
            )

        events.write_parquet(
            config["data_path"] + f"{election_type}/{year}/events.parquet",
            storage_options={
                "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
                "aws_region": "us-east-1",
            },
            credential_provider=pl.CredentialProviderAWS(
                profile_name="default",
                region_name="us-east-1",
            ),
        )
