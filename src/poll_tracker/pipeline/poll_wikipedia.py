from poll_tracker.core.poll_fetcher import PollFetcher


# In config
YEARS = ["2022",  "2012", "2017", "2007", "2027"]  # , "1988"]  Bug with 1988

data_path = "s3://arthurmanceau/poll_tracker/data/polls/"
# data_path = "data/polls/"

# Implement through real CLI
if __name__ == "__main__":

    # Load class
    fetcher = PollFetcher()

    # Load config

    for year in YEARS:
        datasets = fetcher.fetch_polls(year)
        fetcher.save_s3(data_path, datasets, year)
