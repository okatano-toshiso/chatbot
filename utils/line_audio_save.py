import boto3
import io
from abc import ABC, abstractmethod


class StorageStrategy(ABC):
    @abstractmethod
    def save(self, audio_content, user_id):
        pass


class S3Storage(StorageStrategy):
    def __init__(self, bucket_name, s3_key):
        self.bucket_name = bucket_name
        self.s3_key = s3_key
        self.s3 = boto3.client("s3")

    def save(self, audio_content, user_id):
        file_obj = io.BytesIO()
        for chunk in audio_content.iter_content():
            file_obj.write(chunk)
        file_obj.seek(0)
        self.s3.upload_fileobj(file_obj, self.bucket_name, self.s3_key)
        s3_url = f"s3://{self.bucket_name}/{self.s3_key}"
        return s3_url


class TmpStorage(StorageStrategy):
    def save(self, audio_content, user_id):
        file_path = f"/tmp/{user_id}_input_audio.m4a"
        with open(file_path, "wb") as file:
            for chunk in audio_content.iter_content():
                file.write(chunk)
        return file_path


class AudioSaver:
    def __init__(self, strategy: StorageStrategy):
        self.strategy = strategy

    def save_audio(self, audio_content, user_id):
        return self.strategy.save(audio_content, user_id)
