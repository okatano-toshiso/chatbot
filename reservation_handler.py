import os
import re

import textwrap
from datetime import datetime, timedelta
from reservation_status import ReservationStatus
from chatgpt_api import get_chatgpt_response
from prompts.judge_intent import generate_judge_intent
from prompts.checkin_date import generate_checkin_date
from prompts.count_of_stay import generate_count_of_stay
from prompts.count_of_person import generate_count_of_person
from prompts.judge_smoker import generate_judge_smoker
from prompts.room_type_smoker import generate_room_type_smoker
from prompts.room_type_no_smoker import generate_room_type_no_smoker
from prompts.confirm_reserve import generate_confirm_reserve
from prompts.execute_reserve import generate_execute_reserve
from prompts.judge_adult import generate_judge_adult
from prompts.name_kana import generate_name_kana
from prompts.name_yomi import generate_name_yomi
from prompts.name_extractor import generate_name_extractor

from validation import (
    is_valid_date,
    is_single_digit_number,
    is_valid_smoker,
    is_valid_phone_number,
    is_valid_room_type_smoker,
    is_valid_room_type_no_smoker,
    is_valid_japaneses_character,
    is_valid_japanese_katakana,
    is_valid_reservation_menu
)
import requests
import boto3
import json

# from utils.clean_phone_number import clean_phone_number
from utils.digit_extractor import extract_number

reserves = {}
users = {}

dynamodb = boto3.resource('dynamodb')
table_name = "LineChatBot_TBL"
table = dynamodb.Table(table_name)

class ReservationHandler:

    def check_reservation_status(self, unique_code):

        response = table.get_item(Key={'unique_code': unique_code})
        current_data = response.get('Item', {})
        required_fields = ["check_in", "check_out", "count_of_person", "name", "phone_number", "room_type"]
        missing_fields = [field for field in required_fields if not current_data.get(field)]

        if not missing_fields:
            return 'complete', "予約可能になりました。内容確認に進みますか。『はい』とお答えいただければ内容を確認します。もし修正したい場合は、『修正したい』とお伝えいただき、変更したい項目を教えてください。内容確認に進まない場合は『いいえ』とお答えください。", []
        missing_messages = {
            "check_in": "チェックイン日",
            "check_out": "チェックアウト日",
            "count_of_person": "利用者人数",
            "name": "代表者氏名",
            "phone_number": "当日連絡可能の電話番号",
            "room_type": "部屋タイプ"
        }
        missing_list = [missing_messages[field] for field in missing_fields]
        return 'incomplete', f"{', '.join(missing_list)}を教えてください。", missing_fields

    def get_new_reserve_id(self):
        token_data = {"token": self.access_token}
        getReserveIdUrl = os.environ["API_SET_RESERVE_ID"]
        response = requests.get(getReserveIdUrl, json=token_data)

        if response.status_code == 200:
            response_body = json.loads(response.json().get("body"))
            latest_reserve_id = response_body.get("latest_reserve_id")

            if latest_reserve_id is not None:
                return int(latest_reserve_id) + 1
            else:
                return int(9100001)
        else:
            print("Cannot get the latest reserve ID")
            return None

    def set_line_users_data(self, user_id, datas, current_datetime):
        line_users = {
            "line_id": user_id,
            # 'token': self.access_token,
            "name": datas["name"],
            "name_kana": datas["name_kana"],
            "display_name": datas["display_name"],
            "adult": datas["adult"],
            "phone_number": datas["phone_number"],
            "created_at": current_datetime,
            "updated_at": current_datetime,
        }
        return line_users

    def set_line_reserves_data(
        self, user_id, datas, new_reserve_id, current_date, current_datetime
    ):
        line_reserves = {
            # 'token': self.access_token,
            "reservation_date": current_date,
            "reservation_id": new_reserve_id,
            "line_id": user_id,
            "name": datas["name"],
            "phone_number": datas["phone_number"],
            "check_in": datas["check_in"],
            "check_out": datas["check_out"],
            "room_type": datas["room_type"],
            "count_of_person": datas["count_of_person"],
            "status": "RESERVE",
            "created_at": current_datetime,
            "updated_at": current_datetime,
        }
        return line_reserves

    def send_reservation_data(self, reserve_datas, user_datas):
        data = {"line_reserves": [reserve_datas], "line_users": [user_datas]}
        url = os.environ["API_SAVE_RESERVE_DATA"]
        access_token = os.environ.get("ACCESS_TOKEN")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                reservation_id = reserve_datas.get("reservation_id")
                return self.messages[
                    ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name
                ], reservation_id
            else:
                print(
                    f"Unexpected status code: {response.status_code}, Response: {response.text}"
                )
                return self.messages[
                    "SEND_RESERVATION_DATA_ERROR"
                ], ReservationStatus.RESERVATION_MENU.name

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return f"Failed to submit reservation: {http_err}", "ERROR_STATUS"
        except Exception as err:
            print(f"An error occurred: {err}")
            return f"An unexpected error has occurred.: {err}", "ERROR_STATUS"

    def __init__(self, table_name, api_key, messages):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.messages = messages
        self.reserves = {}
        self.temp_data = {}
        self.handlers = {
            ReservationStatus.NEW_RESERVATION_JUDGE_INTENT: self._handle_judge_intent,
            ReservationStatus.NEW_RESERVATION_CHECKIN: self._handle_checkin,
            ReservationStatus.NEW_RESERVATION_CHECKOUT: self._handle_checkout,
            ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON: self._handle_count_of_person,
            ReservationStatus.NEW_RESERVATION_SMOKER: self._handle_smoker,
            ReservationStatus.NEW_RESERVATION_ROOM_TYPE_SMOKER: self._handle_room_type_smoker,
            ReservationStatus.NEW_RESERVATION_ROOM_TYPE_NO_SMOKER: self._handle_room_type_no_smoker,
            ReservationStatus.NEW_RESERVATION_NAME: self._handle_name,
            ReservationStatus.NEW_RESERVATION_ADULT: self._handle_adult,
            ReservationStatus.NEW_RESERVATION_PHONE_NUMBER: self._handle_phone_number,
            ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM: self._handle_reserve_confirm,
            ReservationStatus.NEW_RESERVATION_RESERVE_EXECUTE: self._handle_reserve_execute,
        }

    def handle_reservation_step(
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
                message_type=message_type
            )
        else:
            raise ValueError(f"Unsupported reservation status: {status}")

    def _handle_judge_intent(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_judge_intent()
        reservation_menu = self.get_chatgpt_response(system_content, user_message)
        if is_valid_reservation_menu(reservation_menu):
            if reservation_menu == "checkin_checkout":
                return self.messages[ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_CHECKIN"], ReservationStatus.NEW_RESERVATION_CHECKIN.name
            elif reservation_menu == "count_of_person":
                return self.messages[ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_COUNT_OF_PERSON"], ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name
            elif reservation_menu == "room_type":
                return self.messages[ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_ROOM_TYPE"], ReservationStatus.NEW_RESERVATION_SMOKER.name
            elif reservation_menu == "name":
                return self.messages[ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_NAME"], ReservationStatus.NEW_RESERVATION_NAME.name
            elif reservation_menu == "phone_number":
                return self.messages[ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_PHONE_NUMBER"], ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name
            else:
                return self.messages[ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_ERROR"], ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name
        else:
            return self.messages[ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_ERROR"], ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name


    def _handle_checkin(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_checkin_date()
        check_in_date = self.get_chatgpt_response(system_content, user_message)

        if is_valid_date(check_in_date):
            formatted_date = datetime.strptime(check_in_date, "%Y-%m-%d").strftime(
                "%Y-%m-%d"
            )
            ymd_format = datetime.strptime(check_in_date, "%Y-%m-%d").strftime(
                "%Y年%m月%d日"
            )
            self.reserves[ReservationStatus.NEW_RESERVATION_CHECKIN.key] = (
                formatted_date
            )
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": ReservationStatus.NEW_RESERVATION_CHECKIN.key
                },
                ExpressionAttributeValues={":cd": formatted_date},
            )
            message = f"{ymd_format} {self.messages[ReservationStatus.NEW_RESERVATION_CHECKIN.name]}"
            return message, next_status.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_CHECKIN.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_CHECKIN.name

    def _handle_checkout(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_count_of_stay()
        stay_length = self.get_chatgpt_response(system_content, user_message)
        table_datas = self.table.get_item(Key={"unique_code": unique_code})
        checkin_date = table_datas["Item"]["check_in"]

        if checkin_date and is_single_digit_number(stay_length):
            checkout_date = self._calculate_checkout_date(checkin_date, stay_length)
            formatted_date = datetime.strptime(checkout_date, "%Y-%m-%d").strftime(
                "%Y-%m-%d"
            )
            ymd_format = datetime.strptime(checkout_date, "%Y-%m-%d").strftime(
                "%Y年%m月%d日"
            )
            self.reserves[ReservationStatus.NEW_RESERVATION_CHECKOUT.key] = (
                formatted_date
            )
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": ReservationStatus.NEW_RESERVATION_CHECKOUT.key
                },
                ExpressionAttributeValues={":cd": formatted_date},
            )
            reservation_status, reservation_message, missing_fields = self.check_reservation_status(unique_code)
            if reservation_status == 'complete':
                return reservation_message, ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
            message = textwrap.dedent(
                f"宿泊数は {stay_length}泊、チェックアウト日は {ymd_format}になります。 {self.messages[ReservationStatus.NEW_RESERVATION_CHECKOUT.name]}あとは{reservation_message}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_CHECKOUT.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_CHECKOUT.name

    def _handle_count_of_person(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_count_of_person()
        count_of_person = self.get_chatgpt_response(system_content, user_message)
        if is_single_digit_number(count_of_person):
            count_of_person = int(count_of_person)
            if count_of_person > 2:
                return self.messages[
                    ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name + "_OVER"
                ], ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name

            self.reserves[ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.key] = (
                count_of_person
            )
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.key
                },
                ExpressionAttributeValues={":cd": count_of_person},
            )
            reservation_status, reservation_message, missing_fields = self.check_reservation_status(unique_code)
            if reservation_status == 'complete':
                return reservation_message, ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
            message = textwrap.dedent(
                f"利用者人数は {count_of_person} 人ですね。{self.messages[ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name]}あとは{reservation_message}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name

    def _handle_smoker(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_judge_smoker()
        smoker = self.get_chatgpt_response(system_content, user_message)
        if is_valid_smoker(smoker):
            if smoker == "喫煙":
                message = textwrap.dedent(
                    f"禁煙か喫煙かは {smoker}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_SMOKER.name]}"
                ).strip()
                next_status = ReservationStatus.NEW_RESERVATION_ROOM_TYPE_SMOKER
                return message, next_status.name
            elif smoker == "禁煙":
                message = textwrap.dedent(
                    f"禁煙か喫煙かは {smoker}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_NO_SMOKER.name]}"
                ).strip()
                next_status = ReservationStatus.NEW_RESERVATION_ROOM_TYPE_NO_SMOKER
                return message, next_status.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_SMOKER.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_SMOKER.name

    def _handle_room_type_smoker(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_room_type_smoker()
        room_type_smoker = self.get_chatgpt_response(system_content, user_message)

        if is_valid_room_type_smoker(room_type_smoker):
            self.reserves[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key] = (
                room_type_smoker
            )
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key
                },
                ExpressionAttributeValues={":cd": room_type_smoker},
            )
            reservation_status, reservation_message, missing_fields = self.check_reservation_status(unique_code)
            if reservation_status == 'complete':
                return reservation_message, ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
            message = textwrap.dedent(
                f"部屋タイプは {room_type_smoker} ですね。 {self.messages[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name]}あとは{reservation_message}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_ROOM_TYPE_SMOKER.name

    def _handle_room_type_no_smoker(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        system_content = generate_room_type_no_smoker()
        room_type_no_smoker = self.get_chatgpt_response(system_content, user_message)

        if is_valid_room_type_no_smoker(room_type_no_smoker):
            self.reserves[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key] = (
                room_type_no_smoker
            )
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key
                },
                ExpressionAttributeValues={":cd": room_type_no_smoker},
            )
            reservation_status, reservation_message, missing_fields = self.check_reservation_status(unique_code)
            if reservation_status == 'complete':
                return reservation_message, ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
            message = textwrap.dedent(
                f"部屋タイプは {room_type_no_smoker}  {self.messages[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name]}あとは{reservation_message}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_ROOM_TYPE_NO_SMOKER.name

    def _handle_name(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        name_pattern = r"[、。0-9!-/:-@≠[-`{-~]"
        user_message = re.sub(name_pattern, "", user_message)
        if message_type == "audio":
            system_content = generate_name_yomi()
            name = self.get_chatgpt_response(system_content, user_message)
        else:
            system_content = generate_name_extractor()
            name = self.get_chatgpt_response(system_content, user_message)
        name = name[:20]
        if is_valid_japaneses_character(name):
            self.reserves[ReservationStatus.NEW_RESERVATION_NAME.key] = name
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": ReservationStatus.NEW_RESERVATION_NAME.key
                },
                ExpressionAttributeValues={":cd": name},
            )
            system_content = generate_name_kana()
            name_kana = self.get_chatgpt_response(system_content, name)
            if is_valid_japanese_katakana(name_kana):
                self.reserves[ReservationStatus.NEW_RESERVATION_NAME_KANA.key] = (
                    name_kana
                )
                self.table.update_item(
                    Key={"unique_code": unique_code},
                    UpdateExpression="SET #co = :cd",
                    ExpressionAttributeNames={
                        "#co": ReservationStatus.NEW_RESERVATION_NAME_KANA.key
                    },
                    ExpressionAttributeValues={":cd": name_kana},
                )
            else:
                return self.messages[
                    ReservationStatus.NEW_RESERVATION_NAME.name + "_ERROR"
                ], ReservationStatus.NEW_RESERVATION_NAME.name
            message = textwrap.dedent(
                f"代表者氏名は {name} 、読みは{name_kana}でよろしいでしょうか。 {self.messages[ReservationStatus.NEW_RESERVATION_NAME.name]}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_NAME.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_NAME.name

    def _handle_adult(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        adult = user_message
        system_content = generate_judge_adult()
        adult = self.get_chatgpt_response(system_content, user_message)
        if adult == "ADULT":
            is_adult = True
            self.reserves[ReservationStatus.NEW_RESERVATION_ADULT.key] = is_adult
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": ReservationStatus.NEW_RESERVATION_ADULT.key
                },
                ExpressionAttributeValues={":cd": is_adult},
            )
            reservation_status, reservation_message, missing_fields = self.check_reservation_status(unique_code)
            if reservation_status == 'complete':
                return reservation_message, ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
            message = textwrap.dedent(
                f"{self.messages[ReservationStatus.NEW_RESERVATION_ADULT.name]}あとは{reservation_message}"
            ).strip()
            return message, next_status.name
        elif adult == "CHILD":
            self.table.delete_item(Key={"unique_code": unique_code})
            return self.messages[
                ReservationStatus.NEW_RESERVATION_ADULT.name + "_ERROR_CHILD"
            ], ReservationStatus.RESERVATION_MENU.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_ADULT.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_ADULT.name

    def _handle_phone_number(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        phone_number = user_message
        phone_number = extract_number(phone_number, 10, 11)
        if phone_number is False:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name
        if is_valid_phone_number(phone_number):
            self.reserves[ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.key] = (
                phone_number
            )
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.key
                },
                ExpressionAttributeValues={":cd": phone_number},
            )
            reservation_status, reservation_message, missing_fields = self.check_reservation_status(unique_code)
            if reservation_status == 'complete':
                return reservation_message, ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
            message = textwrap.dedent(
                f"代表者の連絡先は{phone_number}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name]}あとは{reservation_message}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name

    def _handle_reserve_confirm(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        user_message = re.sub(r"[^\w]", "", user_message)
        system_content = generate_confirm_reserve()
        reserve_confirm = self.get_chatgpt_response(system_content, user_message)
        if reserve_confirm in ["True", "TRUE", "1"]:
            table_datas = self.table.get_item(Key={"unique_code": unique_code})
            reserve_datas = table_datas["Item"]
            reserve_datas["check_in"] = datetime.strptime(
                reserve_datas["check_in"], "%Y-%m-%d"
            ).strftime("%Y年%m月%d日")
            reserve_datas["check_out"] = datetime.strptime(
                reserve_datas["check_out"], "%Y-%m-%d"
            ).strftime("%Y年%m月%d日")
            message_template = self.messages[
                ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
            ]
            message = message_template.format(**reserve_datas)
            return message, next_status.name
        elif reserve_confirm in ["Modify", "MODIFY"]:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name + "_MODIFY"
            ], ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name
        elif reserve_confirm in ["False", "FALSE", "0"]:
            self.table.delete_item(Key={"unique_code": unique_code})
            return self.messages[
                ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name + "_REFUSE"
            ], ReservationStatus.RESERVATION_MENU.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name

    def _handle_reserve_execute(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        user_message = re.sub(r"[^\w]", "", user_message)
        system_content = generate_confirm_reserve()
        reserve_execute = self.get_chatgpt_response(system_content, user_message)
        print("reserve_execute", reserve_execute)
        if reserve_execute in ["True", "TRUE", "1"]:
            new_reserve_id = self.get_new_reserve_id()
            if new_reserve_id is None:
                self.table.delete_item(Key={"unique_code": unique_code})
                return (
                    "Failed to obtain a reservation number.",
                    ReservationStatus.RESERVATION_MENU.name,
                )
            table_datas = self.table.get_item(Key={"unique_code": unique_code})
            datas = table_datas["Item"]
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_datas = self.set_line_users_data(user_id, datas, current_datetime)
            reserve_datas = self.set_line_reserves_data(
                user_id, datas, new_reserve_id, current_date, current_datetime
            )
            reservation_message, reservation_id = self.send_reservation_data(
                reserve_datas, user_datas
            )
            self.table.delete_item(Key={"unique_code": unique_code})
            message_template = self.messages[
                ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name
            ]
            message = message_template.format(reservation_id)
            # message = textwrap.dedent(
            #     f"{reservation_message}\n{reservation_id}"
            # ).strip()
            return message, next_status.name
        elif reserve_execute in ["Modify", "MODIFY"]:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name + "_MODIFY"
            ], ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name
        elif reserve_execute in ["False", "FALSE", "0"]:
            self.table.delete_item(Key={"unique_code": unique_code})
            return self.messages[
                ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name + "_REFUSE"
            ], ReservationStatus.RESERVATION_MENU.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name + "_ERROR"
            ], ReservationStatus.NEW_RESERVATION_RESERVE_EXECUTE.name

    def _calculate_checkout_date(self, checkin_date, stay_length):
        return (
            datetime.strptime(checkin_date, "%Y-%m-%d")
            + timedelta(days=int(stay_length))
        ).strftime("%Y-%m-%d")

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(
            self.api_key, "gpt-4o", 0, system_content, user_message
        )
