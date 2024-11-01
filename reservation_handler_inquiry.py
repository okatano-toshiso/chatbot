import os
from reservation_status import (
    InquiryReservationStatus
)
from prompts.inn_faq import generate_inn_faq
from chatgpt_api import get_chatgpt_response
import boto3  # type: ignore

reserves = {}
users = {}


class InquiryHandler:

    def __init__(self, table_name, api_key, messages):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.messages = messages
        self.check_reserves = {}
        self.temp_data = {}
        self.handlers = {
            InquiryReservationStatus.INQUIRY_RESERVATION_MENU : self._handle_inquiry_faq
        }

    def handle_inquiry_step(
        self, status, user_message, next_status, user_id=None, unique_code=None, message_type=None
    ):
        if status in self.handlers:
            return self.handlers[status](
                user_message, next_status, user_id=user_id, unique_code=unique_code, message_type=message_type
            )
        else:
            raise ValueError(f"Unsupported reservation status: {status}")

    def _handle_inquiry_faq(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_inn_faq()
        system_message = self.get_chatgpt_response(system_content, user_message)
        if system_message:
            return system_message, next_status.name
        else:
            return False

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(
            self.api_key, "ft:gpt-3.5-turbo-0125:personal:inn-faq-v1:AOL3qfFi", 0, system_content, user_message
        )

