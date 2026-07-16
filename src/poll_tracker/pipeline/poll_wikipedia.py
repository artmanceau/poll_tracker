from poll_tracker.core.poll_fetcher import PollFetcher
from pathlib import Path
import json


if __name__ == "__main__":

    # Load class
    fetcher = PollFetcher()

    # Load config
    config_path = Path("config/wiki_extraction_config.json")
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    for year in config['years']:
        datasets = fetcher.fetch_polls(year)
        fetcher.save_s3(config['data_path'], datasets, year)
