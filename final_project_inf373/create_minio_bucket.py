import time
from minio import Minio
from minio.error import S3Error

# Подключение к MinIO
client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = "documents-bucket"

# Ждём MinIO (до 30 секунд)
for i in range(10):
    try:
        if client.bucket_exists(bucket_name):
            print(f"Bucket '{bucket_name}' уже существует.")
            break
        else:
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' создан.")
            break
    except Exception as e:
        print(f"Ожидание MinIO... попытка {i+1}/10")
        time.sleep(3)
else:
    print("❌ MinIO так и не запустился. Bucket не создан.")
