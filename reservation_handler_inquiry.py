import os
import json
from reservation_status import InquiryReservationStatus
from prompts.inn_faq import generate_inn_faq
from chatgpt_api import get_chatgpt_response
from chatgpt_api import get_chatgpt_response_rag
import boto3  # type: ignore
from messages import MESSAGES


class InquiryHandler:

    def __init__(self, table_name, api_key, messages):
        self.dynamodb = boto3.resource("dynamodb")
        self.dynamo_client = boto3.client("dynamodb", region_name="ap-northeast-1")
        self.table = self.dynamodb.Table(table_name)
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.messages = messages
        self.check_reserves = {}
        self.temp_data = {}
        self.handlers = {
            InquiryReservationStatus.INQUIRY_DEFAULT: self._handle_inquiry_default,
            InquiryReservationStatus.INQUIRY_FAQ: self._handle_inquiry_faq
        }

    def handle_inquiry_step(
        self,
        status,
        user_message,
        next_status,
        user_id=None,
        unique_code=None,
        message_type=None
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


    def _handle_inquiry_default (
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_inn_faq()
        system_message = self.get_chatgpt_response(system_content, user_message)
        if system_message:
            return system_message, next_status
        else:
            return False


    def _handle_inquiry_faq(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        # system_message = self.get_chatgpt_response(system_content, user_message)
        model = "gpt-4o"
        message_template = f"{MESSAGES['RAG']}"
        system_content = generate_inn_faq()
        system_message = self.get_chatgpt_response_rag(
            user_message, model, message_template
        )

        if system_message:
            return system_message, next_status.name
        else:
            return False

    # use rag
    def get_chatgpt_response_rag(self, user_message, model, message_template):
        status = "faq"
        urls = [
            "https://www.toyoko-inn.com/support/faq/hotel/",
            "https://www.toyoko-inn.com/support/faq/reserve/",
            "https://www.toyoko-inn.com/support/faq/account/",
            "https://www.toyoko-inn.com/support/faq/facility/",
            "https://www.toyoko-inn.com/support/faq/payment/",
            "https://www.toyoko-inn.com/support/faq/club/"
        ]
        data = None
        # data = get_data_faq()
        # file_path = "prompts/text_chunks_faq.json"
        # if os.path.exists(file_path):
        #     with open(file_path, "r", encoding="utf-8") as f:
        #         text_chunks = json.load(f)
        # else:
        #     text_chunks = None
        # file_path_vectors = "prompts/vectors_faq.json"
        # if os.path.exists(file_path_vectors):
        #     with open(file_path_vectors, "r", encoding="utf-8") as f:
        #         vectors = json.load(f)
        # else:
        #     vectors = None
        return get_chatgpt_response_rag(
            user_message,
            urls,
            model,
            message_template,
            status,
            data,
            text_chunks = None,
            vectors = None,
        )

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(
            self.api_key,
            "ft:gpt-3.5-turbo-0125:personal:inn-faq-v1:AOL3qfFi",
            0,
            system_content,
            user_message,
        )
