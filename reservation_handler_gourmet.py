import os
import json
from reservation_status import GourmetReservationStatus
from prompts.data_gourmet import get_data_gourmet
from chatgpt_api import get_chatgpt_response
from chatgpt_api import get_chatgpt_response_rag
import boto3  # type: ignore
from messages import MESSAGES

reserves = {}
users = {}


class GourmetHandler:
    def __init__(self, table_name, api_key, messages):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.messages = messages
        self.check_reserves = {}
        self.temp_data = {}
        self.handlers = {
            GourmetReservationStatus.GOURMET_RESERVATION_MENU: self._handle_gourmet_faq
        }

    def handle_gourmet_step(
        self,
        status,
        user_message,
        next_status,
        user_id=None,
        unique_code=None,
        message_type=None,
    ):
        if status in self.handlers:
            return self.handlers[status](
                user_message,
                next_status,
                user_id=user_id,
                unique_code=unique_code,
                message_type=message_type,
            )
        else:
            raise ValueError(f"Unsupported reservation status: {status}")

    def _handle_gourmet_faq(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        # system_content = generate_inn_faq()
        # system_message = self.get_chatgpt_response(system_content, user_message)
        model = "gpt-4o"
        message_template = f"{MESSAGES[GourmetReservationStatus.GOURMET_RESERVATION_MENU.name + '_RAG']}"
        system_message = self.get_chatgpt_response_rag(
            user_message, model, message_template
        )

        if system_message:
            return system_message, next_status
        else:
            return False

    # use rag
    def get_chatgpt_response_rag(self, user_message, model, message_template):
        status = "gourmet"
        urls = [
            "https://tabelog.com/tokyo/A1315/A131502/R1901/rstLst/RC/?SrtT=rt&Srt=D&sort_mode=1",
        ]
        # data = None
        data = get_data_gourmet()
        file_path_chunks = "prompts/text_chunks_gourmet.json"
        if os.path.exists(file_path_chunks):
            with open(file_path_chunks, "r", encoding="utf-8") as f:
                text_chunks = json.load(f)
        else:
            text_chunks = None

        file_path_vectors = "prompts/vectors_gourmet.json"
        if os.path.exists(file_path_vectors):
            with open(file_path_vectors, "r", encoding="utf-8") as f:
                vectors = json.load(f)
        else:
            vectors = None

        return get_chatgpt_response_rag(
            user_message,
            urls,
            model,
            message_template,
            status,
            data,
            text_chunks,
            vectors,
        )

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(
            self.api_key,
            "ft:gpt-4o-2024-08-06:personal:all-data-v2:Ag4Ia22i",
            0,
            system_content,
            user_message,
        )
