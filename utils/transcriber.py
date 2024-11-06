import openai
import boto3
import requests
from abc import ABC, abstractmethod
from utils.vocabulary_filter_utils import create_vocabulary_filter_if_not_exists


class AudioTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio_file_path, user_id):
        pass


class WhisperTranscriber(AudioTranscriber):
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def transcribe(self, audio_file_path, user_id):
        with open(audio_file_path, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                prompt="音声ファイルの言語は日本語になります",
                language="ja",
            )
        return transcription.text


class AWSTranscribeTranscriber(AudioTranscriber):
    def __init__(self, bucket_name, s3_key):
        self.s3_client = boto3.client("s3")
        self.transcribe_client = boto3.client("transcribe")
        self.bucket_name = bucket_name
        self.s3_key = s3_key

    def transcribe(self, audio_file_path, user_id):
        vocabulary_filter_name = create_vocabulary_filter_if_not_exists()
        job_name = f"transcription-job-{user_id}"
        self._delete_existing_job(job_name)
        job_uri = audio_file_path
        custom_vocabulary_name = (
            "dev-commapi-trnscrb-api-LineChatBot-CustomVocabularies"
        )
        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": job_uri},
            MediaFormat="m4a",
            LanguageCode="ja-JP",
            Settings={
                "VocabularyFilterName": vocabulary_filter_name,
                "VocabularyFilterMethod": "mask",
                "VocabularyName": custom_vocabulary_name,
            },
        )

        while True:
            result = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            status = result["TranscriptionJob"]["TranscriptionJobStatus"]
            if status in ["COMPLETED", "FAILED"]:
                break

        if status == "COMPLETED":
            transcript_uri = result["TranscriptionJob"]["Transcript"][
                "TranscriptFileUri"
            ]

            response = requests.get(transcript_uri)
            transcript_text = response.json()["results"]["transcripts"][0]["transcript"]
            return transcript_text

        else:
            raise RuntimeError(f"Transcription job failed for user {user_id}")

    def _delete_existing_job(self, job_name):
        try:
            result = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            status = result["TranscriptionJob"]["TranscriptionJobStatus"]
            if status in ["IN_PROGRESS", "COMPLETED", "FAILED"]:
                self.transcribe_client.delete_transcription_job(
                    TranscriptionJobName=job_name
                )
                print(f"Deleted existing job: {job_name}")
        except self.transcribe_client.exceptions.BadRequestException:
            pass
        except self.transcribe_client.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NotFoundException":
                pass
            else:
                raise


class TranscriberFactory:
    @staticmethod
    def get_transcriber(
        api_transcribe_type, api_key=None, bucket_name=None, s3_key=None
    ):
        if api_transcribe_type == "CHATGPT_WHISPER":
            return WhisperTranscriber(api_key)
        elif api_transcribe_type == "AWS_TRANSCRIBE":
            return AWSTranscribeTranscriber(bucket_name, s3_key)
        else:
            raise ValueError(f"Unsupported API type: {api_transcribe_type}")
