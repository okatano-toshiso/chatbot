# Import necessary modules
import os
import textwrap
import uuid
import boto3
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI
from chatgpt_api import get_chatgpt_response
from generate import generate_index, generate_judge_reset
from menu_items import MenuItem
from messages import MESSAGES
from reservation_status import (
    ReservationStatus,
    CheckReservationStatus,
    UpdateReservationStatus,
    ErrorReservationStatus,
)
from reservation_handler import ReservationHandler, ReservationStatus  # noqa: F811
from reservation_handler_check import ReservationCheckHandler
from reservation_handler_update import ReservationUpdateHandler


line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(
    api_key=OPENAI_API_KEY,
)
USER_STATUS_CODE = ReservationStatus.RESERVATION_MENU.name
USE_HISTORY = False
access_token = os.environ["ACCESS_TOKEN"]
dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
reserves_table = dynamodb.Table("dev-commapi-dymdb-api-LineChatBot")
table_name = "dev-commapi-dymdb-api-LineChatBot"
reserve = {}
reserves = {}
users = {}
unique_code = str(uuid.uuid4())


def generate_response(
    user_message: str,
    history: str = None,
    user_status_code: str = None,
    user_id: str = None,
) -> str:
    db_reserves_ref = table_name
    db_check_reserves_ref = table_name
    db_update_reserves_ref = table_name

    reservation_handler = ReservationHandler(db_reserves_ref, OPENAI_API_KEY, MESSAGES)
    reservation_check_handler = ReservationCheckHandler(
        db_check_reserves_ref, OPENAI_API_KEY, MESSAGES
    )
    reservation_update_handler = ReservationUpdateHandler(
        db_update_reserves_ref, OPENAI_API_KEY, MESSAGES
    )

    if user_status_code == ReservationStatus.RESERVATION_MENU.name:
        USER_DEFAULT_PROMPT = MESSAGES[ReservationStatus.RESERVATION_MENU.name]





        user_status_code = "USER__RESERVATION_INDEX"
        return str(USER_DEFAULT_PROMPT), user_status_code

    if user_status_code == "USER__RESERVATION_INDEX":
        system_content = generate_index()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-4o", 0, system_content, user_message
        )
        if MenuItem.NEW_RESERVATION.value in bot_response:
            RESERVATION_RECEPTION_START = MESSAGES[
                ReservationStatus.NEW_RESERVATION_START.name
            ]
            user_status_code = ReservationStatus.NEW_RESERVATION_CHECKIN.name
            return str(RESERVATION_RECEPTION_START), user_status_code
        elif MenuItem.CONFIRM_RESERVATION.value in bot_response:
            extra_datas = {"title": "予約情報の確認"}
            message_template = (
                f"{MESSAGES[CheckReservationStatus.CHECK_RESERVATION_START.name]}"
            )
            CHECK_RESERVATION_START = message_template.format(**extra_datas)
            user_status_code = CheckReservationStatus.CHECK_RESERVATION_NAME.name
            return str(CHECK_RESERVATION_START), user_status_code
        elif MenuItem.MODIFY_RESERVATION.value in bot_response:
            extra_datas = {"title": "予約情報の変更"}
            message_template = (
                f"{MESSAGES[CheckReservationStatus.CHECK_RESERVATION_START.name]}"
            )
            CHECK_RESERVATION_START = message_template.format(**extra_datas)
            user_status_code = CheckReservationStatus.CHECK_RESERVATION_NAME.name
            return str(CHECK_RESERVATION_START), user_status_code
        elif MenuItem.CANCEL_RESERVATION.value in bot_response:
            extra_datas = {"title": "予約のキャンセル"}
            message_template = (
                f"{MESSAGES[CheckReservationStatus.CHECK_RESERVATION_START.name]}"
            )
            CHECK_RESERVATION_START = message_template.format(**extra_datas)
            user_status_code = CheckReservationStatus.CHECK_RESERVATION_NAME.name
            return str(CHECK_RESERVATION_START), user_status_code
        # elif MenuItem.FAQ.value in bot_response:
        #     FAQ = "よくある質問に関してお答えいたします。"
        #     user_status_code = "FAQ"
        #     return str(FAQ), user_status_code
        else:
            ERROR_RESERVATION_MENU = MESSAGES[
                ErrorReservationStatus.ERROR_RESERVATION_MENU.name
            ]
            return str(ERROR_RESERVATION_MENU), user_status_code

    if user_status_code == ReservationStatus.NEW_RESERVATION_CHECKIN.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_CHECKIN,
            user_message,
            ReservationStatus.NEW_RESERVATION_CHECKOUT,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_CHECKOUT.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_CHECKOUT,
            user_message,
            ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON,
            user_message,
            ReservationStatus.NEW_RESERVATION_SMOKER,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_SMOKER.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_SMOKER,
            user_message,
            ReservationStatus.NEW_RESERVATION_ROOM_TYPE,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_SMOKER.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_SMOKER,
            user_message,
            ReservationStatus.NEW_RESERVATION_ROOM_TYPE,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_ROOM_TYPE_SMOKER.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_ROOM_TYPE_SMOKER,
            user_message,
            ReservationStatus.NEW_RESERVATION_NAME,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_ROOM_TYPE_NO_SMOKER.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_ROOM_TYPE_NO_SMOKER,
            user_message,
            ReservationStatus.NEW_RESERVATION_NAME,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_NAME.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_NAME,
            user_message,
            ReservationStatus.NEW_RESERVATION_ADULT,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_ADULT.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_ADULT,
            user_message,
            ReservationStatus.NEW_RESERVATION_PHONE_NUMBER,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_PHONE_NUMBER,
            user_message,
            ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM,
            user_message,
            ReservationStatus.NEW_RESERVATION_RESERVE_EXECUTE,
            user_id,
            unique_code,
        )

    if user_status_code == ReservationStatus.NEW_RESERVATION_RESERVE_EXECUTE.name:
        return reservation_handler.handle_reservation_step(
            ReservationStatus.NEW_RESERVATION_RESERVE_EXECUTE,
            user_message,
            ReservationStatus.RESERVATION_MENU,
            user_id,
            unique_code,
        )

    if user_status_code == CheckReservationStatus.CHECK_RESERVATION_NAME.name:
        return reservation_check_handler.handle_reservation_step(
            CheckReservationStatus.CHECK_RESERVATION_NAME,
            user_message,
            CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER,
            user_id,
            unique_code,
        )

    if user_status_code == CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name:
        return reservation_check_handler.handle_reservation_step(
            CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER,
            user_message,
            CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER,
            user_id,
            unique_code,
        )

    if user_status_code == CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name:
        return reservation_check_handler.handle_reservation_step(
            CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER,
            user_message,
            CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE,
            user_id,
            unique_code,
        )

    if (
        user_status_code
        == CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE.name
    ):
        return reservation_check_handler.handle_reservation_step(
            CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_START,
            user_id,
            unique_code,
        )

    if user_status_code == UpdateReservationStatus.UPDATE_RESERVATION_START.name:
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_START,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_START,
            user_id,
            unique_code,
        )

    if user_status_code == UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name:
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT,
            user_id,
            unique_code,
        )

    if user_status_code == UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name:
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM,
            user_id,
            unique_code,
        )

    if (
        user_status_code
        == UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name
    ):
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM,
            user_id,
            unique_code,
        )

    if (
        user_status_code
        == UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name
    ):
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM,
            user_id,
            unique_code,
        )

    if user_status_code == UpdateReservationStatus.UPDATE_RESERVATION_SMOKER.name:
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_SMOKER,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE,
            user_id,
            unique_code,
        )

    if (
        user_status_code
        == UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_SMOKER.name
    ):
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_SMOKER,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM,
            user_id,
            unique_code,
        )

    if (
        user_status_code
        == UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_NO_SMOKER.name
    ):
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_NO_SMOKER,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM,
            user_id,
            unique_code,
        )

    if user_status_code == UpdateReservationStatus.UPDATE_RESERVATION_NAME.name:
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_NAME,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER,
            user_id,
            unique_code,
        )

    if user_status_code == UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name:
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM,
            user_id,
            unique_code,
        )

    if user_status_code == UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name:
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE,
            user_id,
            unique_code,
        )

    if user_status_code == UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name:
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_START,
            user_id,
            unique_code,
        )

    if (
        user_status_code
        == UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM.name
    ):
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM,
            user_message,
            UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_EXECUTE,
            user_id,
            unique_code,
        )

    if (
        user_status_code
        == UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_EXECUTE.name
    ):
        return reservation_update_handler.handle_reservation_step(
            UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_EXECUTE,
            user_message,
            ReservationStatus.RESERVATION_MENU,
            user_id,
            unique_code,
        )


def reply_to_user(reply_token: str, chatgpt_response: str) -> None:
    line_bot_api.reply_message(reply_token, TextSendMessage(text=chatgpt_response))


def lambda_handler(event, context):
    headers = event["headers"]
    body = event["body"]
    signature = headers["x-line-signature"]

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {"statusCode": 400, "body": "Invalid signature"}

    return {"statusCode": 200, "body": "OK"}


def delete_session_user(unique_code, table_name, db_name):
    dynamodb = boto3.resource(db_name)
    table = dynamodb.Table(table_name)
    table.delete_item(Key={"unique_code": unique_code})


user_states = {}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent) -> None:
    global user_states
    global USER_STATUS_CODE
    user_id = event.source.user_id
    user_message = event.message.text

    system_content = generate_judge_reset()
    judge_reset = get_chatgpt_response(
        OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
    )
    if judge_reset == "True":
        user_states[user_id] = str(ReservationStatus.RESERVATION_MENU.name)
        delete_session_user(unique_code, table_name, "dynamodb")
        chatgpt_response = textwrap.dedent(f"""
        {MESSAGES[ReservationStatus.RESERVATION_MENU.name]}
        """).strip()
        reply_to_user(event.reply_token, chatgpt_response)

    history = None

    if user_id in user_states:
        user_status_code = str(user_states[user_id])
    else:
        user_status_code = str(USER_STATUS_CODE)

    chatgpt_response, user_status_code = generate_response(
        user_message, history, user_status_code, user_id
    )

    user_states[user_id] = str(user_status_code)

    reply_to_user(event.reply_token, chatgpt_response)
