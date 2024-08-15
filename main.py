# Import necessary modules
import json
import os
import tempfile
from datetime import datetime, timedelta
from flask import Request, abort
from google.cloud import firestore, storage
from langchain.chat_models import ChatOpenAI
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from llama_index import (
    LLMPredictor,
    ServiceContext,
    PromptTemplate,
    StorageContext,
    load_index_from_storage,
)
from llama_index.indices.base import BaseIndex
from openai import OpenAI
from validation import (
    is_valid_date,
    is_single_digit_number,
    is_valid_smoking,
    is_valid_phone_number,
    is_valid_room_type,
    is_valid_room_type_smoke
)
from chatgpt_api import get_chatgpt_response
from generate import (
    generate_index,
    generate_start_date,
    generate_stay,
    generate_number,
    generate_smoking,
    generate_room,
    generate_room_smoking,
    generate_select,
)
from menu_items import MenuItem
from message import MESSAGES
import textwrap
import re

import requests

# Define constants
FILES_TO_DOWNLOAD = ["docstore.json", "index_store.json", "vector_store.json"]
BUCKET_NAME = "udemy-vector-store_1045"

# Initialize LINE Bot API and Firestore client
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
db = firestore.Client()

# Initialize Google Cloud Storage client and bucket
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(
    api_key=OPENAI_API_KEY,
)

# user status Initialize
USER_STATUS_CODE = "USER__RESERVATION_DEFAULT"
USE_HISTORY = False


# Function to get the last updated time of an object in the bucket
def get_object_updated_time(object_name: str) -> datetime:
    blob = bucket.blob(object_name)
    blob.reload()
    return blob.updated


# Function to download files from storage to a temporary director
def download_files_from_storage(temp_dir: str) -> None:
    for file in FILES_TO_DOWNLOAD:
        blob = bucket.blob(file)
        blob.download_to_filename(f"{temp_dir}/{file}")


# Function to set up storage and load index from downloaded files
def setup_storage_and_load_index() -> BaseIndex:
    with tempfile.TemporaryDirectory() as temp_dir:
        download_files_from_storage(temp_dir)
        service_context = ServiceContext.from_defaults(
            llm_predictor=LLMPredictor(
                llm=ChatOpenAI(
                    temperature=0,
                    model_name="gpt-3.5-turbo",
                    max_tokens=512
                )
            )
        )
        storage_context = StorageContext.from_defaults(persist_dir=temp_dir)
        return load_index_from_storage(
            storage_context=storage_context, service_context=service_context
        )


# Initialize index and updated time
index = setup_storage_and_load_index()
updated_time = get_object_updated_time(FILES_TO_DOWNLOAD[0])


# Function to reload the index if it has been updated
def reload_index_if_updated() -> None:
    global index, updated_time
    latest_updated_time = get_object_updated_time(FILES_TO_DOWNLOAD[0])
    if updated_time != latest_updated_time:
        index = setup_storage_and_load_index()
        updated_time = latest_updated_time


# Function to get previous messages from the Firestore database
def get_previous_messages(user_id: str) -> list:
    query = (
        db.collection("users")
        .document(user_id)
        .collection("messages")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(3)
    )
    return [
        {
            "chatgpt_response": doc.to_dict()["chatgpt_response"],
            "user_message": doc.to_dict()["user_message"],
        }
        for doc in query.stream()
    ]


# Function to format previous messages into a string
def format_history(previous_messages: list) -> str:
    return "".join(
        f"ユーザー: {d['user_message']}\nアシスタント: {d['chatgpt_response']}\n"
        for d in previous_messages[::-1]
    )


# Load messages from JSON file
# with open("messages.json", "r", encoding="utf-8") as f:
#     messages = json.load(f)

# Function to generate a response based on user message,
# history, and current state
res = {}
reserve = {}
reserves = {}
DEFAULT_MESSAGE_TO_USER = textwrap.dedent(f"""
    LINEメッセージありがとうございます。こちら〇〇ホテルAI予約応答サービスです。\n
    下記ご用件を承っております。\n\n----\n
    1.{MenuItem.NEW_RESERVATION.value}\n
    2.{MenuItem.CONFIRM_RESERVATION.value}\n
    3.{MenuItem.MODIFY_RESERVATION.value}\n
    4.{MenuItem.CANCEL_RESERVATION.value}\n
    5.{MenuItem.FAQ.value}\n----
""").strip()


def generate_response(
    user_message: str, history: str = None, user_status_code: str = None, user_id: str = None 
) -> str:
    if user_status_code == "USER__RESERVATION_DEFAULT":
        USER_DEFAULT_PROMPT = DEFAULT_MESSAGE_TO_USER
        user_status_code = "USER__RESERVATION_INDEX"
        return str(USER_DEFAULT_PROMPT), user_status_code

    if user_status_code == "USER__RESERVATION_INDEX":
        system_content = generate_index()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
        )
        if MenuItem.NEW_RESERVATION.value in bot_response:
            RESERVATION_RECEPTION_START = MESSAGES["reservation_reception_start"]
            user_status_code = "USER__RESERVATION_NEW"
            return str(RESERVATION_RECEPTION_START), user_status_code
        elif MenuItem.CONFIRM_RESERVATION.value in bot_response:
            RESERVATION_RECEPTION_CHECK = MESSAGES["reservation_reception_check"]
            user_status_code = "USER__RESERVATION_CHECK"
            return str(RESERVATION_RECEPTION_CHECK), user_status_code
        elif MenuItem.MODIFY_RESERVATION.value in bot_response:
            RESERVATION_RECEPTION_UPDATA = MESSAGES["reservation_reception_updata"]
            user_status_code = "USER__RESERVATION_UPDATA_RESULT"
            return str(RESERVATION_RECEPTION_UPDATA), user_status_code
        elif MenuItem.CANCEL_RESERVATION.value in bot_response:
            USER__RESERVATION_CANCEL = MESSAGES["reservation_reception_cancel"]
            user_status_code = "USER__RESERVATION_CANCEL"
            return str(USER__RESERVATION_CANCEL), user_status_code
        elif MenuItem.FAQ.value in bot_response:
            FAQ = "よくある質問に関してお答えいたします。"
            user_status_code = "FAQ"
            return str(FAQ), user_status_code
        else:
            RESERVATION_RECEPTION_ERROR = MESSAGES["reservation_reception_error"]
            return str(RESERVATION_RECEPTION_ERROR), user_status_code

    if user_status_code == "USER__RESERVATION_NEW":
        system_content = generate_start_date()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY,
            "ft:gpt-3.5-turbo-1106:personal::9hWLayjR",
            0,
            system_content,
            user_message,
        )
        reserves['check_in'] = datetime.strptime(bot_response, '%Y-%m-%d').strftime('%Y-%m-%d')
        if is_valid_date(reserve['check_in']):
            RESERVATION_RECEPTION_STAY = (
                f"{reserve['check_in']} {MESSAGES['reservation_reception_stay']}"
            )
            user_status_code = "USER__RESERVATION_NEW_START"
            return str(RESERVATION_RECEPTION_STAY), user_status_code
        else:
            RESERVATION_RECEPTION_STAY = MESSAGES["reservation_reception_stay_error"]
            return str(RESERVATION_RECEPTION_STAY), user_status_code
    if user_status_code == "USER__RESERVATION_NEW_START":
        system_content = generate_stay()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
        )

        reserves['check_out'] = (datetime.strptime(reserve['check_in'], '%Y-%m-%d') + timedelta(days=int(reserve['stay']))).strftime('%Y-%m-%d')
        if is_single_digit_number(bot_response):
            res["stay"] = bot_response
            RESERVATION_RECEPTION_NUMBER = (
                textwrap.dedent(f"宿泊数は {res['stay']}で、チェックアウト日は {reserves['check_out']}になります。 {MESSAGES['reservation_reception_number']}").strip()
            )
            user_status_code = "USER__RESERVATION_NEW_STAY"
            return str(RESERVATION_RECEPTION_NUMBER), user_status_code
        else:
            RESERVATION_RECEPTION_NUMBER = MESSAGES[
                "reservation_reception_number_error"
            ]
            return str(RESERVATION_RECEPTION_NUMBER), user_status_code

    if user_status_code == "USER__RESERVATION_NEW_STAY":
        system_content = generate_number()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
        )
        if is_single_digit_number(bot_response):
            reserves["count_of_person"] = bot_response
            RESERVATION_RECEPTION_SMOKING = textwrap.dedent(f"""
                利用者人数は {reserves["count_of_person"]} {MESSAGES['reservation_reception_smoking']}
            """).strip()
            user_status_code = "USER__RESERVATION_NEW_NUMBER"
            return str(RESERVATION_RECEPTION_SMOKING), user_status_code
        else:
            RESERVATION_RECEPTION_SMOKING = MESSAGES["reservation_reception_smoking_error"]
            return str(RESERVATION_RECEPTION_SMOKING), user_status_code

    if user_status_code == "USER__RESERVATION_NEW_NUMBER":
        system_content = generate_smoking()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
        )
        res["smoking"] = bot_response
        if res["smoking"] == "禁煙": 
            if is_valid_smoking(res["smoking"]):
                RESERVATION_RECEPTION_ROOM = textwrap.dedent(f"""
                    禁煙か喫煙かは {res['smoking']}ですね。 {MESSAGES['reservation_reception_room']}
                """).strip()
            else:
                RESERVATION_RECEPTION_ROOM = MESSAGES["reservation_reception_room_error"]
                return str(RESERVATION_RECEPTION_ROOM), user_status_code
        elif res["smoking"] == "喫煙":
            if is_valid_smoking(bot_response):
                RESERVATION_RECEPTION_ROOM = textwrap.dedent(f"""
                    禁煙か喫煙かは {res['smoking']}ですね。 {MESSAGES['reservation_reception_room_smoke']}
                """).strip()
            else:
                RESERVATION_RECEPTION_ROOM = MESSAGES["reservation_reception_room_error"]
                return str(RESERVATION_RECEPTION_ROOM), user_status_code

        else:
            RESERVATION_RECEPTION_ROOM = MESSAGES["reservation_reception_room_error"]
            return str(RESERVATION_RECEPTION_ROOM), user_status_code

        user_status_code = "USER__RESERVATION_NEW_SMOKING"
        return str(RESERVATION_RECEPTION_ROOM), user_status_code

    if user_status_code == "USER__RESERVATION_NEW_SMOKING":
        room_judge = False
        if res["smoking"] == "禁煙":
            system_content = generate_room()
            bot_response = get_chatgpt_response(
                OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
            )
            if is_valid_room_type(bot_response):
                room_judge = True
        elif res["smoking"] == "喫煙":
            system_content = generate_room_smoking()
            bot_response = get_chatgpt_response(
                OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
            )
            if is_valid_room_type_smoke(bot_response):
                room_judge = True
        if room_judge:
            reserves["room"] = bot_response
            RESERVATION_RECEPTION_NAME = textwrap.dedent(f"""
                部屋タイプは {reserve['room']} {MESSAGES['reservation_reception_name']}
            """).strip()
            user_status_code = "USER__RESERVATION_NEW_ROOM"
            return str(RESERVATION_RECEPTION_NAME), user_status_code
        else:
            RESERVATION_RECEPTION_NAME = MESSAGES["reservation_reception_name_error"]
            return str(RESERVATION_RECEPTION_NAME), user_status_code


    if user_status_code == "USER__RESERVATION_NEW_ROOM":
        if user_message:
            reserve["name"] = user_message
            RESERVATION_RECEPTION_TELL = textwrap.dedent(f"""
                代表者氏名は {reserve['name']} 様ですね。
                {MESSAGES['reservation_reception_tell']}
            """).strip()
            user_status_code = "USER__RESERVATION_NEW_NAME"
            return str(RESERVATION_RECEPTION_TELL), user_status_code
        else:
            RESERVATION_RECEPTION_TELL = MESSAGES["reservation_reception_tell_error"]
            return str(RESERVATION_RECEPTION_TELL), user_status_code

    if user_status_code == "USER__RESERVATION_NEW_NAME":
        start_date = datetime.strptime(reserve['start'], '%Y-%m-%d')
        reserve['check_in'] = start_date.strftime('%Y-%m-%d')
        reserve['check_out'] = (start_date + timedelta(days=int(reserve['stay']))).strftime('%Y-%m-%d')
        inside_parentheses = re.search(r'\((.*?)\)', reserve['room'])
        reserve['room_type'] = inside_parentheses.group(1)
        reserve['reservation_date'] = datetime.now().strftime('%Y-%m-%d')
        reserve['reservation_id'] = int(100)
        reserve['line_id'] = user_id
        reserve['status'] = "RESERVE"
        reserve['count_of_person'] = {reserve['number']}

        if is_valid_phone_number(user_message):
            reserve["tell"] = user_message
            RESERVATION_RECEPTION_CONFIRM = textwrap.dedent(f"""
                当日連絡可能な電話番号をありがとうございます。
                下記が宿泊予約の内容になりますのでご確認ください。
                ----
                予約番号：{reserve['reservation_id']}
                予約日：{reserve['reservation_date']}
                ラインID：{reserve['line_id']}
                チェックイン：{reserve['check_in']} 
                チェックアウト：{reserve['check_out']}
                ステータス：{reserve['status']}
                利用者人数：{reserve['number']}
                部屋タイプ：{reserve['room_type']}
                代表者氏名：{reserve['name']}
                電話番号：{reserve['tell']}
                ----
                この条件でよろしければ、空室検索をいたします。
                「検索」とメッセージで送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_NEW_TELL"
            print(reserve)
            return str(RESERVATION_RECEPTION_CONFIRM), user_status_code
        else:
            RESERVATION_RECEPTION_CONFIRM = MESSAGES["reservation_reception_confirm_error"]
            return str(RESERVATION_RECEPTION_CONFIRM), user_status_code

    if user_status_code == "USER__RESERVATION_NEW_TELL":
        if user_message == "検索":
            RESERVATION_RECEPTION_SEARCH = textwrap.dedent(f"""
                下記条件で空室検索をいたしました。\n\n
                ----\n
                宿泊開始日：{reserve['start']}\n
                宿泊数：{reserve['stay']}\n
                利用者人数：{reserve['number']}\n
                部屋タイプ：{reserve['room']}\n
                代表者氏名：{reserve['name']}\n
                電話番号：{reserve['tell']}\n
                ----\n\n
                空室APIで検索結果を表示させます。\n
                ヒットすればTrue、ヒットしなければFalseを返します。\n\n
                予約する場合は「予約」とメッセージで送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_NEW_SEARCH"
            return str(RESERVATION_RECEPTION_SEARCH), user_status_code
        else:
            user_status_code = "USER__RESERVATION_DEFAULT"
            RESERVATION_RECEPTION_SEARCH = MESSAGES[
                "reservation_reception_search_error"
            ]
            return str(RESERVATION_RECEPTION_SEARCH), user_status_code

    if user_status_code == "USER__RESERVATION_NEW_SEARCH":
        if user_message == "予約":
            RESERVATION_RECEPTION_COMPLETE = textwrap.dedent(f"""
                下記条件で予約をいたしました。\n\n
                ----\n
                宿泊開始日：{reserve['start']}\n
                宿泊数：{reserve['stay']}\n
                利用者人数：{reserve['number']}\n
                部屋タイプ：{reserve['room']}\n
                代表者氏名：{reserve['name']}\n
                電話番号：{reserve['tell']}\n
                ----\n\n
                予約APIの実行結果を表示させます。ヒットすればTrue、ヒットしなければFalseを返します。\n\n
                予約ありがとうございます。\n
                {reserve['start']}に{reserve['name']}様{reserve['number']}名様をお待ちしております。
            """).strip()
            user_status_code = "USER__RESERVATION_DEFAULT"
            return str(RESERVATION_RECEPTION_COMPLETE), user_status_code
        else:
            user_status_code = "USER__RESERVATION_DEFAULT"
            RESERVATION_RECEPTION_COMPLETE = MESSAGES[
                "reservation_reception_complete_error"
            ]
            return str(RESERVATION_RECEPTION_COMPLETE), user_status_code

    if user_status_code == "USER__RESERVATION_CHECK":
        if user_message:  # 有効な予約番号かどうかはAPIでチェックする(bool)
            RESERVATION_RECEPTION_CHECK_RESULT = MESSAGES[
                "reservation_reception_check_result"
            ]
            user_status_code = "USER__RESERVATION_UPDATA"
            return str(RESERVATION_RECEPTION_CHECK_RESULT), user_status_code
        else:
            RESERVATION_RECEPTION_CHECK_RESULT = MESSAGES["reservation_number_error"]
            return str(RESERVATION_RECEPTION_CHECK_RESULT), user_status_code

    if (
        user_status_code == "USER__RESERVATION_UPDATA"
    ):  # 予約確認からしかここには来ない。
        if user_message == "予約変更":
            RESERVATION_RECEPTION_UPDATA = textwrap.dedent("""
                予約変更ですね。\n
                予約時に控えていただきました予約番号のみを入力してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_RESULT"
            return str(RESERVATION_RECEPTION_UPDATA), user_status_code
        else:
            user_status_code = "USER__RESERVATION_DEFAULT"
            RESERVATION_RECEPTION_UPDATA = textwrap.dedent("お問い合わせ一覧にもどります。").strip()
            return str(RESERVATION_RECEPTION_UPDATA), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_RESULT":
        if user_message:  # 有効な予約番号かどうかはAPIでチェックする(bool)
            RESERVATION_RECEPTION_UPDATA_RESULT = textwrap.dedent("""
                お客様の予約番号は下記内容になります。\n
                宿泊開始日：予約番号の検索結果\n
                宿泊数：予約番号の検索結果\n
                利用者人数：予約番号の検索結果\n
                部屋タイプ：予約番号の検索結果\n
                代表者氏名：予約番号の検索結果\n
                電話番号：予約番号の検索結果\n\n
                変更したい項目を選んでメッセージに送付してください。\n
                ここで取得した予約データを配列に保管します。コードは後程に記述。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_SELECT"
            # reserve_updata = get_reserve_data(予約番号)
            return str(RESERVATION_RECEPTION_UPDATA_RESULT), user_status_code
        else:
            user_status_code = "USER__RESERVATION_DEFAULT"
            RESERVATION_RECEPTION_UPDATA_RESULT = MESSAGES["reservation_number_error"]
            return str(RESERVATION_RECEPTION_UPDATA_RESULT), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_SELECT":
        system_content = generate_select()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
        )
        if "宿泊開始日" in bot_response:
            USER__RESERVATION_UPDATA_START = textwrap.dedent("""
                宿泊開始日を変更します。\n
                変更したい宿泊日をご記入してメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_START"
            return str(USER__RESERVATION_UPDATA_START), user_status_code
        elif "宿泊数" in bot_response:
            USER__RESERVATION_UPDATA_STAY = textwrap.dedent("""
                宿泊数を変更します。
                変更したい宿泊数をご記入してメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_STAY"
            return str(USER__RESERVATION_UPDATA_STAY), user_status_code
        elif "利用者人数" in bot_response:
            USER__RESERVATION_UPDATA_NUMBER = textwrap.dedent("""
                利用者人数を変更します。
                変更したい利用者人数をご記入してメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_NUMBER"
            return str(USER__RESERVATION_UPDATA_NUMBER), user_status_code
        elif "部屋タイプ" in bot_response:
            USER__RESERVATION_UPDATA_ROOM = textwrap.dedent("""
                部屋タイプを変更します。
                変更したい部屋タイプをご記入してメッセージ送信してください。
                ---
                禁煙シングル(SK)
                禁煙シングルA(SAK)
                禁煙スモールシングルA(XSK)
                禁煙エコノミーダブル(WAK)
                禁煙キングダブル(QWK)
                禁煙エコノミーツイン(ETK)
                禁煙ハートフルツイン(HTK)
                ハートフルシングル(HSK)
                喫煙シングル(S)
                喫煙シングルA(SA)
                喫煙スモールシングルA(XS)
                喫煙エコノミーダブル(WA)
                喫煙キングダブル(QW)
                喫煙エコノミーツイン(ET)
                ---
                以上になります。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_ROOM"
            return str(USER__RESERVATION_UPDATA_ROOM), user_status_code
        elif "代表者氏名" in bot_response:
            USER__RESERVATION_UPDATA_NAME = textwrap.dedent("""
                代表者氏名を変更します。
                変更したい代表者氏名をご記入してメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_NAME"
            return str(USER__RESERVATION_UPDATA_NAME), user_status_code
        elif "電話番号" in bot_response:
            USER__RESERVATION_UPDATA_TELL = textwrap.dedent("""
                電話番号を変更します。\n
                変更したい電話番号をご記入してメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_TELL"
            return str(USER__RESERVATION_UPDATA_TELL), user_status_code
        else:
            user_status_code = "USER__RESERVATION_DEFAULT"
            USER__RESERVATION_DEFAULT = (
                textwrap.dedent("""
                    予約変更しない場合は、最初からお問い合わせしなおしてください。
                """).strip()
            )
            return str(USER__RESERVATION_DEFAULT), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_START":
        system_content = generate_start_date()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
        )
        if is_valid_date(bot_response):
            reserve["start"] = bot_response
            USER__RESERVATION_UPDATA_CONFIRM = textwrap.dedent(f"""
                {reserve['start']}ですね。
                確認画面に行く場合は「確認」とメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_CONFIRM"
            return str(USER__RESERVATION_UPDATA_CONFIRM), user_status_code
        else:
            USER__RESERVATION_UPDATA_START = MESSAGES["reservation_reception_stay_error"]
            return str(USER__RESERVATION_UPDATA_START), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_STAY":
        system_content = generate_stay()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
        )
        if is_single_digit_number(bot_response):
            reserve["stay"] = bot_response
            USER__RESERVATION_UPDATA_CONFIRM = textwrap.dedent(f"""
                宿泊数は {reserve['stay']} ですね。
                確認画面に行く場合は「確認」とメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_CONFIRM"
            return str(USER__RESERVATION_UPDATA_CONFIRM), user_status_code
        else:
            USER__RESERVATION_UPDATA_STAY = MESSAGES[
                "reservation_reception_number_error"
            ]
            return str(USER__RESERVATION_UPDATA_STAY), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_NUMBER":
        system_content = generate_number()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
        )
        if is_single_digit_number(bot_response):
            reserve["number"] = bot_response
            USER__RESERVATION_UPDATA_CONFIRM = textwrap.dedent(f"""
                利用者人数は {reserve['number']} ですね。
                確認画面に行く場合は「確認」とメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_CONFIRM"
            return str(USER__RESERVATION_UPDATA_CONFIRM), user_status_code
        else:
            USER__RESERVATION_UPDATA_NUMBER = MESSAGES["reservation_reception_room_error"]
            return str(USER__RESERVATION_UPDATA_NUMBER), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_ROOM":
        system_content = generate_room()
        bot_response = get_chatgpt_response(
            OPENAI_API_KEY, "gpt-3.5-turbo", 0, system_content, user_message
        )
        if is_valid_room_type(bot_response):
            reserve["room"] = bot_response
            USER__RESERVATION_UPDATA_CONFIRM = textwrap.dedent(f"""
                部屋タイプは {reserve['room']} ですね。
                確認画面に行く場合は「確認」とメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_CONFIRM"
            return str(USER__RESERVATION_UPDATA_CONFIRM), user_status_code
        else:
            USER__RESERVATION_UPDATA_ROOM = MESSAGES["reservation_reception_name_error"]
            return str(USER__RESERVATION_UPDATA_ROOM), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_NAME":
        if user_message:
            reserve["name"] = user_message
            USER__RESERVATION_UPDATA_CONFIRM = textwrap.dedent(f"""
                代表者氏名は {reserve['name']} ですね。
                確認画面に行く場合は「確認」とメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_CONFIRM"
            return str(USER__RESERVATION_UPDATA_CONFIRM), user_status_code
        else:
            USER__RESERVATION_UPDATA_NAME = MESSAGES["reservation_reception_tell_error"]
            return str(USER__RESERVATION_UPDATA_NAME), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_TELL":
        if user_message:
            reserve["tell"] = user_message
            USER__RESERVATION_UPDATA_CONFIRM = textwrap.dedent(f"""
                連絡先電話番号は {reserve['tell']} ですね。
                確認画面に行く場合は「確認」とメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_CONFIRM"
            return str(USER__RESERVATION_UPDATA_CONFIRM), user_status_code
        else:
            USER__RESERVATION_UPDATA_TELL = MESSAGES[
                "reservation_reception_confirm_error"
            ]
            return str(USER__RESERVATION_UPDATA_TELL), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_CONFIRM":
        if user_message == "確認":
            USER__RESERVATION_UPDATA_CHECK = textwrap.dedent("""
                予約変更は下記内容になります。\n
                宿泊開始日：予約番号の検索結果\n
                宿泊数：予約番号の検索結果\n
                利用者人数：予約番号の検索結果\n
                部屋タイプ：予約番号の検索結果\n
                代表者氏名：予約番号の検索結果\n
                電話番号：予約番号の検索結果\n\n
                内容に問題なければ「変更」とメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_UPDATA_CHECK"
            return str(USER__RESERVATION_UPDATA_CHECK), user_status_code
        else:
            user_status_code = "USER__RESERVATION_DEFAULT"
            USER__RESERVATION_DEFAULT = ("""予約変更しない場合は、最初からお問い合わせしなおしてください。""")
            return str(USER__RESERVATION_DEFAULT), user_status_code

    if user_status_code == "USER__RESERVATION_UPDATA_CHECK":
        if user_message == "変更":
            USER__RESERVATION_UPDATA_CHECK = textwrap.dedent("""
                下記内容に予約内容を変更いたしました。
                宿泊開始日：予約番号の検索結果
                宿泊数：予約番号の検索結果
                利用者人数：予約番号の検索結果
                部屋タイプ：予約番号の検索結果
                代表者氏名：予約番号の検索結果
                電話番号：予約番号の検索結果
            """).strip()
            user_status_code = "USER__RESERVATION_DEFAULT"
            return str(USER__RESERVATION_UPDATA_CHECK), user_status_code
        else:
            user_status_code = "USER__RESERVATION_DEFAULT"
            USER__RESERVATION_DEFAULT = ("予約変更しない場合は、最初からお問い合わせしなおしてください。")
            return str(USER__RESERVATION_DEFAULT), user_status_code

    if user_status_code == "USER__RESERVATION_CANCEL":
        if user_message:  # 有効な予約番号かどうかはAPIでチェックする(bool)
            USER__RESERVATION_CANCEL_RESULT = textwrap.dedent("""
                お客様の予約は下記内容になります。
                宿泊開始日：予約番号の検索結果
                宿泊数：予約番号の検索結果
                利用者人数：予約番号の検索結果
                部屋タイプ：予約番号の検索結果
                代表者氏名：予約番号の検索結果
                電話番号：予約番号の検索結果\n
                キャンセルを実行したい場合は「キャンセル」とのみメッセージ送信してください。
            """).strip()
            user_status_code = "USER__RESERVATION_CANCEL_RESULT"
            # reserve_updata = get_reserve_data(予約番号)
            return str(USER__RESERVATION_CANCEL_RESULT), user_status_code
        else:
            user_status_code = "USER__RESERVATION_DEFAULT"
            USER__RESERVATION_CANCEL = MESSAGES["reservation_number_error"]
            return str(USER__RESERVATION_CANCEL), user_status_code

    if user_status_code == "USER__RESERVATION_CANCEL_RESULT":
        if user_message == "キャンセル":
            USER__RESERVATION_CANCELED = textwrap.dedent(""""
                お客様の予約をキャンセルしました。
                ※予約APIの結果によってはキャンセル料金が発生？
            """).strip()
            user_status_code = "USER__RESERVATION_DEFAULT"
            return str(USER__RESERVATION_CANCELED), user_status_code
        else:
            user_status_code = "USER__RESERVATION_DEFAULT"
            USER__RESERVATION_CANCEL = (
                textwrap.dedent("""
                    キャンセルしない場合は、最初からお問い合わせしなおしてください。
                """).strip()
            )
            return str(USER__RESERVATION_CANCEL), user_status_code

    if user_status_code == "FAQ":
        COMMON_PROMPT = textwrap.dedent("""
            あなたは親切なアシスタントです。
            {history_section}
            以下に文献の情報を提供します。
            ---------------------
            {{context_str}}
            ---------------------
            与えられた情報を元にユーザーへのアドバイスを200文字以内で出力してください。
            文献の情報から回答できない入力の場合は、そのように出力してください。
            入力：{{query_str}}
            出力：
        """).strip()
        if USE_HISTORY:
            history_section = textwrap.dedent(f"""
                これまでのユーザーとアシスタントの会話の履歴は以下のようになっています。
                ---------------------
                {history}
                ---------------------
                過去にした質問を確認してください。
                情報を重複して尋ねないように注意してください。
                また、追加のリクエストや質問がないかをお尋ねし、お客様に安心感を提供してください。
            """).strip()
        else:
            history_section = ""
        PROMPT = COMMON_PROMPT.format(history_section=history_section)
        query_engine = index.as_query_engine(text_qa_template=PromptTemplate(PROMPT))
        return str(query_engine.query(user_message)), user_status_code


# Function to reply to the user using LINE Bot API
def reply_to_user(reply_token: str, chatgpt_response: str) -> None:
    line_bot_api.reply_message(reply_token, TextSendMessage(text=chatgpt_response))


# Function to save messages to the Firestore database
def save_message_to_db(user_id: str, user_message: str, chatgpt_response: str) -> None:
    doc_ref = db.collection("users").document(user_id).collection("messages").document()
    doc_ref.set(
        {
            "user_message": user_message,
            "chatgpt_response": chatgpt_response,
            "timestamp": datetime.now(),
        }
    )


def is_first_time_user(user_id):
    previous_messages = get_previous_messages(user_id)
    return len(previous_messages) == 0


###################
# Main function to handle incoming requests
def main(request: Request) -> str:
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


# Function to handle incoming messages from LINE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent) -> None:
    global USER_STATUS_CODE
    reload_index_if_updated()
    user_id = event.source.user_id
    user_message = event.message.text
    print(user_id)
    if USE_HISTORY:
        previous_messages = get_previous_messages(user_id)
        history = format_history(previous_messages)
    else:
        history = None
    # chatgpt_response = generate_response(user_message, history)
    chatgpt_response, user_status_code = generate_response(
        user_message, history, USER_STATUS_CODE, user_id
    )
    USER_STATUS_CODE = user_status_code
    reply_to_user(event.reply_token, chatgpt_response)
    if USE_HISTORY:
        save_message_to_db(user_id, user_message, chatgpt_response)
