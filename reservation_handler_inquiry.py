import os
import json
from reservation_status import InquiryReservationStatus
from prompts.inn_faq import generate_inn_faq
from prompts.data_faq import get_data_faq
from chatgpt_api import get_chatgpt_response, get_chatgpt_response_rag
from linebot import LineBotApi
from linebot.models import TextSendMessage
import boto3  # type: ignore
from boto3.dynamodb.conditions import Key, Attr
from messages import MESSAGES

line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

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

    def handle_inquiry_step(self, status, user_message, next_status, user_id=None, unique_code=None, message_type=None):
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
        print("handle_inquiry_default")
        system_content = generate_inn_faq()
        system_message = self.get_chatgpt_response(system_content, user_message)
        if system_message:
            return system_message, next_status
        else:
            return False


    def _handle_inquiry_faq(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        print("handle_inquiry_faq")
        # system_content = generate_inn_faq()
        # system_message = self.get_chatgpt_response(system_content, user_message)
        model = "gpt-4o"
        message_template = f"{MESSAGES[InquiryReservationStatus.INQUIRY_FAQ.name + '_RAG']}"
        system_message = self.get_chatgpt_response_rag(
            user_message, model, message_template
        )
        if system_message:
            return system_message, next_status
        else:
            return False

    # use rag
    def get_chatgpt_response_rag(self, user_message, model, message_template):
        status = "faq"
        urls = [
            "https://www.toyoko-inn.com/support/faq/hotel/?lcl_id=ja",
            "https://www.toyoko-inn.com/support/faq/reserve/?lcl_id=ja",
            "https://www.toyoko-inn.com/support/faq/account/?lcl_id=ja",
            "https://www.toyoko-inn.com/support/faq/facility/?lcl_id=ja",
            "https://www.toyoko-inn.com/support/faq/payment/?lcl_id=ja",
            "https://www.toyoko-inn.com/support/faq/club/?lcl_id=ja"
        ]
        # data = None
        data = get_data_faq()
        file_path = "prompts/text_chunks_faq.json"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                text_chunks = json.load(f)
        else:
            text_chunks = None

        file_path_vectors = "prompts/vectors_faq.json"
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
