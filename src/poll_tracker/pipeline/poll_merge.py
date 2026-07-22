import polars as pl

if __name__ == "__main__":
    storage_options = {
        "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
        "aws_region": "us-east-1",
    }
    credential_provider = pl.CredentialProviderAWS(
        profile_name="default",
        region_name="us-east-1",
    )

    wiki_paths = (
        pl.scan_parquet(
            "s3://arthurmanceau/poll_tracker/wiki/**/*.parquet",
            storage_options=storage_options,
            credential_provider=credential_provider,
            include_file_paths="source_path",
            missing_columns="insert",
            extra_columns="ignore",
        )
        .select("source_path")
        .collect()
    )

    paths = wiki_paths["source_path"].unique().to_list()

    all_columns = {}
    for path in paths:
        schema = pl.scan_parquet(
            path,
            storage_options=storage_options,
            credential_provider=credential_provider,
        ).collect_schema()
        all_columns.update(schema)

    wiki = pl.scan_parquet(
        "s3://arthurmanceau/poll_tracker/wiki/**/*.parquet",
        storage_options=storage_options,
        credential_provider=pl.CredentialProviderAWS(
            profile_name="default",
            region_name="us-east-1",
        ),
        include_file_paths="source_path",
        schema=all_columns,
        missing_columns="insert",
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

    X = wiki.join(cds, left_on="source_link", right_on="url_title", how="full").select(
        "source_link", "url_title"
    )
