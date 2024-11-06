# Import necessary modules
import os
import textwrap
import uuid
import boto3
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    AudioMessage,
    TextSendMessage,
    AudioSendMessage,
)
from openai import OpenAI
from boto3.dynamodb.conditions import Key
from chatgpt_api import get_chatgpt_response
from prompts.judge_start_inquiry import generate_judge_start_inquiry
from prompts.judge_reset import generate_judge_reset
from menu_items import MenuItem
from messages import MESSAGES
from reservation_status import (
    ReservationStatus,
    CheckReservationStatus,
    UpdateReservationStatus,
    ErrorReservationStatus,
    InquiryReservationStatus,
    GourmetReservationStatus,
    TourismReservationStatus,
    GuestReservationStatus,
)
from reservation_handler import ReservationHandler, ReservationStatus  # noqa: F811
from reservation_handler_check import ReservationCheckHandler
from reservation_handler_update import ReservationUpdateHandler
from reservation_handler_inquiry import InquiryHandler
from reservation_handler_gourmet import GourmetHandler
from reservation_handler_tourism import TourismHandler
from reservation_handler_guest import GuestHandler

from datetime import datetime, timedelta
from utils.line_audio_save import AudioSaver, S3Storage, TmpStorage
from utils.line_speech_save import LineSpeechSave
from utils.transcriber import TranscriberFactory

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
history_table = dynamodb.Table("dev-commapi-dymdb-api-LineChatHistory")
history_table_name = "dev-commapi-dymdb-api-LineChatHistory"

reserve = {}
reserves = {}
users = {}
unique_code = str(uuid.uuid4())

# CHATGPT_WHISPER or AWS_TRANSCRIBE
api_transcribe_type = os.environ["API_TRANSCRIBE_TYPE"]
polly_client = boto3.client("polly")

s3_client = boto3.client("s3")
bucket_name = os.environ["BUCKET_NAME"]


def process_audio(event, line_bot_api, user_id, storage_method="tmp"):
    audio_id = event.message.id
    audio_content = line_bot_api.get_message_content(audio_id)

    if storage_method == "s3":
        s3_key = user_id + "_audio.m4a"
        storage_strategy = S3Storage(bucket_name, s3_key)
    else:
        storage_strategy = TmpStorage()

    audio_saver = AudioSaver(storage_strategy)
    file_location = audio_saver.save_audio(audio_content, user_id)

    return file_location


def process_audio_transcription(
    event,
    line_bot_api,
    user_id,
    api_transcribe_type,
    audio_file_path,
    api_key=None,
    bucket_name=None,
    s3_key=None,
):
    transcriber = TranscriberFactory.get_transcriber(
        api_transcribe_type, api_key, bucket_name, s3_key
    )
    return transcriber.transcribe(audio_file_path, user_id)


def generate_response(
    user_message: str,
    history: str = None,
    user_status_code: str = None,
    user_id: str = None,
    display_name: str = None,
    message_type: str = None,
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
    inquiry_handler = InquiryHandler(db_reserves_ref, OPENAI_API_KEY, MESSAGES)
    gourmet_handler = GourmetHandler(db_reserves_ref, OPENAI_API_KEY, MESSAGES)
    tourism_handler = TourismHandler(db_reserves_ref, OPENAI_API_KEY, MESSAGES)
    guest_handler = GuestHandler(db_reserves_ref, OPENAI_API_KEY, MESSAGES)

    if user_status_code == ReservationStatus.RESERVATION_MENU.name:
        USER_DEFAULT_PROMPT = MESSAGES[ReservationStatus.RESERVATION_MENU.name]
        user_status_code = "USER__RESERVATION_INDEX"
        return str(USER_DEFAULT_PROMPT), user_status_code

    if user_status_code == "USER__RESERVATION_INDEX":
        system_content = generate_judge_start_inquiry()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-4o", 0, system_content, user_message
        )
        if MenuItem.NEW_RESERVATION.code in bot_response:
            RESERVATION_RECEPTION_START = MESSAGES[
                ReservationStatus.NEW_RESERVATION_START.name
            ]
            user_status_code = ReservationStatus.NEW_RESERVATION_CHECKIN.name
            return str(RESERVATION_RECEPTION_START), user_status_code
        elif MenuItem.CONFIRM_RESERVATION.code in bot_response:
            extra_datas = {"title": "予約情報の確認"}
            message_template = (
                f"{MESSAGES[CheckReservationStatus.CHECK_RESERVATION_START.name]}"
            )
            CHECK_RESERVATION_START = message_template.format(**extra_datas)
            user_status_code = CheckReservationStatus.CHECK_RESERVATION_NAME.name
            return str(CHECK_RESERVATION_START), user_status_code
        elif MenuItem.MODIFY_RESERVATION.code in bot_response:
            extra_datas = {"title": "予約情報の変更"}
            message_template = (
                f"{MESSAGES[CheckReservationStatus.CHECK_RESERVATION_START.name]}"
            )
            CHECK_RESERVATION_START = message_template.format(**extra_datas)
            user_status_code = CheckReservationStatus.CHECK_RESERVATION_NAME.name
            return str(CHECK_RESERVATION_START), user_status_code
        elif MenuItem.CANCEL_RESERVATION.code in bot_response:
            extra_datas = {"title": "予約のキャンセル"}
            message_template = (
                f"{MESSAGES[CheckReservationStatus.CHECK_RESERVATION_START.name]}"
            )
            CHECK_RESERVATION_START = message_template.format(**extra_datas)
            user_status_code = CheckReservationStatus.CHECK_RESERVATION_NAME.name
            return str(CHECK_RESERVATION_START), user_status_code
        elif MenuItem.FAQ.code in bot_response:
            extra_datas = {"title": "よくあるお問い合わせ"}
            message_template = (
                f"{MESSAGES[InquiryReservationStatus.INQUIRY_RESERVATION_MENU.name]}"
            )
            INQUIRY_START = message_template.format(**extra_datas)
            user_status_code = InquiryReservationStatus.INQUIRY_RESERVATION_MENU.name
            return str(INQUIRY_START), user_status_code
        elif MenuItem.GOURMET.code in bot_response:
            extra_datas = {"title": "レストラン情報"}
            message_template = (
                f"{MESSAGES[GourmetReservationStatus.GOURMET_RESERVATION_MENU.name]}"
            )
            GOURMET_START = message_template.format(**extra_datas)
            user_status_code = GourmetReservationStatus.GOURMET_RESERVATION_MENU.name
            return str(GOURMET_START), user_status_code
        elif MenuItem.TOURISM.code in bot_response:
            extra_datas = {"title": "観光スポット情報"}
            message_template = (
                f"{MESSAGES[TourismReservationStatus.TOURISM_RESERVATION_MENU.name]}"
            )
            TOURISM_START = message_template.format(**extra_datas)
            user_status_code = TourismReservationStatus.TOURISM_RESERVATION_MENU.name
            return str(TOURISM_START), user_status_code
        elif MenuItem.GUEST.code in bot_response:
            extra_datas = {"title": "宿泊者情報"}
            message_template = (
                f"{MESSAGES[GuestReservationStatus.GUEST_RESERVATION_MENU.name]}"
            )
            GUEST_START = message_template.format(**extra_datas)
            user_status_code = GuestReservationStatus.GUEST_RESERVATION_MENU.name
            return str(GUEST_START), user_status_code
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
            message_type,
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
            message_type,
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

    if user_status_code == InquiryReservationStatus.INQUIRY_RESERVATION_MENU.name:
        return inquiry_handler.handle_inquiry_step(
            InquiryReservationStatus.INQUIRY_RESERVATION_MENU,
            user_message,
            InquiryReservationStatus.INQUIRY_RESERVATION_MENU,
            user_id,
            unique_code,
        )

    if user_status_code == GourmetReservationStatus.GOURMET_RESERVATION_MENU.name:
        return gourmet_handler.handle_gourmet_step(
            GourmetReservationStatus.GOURMET_RESERVATION_MENU,
            user_message,
            GourmetReservationStatus.GOURMET_RESERVATION_MENU,
            user_id,
            unique_code,
        )

    if user_status_code == TourismReservationStatus.TOURISM_RESERVATION_MENU.name:
        return tourism_handler.handle_tourism_step(
            TourismReservationStatus.TOURISM_RESERVATION_MENU,
            user_message,
            TourismReservationStatus.TOURISM_RESERVATION_MENU,
            user_id,
            unique_code,
        )

    if user_status_code == GuestReservationStatus.GUEST_RESERVATION_MENU.name:
        return guest_handler.handle_guest_step(
            GuestReservationStatus.GUEST_RESERVATION_MENU,
            user_message,
            GuestReservationStatus.GUEST_RESERVATION_MENU,
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


@handler.add(MessageEvent, message=(TextMessage, AudioMessage))
def handle_message(event: MessageEvent) -> None:
    global user_states
    global USER_STATUS_CODE
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    display_name = profile.display_name
    current_time = datetime.now()
    expiry_time = current_time + timedelta(minutes=60)
    expiry_timestamp = int(expiry_time.timestamp())
    history_expiry_time = current_time + timedelta(days=30)
    history_expiry_timestamp = int(history_expiry_time.timestamp())
    message_type = event.message.type

    response_datas = dynamodb.Table(table_name).get_item(
        Key={"unique_code": unique_code}
    )

    if (
        "Item" not in response_datas
        or response_datas["Item"]["unique_code"] != unique_code
    ):
        dynamodb.Table(table_name).put_item(
            Item={
                "unique_code": unique_code,
                "line_id": user_id,
                "ExpirationTime": expiry_timestamp,
                "display_name": display_name,
            }
        )

    if message_type == "audio":
        if api_transcribe_type == "CHATGPT_WHISPER":
            audio_file_path = process_audio(
                event, line_bot_api, user_id, storage_method="tmp"
            )
            user_message = process_audio_transcription(
                event,
                line_bot_api,
                user_id,
                api_transcribe_type,
                audio_file_path,
                api_key=OPENAI_API_KEY,
            )
        elif api_transcribe_type == "AWS_TRANSCRIBE":
            audio_file_path = process_audio(
                event, line_bot_api, user_id, storage_method="s3"
            )
            user_message = process_audio_transcription(
                event,
                line_bot_api,
                user_id,
                api_transcribe_type,
                audio_file_path,
                bucket_name=None,
                s3_key="_audio.m4a",
            )
        else:
            raise ValueError(f"Unsupported API Transcribe type: {api_transcribe_type}")
        text_message = TextSendMessage(text=user_message)
        line_bot_api.push_message(user_id, [text_message])
    else:
        user_message = event.message.text

    system_content = generate_judge_reset()
    judge_reset_result = get_chatgpt_response(
        OPENAI_API_KEY, "gpt-4o", 0, system_content, user_message
    )
    if judge_reset_result == "True":
        user_states[user_id] = str(ReservationStatus.RESERVATION_MENU.name)
        delete_session_user(unique_code, table_name, "dynamodb")
        chatgpt_response = textwrap.dedent(f"""
        {MESSAGES[ReservationStatus.RESERVATION_MENU.name]}
        """).strip()

        text_message = TextSendMessage(text=chatgpt_response)

        line_bot_api.reply_message(event.reply_token, [text_message])
        env_mode = os.getenv("ENV_MODE")
        if env_mode and env_mode != "TEST":
            s3_audio_url = LineSpeechSave(
                chatgpt_response, user_id, polly_client, s3_client, bucket_name
            )
            audio_message = AudioSendMessage(
                type="audio", original_content_url=s3_audio_url, duration=120000
            )
            line_bot_api.push_message(user_id, [audio_message])

    history = None
    if user_id in user_states:
        user_status_code = str(user_states[user_id])
    else:
        user_status_code = str(USER_STATUS_CODE)
    chatgpt_response, user_status_code = generate_response(
        user_message, history, user_status_code, user_id, display_name, message_type
    )
    user_states[user_id] = str(user_status_code)

    text_message = TextSendMessage(text=chatgpt_response)
    line_bot_api.reply_message(event.reply_token, [text_message])

    session_result = dynamodb.Table(history_table_name).query(
        KeyConditionExpression=Key("line_id").eq(user_id),
        FilterExpression=Key("session_id").eq(unique_code),
        ProjectionExpression="message_id",
        ScanIndexForward=False,
        Limit=1,
    )

    if session_result["Items"]:
        message_id = session_result["Items"][0]["message_id"] + 1
    else:
        message_id = 1

    current_timestamp = datetime.now().isoformat()
    dynamodb.Table(history_table_name).put_item(
        Item={
            "line_id": user_id,
            "create_time": current_timestamp,
            "session_id": unique_code,
            "message_id": message_id,
            "display_name": display_name,
            "stage": user_status_code,
            "user_message": user_message,
            "system_message": chatgpt_response,
            "ExpirationTime": int(history_expiry_timestamp),
        }
    )
    message_id += 1

    env_mode = os.getenv("ENV_MODE")
    if env_mode and env_mode != "TEST":
        s3_audio_url = LineSpeechSave(
            chatgpt_response, user_id, polly_client, s3_client, bucket_name
        )
        audio_message = AudioSendMessage(
            type="audio", original_content_url=s3_audio_url, duration=120000
        )
        line_bot_api.push_message(user_id, [audio_message])
