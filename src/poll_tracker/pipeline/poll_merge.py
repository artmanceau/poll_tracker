import polars as pl

if __name__=='__main__':

    wiki = pl.scan_parquet(
        "s3://arthurmanceau/poll_tracker/polls/**/*.parquet",
        storage_options={
            "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
            "aws_region": "us-east-1",
        },
        credential_provider=pl.CredentialProviderAWS(
            profile_name="default",
            region_name="us-east-1",
        ),
        include_file_paths="source_path",
        missing_columns='insert'
    ).collect()

    cds = pl.scan_parquet(
        "s3://arthurmanceau/poll_tracker/cds/",
        storage_options={
            "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
            "aws_region": "us-east-1",
        },
        credential_provider=pl.CredentialProviderAWS(
            profile_name="default",
            region_name="us-east-1",
        ),
    ).collect()
    breakpoint()
