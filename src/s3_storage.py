from pathlib import Path
import boto3


BUCKET_NAME = "fdp-api-storage-rafael-stevanato"

s3_client = boto3.client("s3")


def upload_file_to_s3(local_file_path: str, s3_key: str) -> str:
    """
    Uploads a local file to S3 and returns the S3 URI.
    """
    path = Path(local_file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {local_file_path}")

    s3_client.upload_file(str(path), BUCKET_NAME, s3_key)

    return f"s3://{BUCKET_NAME}/{s3_key}"
