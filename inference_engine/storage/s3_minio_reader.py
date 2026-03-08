import boto3

class S3MinioWriter:
    def __init__(self, bucket, endpoint, access_key, secret_key):
        self.bucket = bucket
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1"
        )

    def ensure_bucket(self):
        buckets = [b["Name"] for b in self.s3.list_buckets().get("Buckets", [])]
        if self.bucket not in buckets:
            self.s3.create_bucket(Bucket=self.bucket)

    def put_jpeg(self, key: str, data: bytes):
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType="image/jpeg",
            CacheControl="no-store"
        )
