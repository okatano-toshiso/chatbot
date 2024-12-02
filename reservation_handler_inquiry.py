import os
from reservation_status import InquiryReservationStatus
from prompts.inn_faq import generate_inn_faq
from chatgpt_api import get_chatgpt_response, get_chatgpt_response_rag
from linebot import LineBotApi
from linebot.models import TextSendMessage
import boto3  # type: ignore
from boto3.dynamodb.conditions import Key, Attr

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

    def get_last_two_user_messages(self, line_id: str, unique_code: str) -> list:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('dev-commapi-dymdb-api-LineChatHistory')
        response = table.query(
            KeyConditionExpression=Key('line_id').eq(line_id),
            FilterExpression=Attr('session_id').eq(unique_code), 
            ProjectionExpression='user_message',
            ScanIndexForward=False,
            Limit=2
        )
        items = response.get('Items', [])
        return items

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
        # last_messages = self.get_last_two_user_messages(user_id, unique_code)
        # line_bot_api.push_message(user_id, TextSendMessage(text="よくあるお問い合わせ についてのお問い合わせでよろしいでしょうか。こちらではよくある質問やホテルについてのお問い合わせを教えてください。"))
        system_content = generate_inn_faq()
        system_message = self.get_chatgpt_response(system_content, user_message)
        if system_message:
            return system_message, next_status
        else:
            return False


    def _handle_inquiry_faq(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_inn_faq()
        system_message = self.get_chatgpt_response(system_content, user_message)
        # system_message = self.get_chatgpt_response(system_content, user_message)
        # system_message = self.get_chatgpt_response_rag(user_message)

        if system_message:
            return system_message, next_status.name
        else:
            return False

    # use rag
    def get_chatgpt_response_rag(self, user_message):
        urls = [
            "https://www.toyoko-inn.com/support/faq/hotel/",
            # "https://www.toyoko-inn.com/support/faq/reserve/",
            # "https://www.toyoko-inn.com/support/faq/account/",
            # "https://www.toyoko-inn.com/support/faq/facility/",
            # "https://www.toyoko-inn.com/support/faq/payment/",
            # "https://www.toyoko-inn.com/support/faq/club/"
        ]
        return get_chatgpt_response_rag(user_message, urls)

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(
            self.api_key,
            "ft:gpt-3.5-turbo-0125:personal:inn-faq-v1:AOL3qfFi",
            0,
            system_content,
            user_message,
        )
