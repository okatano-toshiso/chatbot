import os
from reservation_status import GuestReservationStatus
from chatgpt_api import get_chatgpt_response
from chatgpt_api import get_chatgpt_response_rag
import boto3  # type: ignore
from messages import MESSAGES
from prompts.data_guest import get_data_guest

reserves = {}
users = {}


class GuestHandler:
    def __init__(self, table_name, api_key, messages):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.messages = messages
        self.check_reserves = {}
        self.temp_data = {}
        self.handlers = {
            GuestReservationStatus.GUEST_RESERVATION_MENU: self._handle_guest_faq
        }

    def handle_guest_step(
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

    def _handle_guest_faq(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        # system_content = generate_inn_faq()
        # system_message = self.get_chatgpt_response(system_content, user_message)
        model = "gpt-4o"
        message_template = (
            f"{MESSAGES[GuestReservationStatus.GUEST_RESERVATION_MENU.name + '_RAG']}"
        )
        system_message = self.get_chatgpt_response_rag(
            user_message, model, message_template
        )

        if system_message:
            return system_message, next_status.name
        else:
            return False

    # use rag
    def get_chatgpt_response_rag(self, user_message, model, message_template):
        status = "guest"
        urls = []
        data = get_data_guest()
        return get_chatgpt_response_rag(
            user_message, urls, model, message_template, status, data
        )

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(
            self.api_key,
            "ft:gpt-3.5-turbo-0125:personal:inn-faq-v1:AOL3qfFi",
            0,
            system_content,
            user_message,
        )
