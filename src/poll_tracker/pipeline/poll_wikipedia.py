from poll_tracker.core.poll_fetcher import PollFetcher
from pathlib import Path
import json
import os
from poll_tracker.utils.utils import clean_env_var

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

        clean_env_var()

        storage_options = {
            "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
            "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
            "aws_endpoint_url": os.environ.get(
                "AWS_ENDPOINT_URL", "https://minio.lab.sspcloud.fr"
            ),
            "aws_region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        }

        for tour in ["t1", "t2"]:
            datasets[tour].write_parquet(
                config["data_path"] + f"{election_type}/{year}/{tour}/polls.parquet",
                storage_options=storage_options,
            )

        events.write_parquet(
            config["data_path"] + f"{election_type}/{year}/events.parquet",
            storage_options=storage_options,
        )
