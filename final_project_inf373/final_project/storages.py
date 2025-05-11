from storages.backends.s3boto3 import S3Boto3Storage

class MinIOStorage(S3Boto3Storage):
    def url(self, name):
        url = super().url(name)
        return url.replace("https://", "http://")