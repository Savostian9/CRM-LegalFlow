import os
from storages.backends.s3boto3 import S3Boto3Storage

class SafeS3Boto3Storage(S3Boto3Storage):
    """
    Storage wrapper that prevents deletions when SAFE_STORAGE_NO_DELETE=1.
    Useful to guarantee that uploaded files are never removed by app logic.
    """
    def delete(self, name):
        if os.getenv('SAFE_STORAGE_NO_DELETE', '').strip().lower() in {'1','true','yes','on'}:
            # Skip deletion silently
            return None
        return super().delete(name)
