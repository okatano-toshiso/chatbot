import os
import textwrap
from datetime import datetime, timedelta
from reservation_status import ReservationStatus, UpdateReservationStatus
from chatgpt_api import get_chatgpt_response
from prompts.judge_update_inquiry import generate_judge_update_inquiry
from prompts.checkin_date import generate_checkin_date
from prompts.count_of_stay import generate_count_of_stay
from prompts.count_of_person import generate_count_of_person
from prompts.judge_smoker import generate_judge_smoker
from prompts.confirm_cancel import generate_confirm_cancel
from prompts.confirm_reserve import generate_confirm_reserve
from prompts.room_type_smoker import generate_room_type_smoker
from prompts.room_type_no_smoker import generate_room_type_no_smoker
from prompts.name_kana import generate_name_kana
from validation import (
    is_valid_japaneses_character,
    is_valid_phone_number,
    is_valid_date,
    is_single_digit_number,
    is_valid_smoker,
    is_valid_room_type_smoker,
    is_valid_room_type_no_smoker,
    is_valid_japanese_katakana
)
import requests  # type: ignore
import json
import boto3  # type: ignore
from decimal import Decimal
from utils.clean_phone_number import clean_phone_number

reserves = {}
users = {}


class ReservationUpdateHandler:
    def _convert_decimal_to_int(self, data):
        if isinstance(data, dict):
            return {
                key: self._convert_decimal_to_int(value) for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._convert_decimal_to_int(element) for element in data]
        elif isinstance(data, Decimal):
            return int(data)
        else:
            return data

    def _fetch_reservation_data(self, unique_code, user_id):
        self.table.update_item(
            Key={"unique_code": unique_code},
            UpdateExpression="SET #co = :cd",
            ExpressionAttributeNames={"#co": "line_id"},
            ExpressionAttributeValues={":cd": user_id},
        )
        table_datas = self.table.get_item(Key={"unique_code": unique_code})
        reserve_datas = table_datas.get("Item", {})
        keys_to_remove = ["ExpirationTime", "unique_code"]
        for key in keys_to_remove:
            if key in reserve_datas:
                del reserve_datas[key]
        reserve_datas = self._convert_decimal_to_int(reserve_datas)
        if reserve_datas:
            data = reserve_datas
            url = os.environ["API_SAVE_RESERVE_DATA"]
            access_token = os.environ.get("ACCESS_TOKEN")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
        try:
            json_data = json.dumps(data)
            response = requests.get(url, json=json.loads(json_data))
            try:
                response = requests.get(url, params=reserve_datas, headers=headers)
                if response.status_code != 200:
                    print(f"error: status_code is {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"error message: {e}")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return None
        except Exception as err:
            print(f"An error occurred: {err}")
            return None
        if response.status_code == 200:
            if response.text is None or response.text == "" or response.text == "null":
                return None
            return json.loads(response.json().get("body", []))
        else:
            print(f"Error: Received unexpected status code {response.status_code}")
            return None

    def set_line_users_data_update(self, user_id, datas, current_datetime):
        line_users = {
            "line_id": datas["line_id"],
            "name": datas["name"],
            "name_kana": datas["name_kana"] if datas["name_kana"] is not None else "フリガナ",
            "phone_number": datas["phone_number"],
            "created_at": current_datetime,
            "updated_at": current_datetime,
        }

        if "new_name" in datas and datas["new_name"]:
            line_users["new_name"] = datas["new_name"]

        if "new_name_kana" in datas and datas["new_name_kana"]:
            line_users["new_name_kana"] = datas["new_name_kana"]

        if "new_phone_number" in datas and datas["new_phone_number"]:
            line_users["new_phone_number"] = datas["new_phone_number"]

        return line_users

    def set_line_reserves_data_update(
        self, user_id, datas, new_reserve_id, current_date, current_datetime
    ):
        line_reserves = {
            "id": datas["id"],
            "reservation_id": datas["reservation_id"],
            "reservation_date": current_date,
            "line_id": datas["line_id"],
            "name": datas["name"],
            "phone_number": datas["phone_number"],
            "check_in": datas["check_in"],
            "check_out": datas["check_out"],
            "room_type": datas["room_type"],
            "count_of_person": datas["count_of_person"],
            "status": "UPDATED",
            "created_at": datas["created_at"],
            "updated_at": current_datetime,
        }

        if "new_name" in datas and datas["new_name"]:
            line_reserves["name"] = datas["new_name"]

        if "new_phone_number" in datas and datas["new_phone_number"]:
            line_reserves["phone_number"] = datas["new_phone_number"]

        return line_reserves

    def set_line_reserves_data_cancel(
        self, user_id, datas, new_reserve_id, current_date, current_datetime
    ):
        line_reserves = {
            "id": datas["id"],
            "reservation_id": datas["reservation_id"],
            "reservation_date": current_date,
            "line_id": datas["line_id"],
            "name": datas["name"],
            "phone_number": datas["phone_number"],
            "check_in": datas["check_in"],
            "check_out": datas["check_out"],
            "room_type": datas["room_type"],
            "count_of_person": datas["count_of_person"],
            "status": "CANCEL",
            "created_at": datas["created_at"],
            "updated_at": current_datetime,
        }

        return line_reserves

    def send_reservation_data_update(self, reserve_datas, user_datas):
        data = {"line_reserves": [reserve_datas], "line_users": [user_datas]}
        url = os.environ["API_SAVE_RESERVE_DATA"]
        access_token = os.environ.get("ACCESS_TOKEN")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.put(url, json=data, headers=headers)
            if response.status_code == 200:
                reservation_id = reserve_datas.get("reservation_id")
                return self.messages[
                    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name
                ], reservation_id
            else:
                print(
                    f"Unexpected status code: {response.status_code}, Response: {response.text}"
                )
                return self.messages[
                    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name + "_ERROR"
                ], ReservationStatus.RESERVATION_MENU.name
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return f"Failed to submit reservation: {http_err}", "ERROR_STATUS"
        except Exception as err:
            print(f"An error occurred: {err}")
            return f"An unexpected error has occurred.: {err}", "ERROR_STATUS"

    def send_reservation_data_cancel(self, reserve_datas):
        data = {"line_reserves": [reserve_datas]}
        url = os.environ["API_SAVE_RESERVE_DATA"]
        access_token = os.environ.get("ACCESS_TOKEN")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.delete(url, json=data, headers=headers)
            if response.status_code == 200:
                reservation_id = reserve_datas.get("reservation_id")
                return self.messages[
                    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name
                ], reservation_id
            else:
                print(
                    f"Unexpected status code: {response.status_code}, Response: {response.text}"
                )
                return self.messages[
                    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name + "_ERROR"
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
        self.check_reserves = {}
        self.temp_data = {}
        self.handlers = {
            UpdateReservationStatus.UPDATE_RESERVATION_START: self._handle_update_reservation_start,
            UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN: self._handle_update_reservation_checkin,
            UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT: self._handle_update_reservation_checkout,
            UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON: self._handle_update_reservation_count_of_person,
            UpdateReservationStatus.UPDATE_RESERVATION_SMOKER: self._handle_update_smoker,
            UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_SMOKER: self._handle_update_room_type_smoker,
            UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_NO_SMOKER: self._handle_update_room_type_no_smoker,
            UpdateReservationStatus.UPDATE_RESERVATION_NAME: self._handle_update_name,
            UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER: self._handle_update_phone_number,
            UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM: self._handle_update_reservation_confirm,
            UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE: self._handle_update_reservation_execute,
            UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM: self._handle_update_reservation_cancel_confirm,
            UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_EXECUTE: self._handle_update_reservation_cancel_execute,
        }

    def handle_reservation_step(
        self, status, user_message, next_status, user_id=None, unique_code=None
    ):
        if status in self.handlers:
            return self.handlers[status](
                user_message, next_status, user_id=user_id, unique_code=unique_code
            )
        else:
            raise ValueError(f"Unsupported reservation status: {status}")

    def _handle_update_reservation_start(
        self, user_message, next_status, user_id, unique_code
    ):
        system_content = generate_judge_update_inquiry()
        update_menu = self.get_chatgpt_response(system_content, user_message)
        current_time = datetime.now()
        expiry_time = current_time + timedelta(minutes=5)
        expiry_timestamp = int(expiry_time.timestamp())

        reserve_datas = self._fetch_reservation_data(unique_code, user_id)

        if isinstance(reserve_datas, list):
            for data in reserve_datas:
                data["unique_code"] = unique_code
                data["ExpirationTime"] = expiry_timestamp
                try:
                    response = self.table.put_item(Item=data)
                    print("Data inserted successfully:", response)
                except Exception as e:
                    print("An error occurred:", e)

        try:
            response = self.table.put_item(Item=reserve_datas)
            print("Data inserted successfully:", response)
        except Exception as e:
            print("An error occurred:", e)

        if isinstance(update_menu, str) and update_menu.isdigit():
            update_menu = int(update_menu)

        pre_datas = {}
        if reserve_datas:
            pre_datas = {str(index): value for index, value in enumerate(reserve_datas)}
            pre_datas = pre_datas["0"]

        if isinstance(update_menu, int) and 0 <= update_menu <= 6:
            if update_menu == 1:
                extra_datas = {"title": "チェックインと宿泊数"}
                message_template = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_CHECKIN"]}'
                pre_datas['check_in'] = datetime.strptime(pre_datas['check_in'], "%Y-%m-%d").strftime(
                    "%Y年%m月%d日"
                )
                pre_datas['check_out'] = datetime.strptime(pre_datas['check_out'], "%Y-%m-%d").strftime(
                    "%Y年%m月%d日"
                )
                message = message_template.format(**{**pre_datas, **extra_datas})
                return message, UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name
            if update_menu == 2:
                extra_datas = {"title": "利用者人数"}
                message_template = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_COUNT_OF_PERSON"]}'
                message = message_template.format(**{**pre_datas, **extra_datas})
                return (
                    message,
                    UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name,
                )
            if update_menu == 3:
                extra_datas = {"title": "部屋タイプ"}
                message_template = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_SMOKER"]}'
                message = message_template.format(**{**pre_datas, **extra_datas})
                return message, UpdateReservationStatus.UPDATE_RESERVATION_SMOKER.name
            if update_menu == 4:
                extra_datas = {"title": "代表者"}
                message_template = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_NAME"]}'
                message = message_template.format(**{**pre_datas, **extra_datas})
                return message, UpdateReservationStatus.UPDATE_RESERVATION_NAME.name
            if update_menu == 5:
                extra_datas = {"title": "連絡先"}
                message_template = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_PHONE_NUMBER"]}'
                message = message_template.format(**{**pre_datas, **extra_datas})
                return (
                    message,
                    UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name,
                )
            if update_menu == 6:
                extra_datas = {"title": "キャンセル"}
                message_template = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_CANCEL"]}'
                message = message_template.format(**{**pre_datas, **extra_datas})
                return (
                    message,
                    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM.name,
                )
            if update_menu == 0:
                return self.messages[
                    UpdateReservationStatus.UPDATE_RESERVATION_START.name
                    + "_SELECT_ERROR"
                ], UpdateReservationStatus.UPDATE_RESERVATION_START.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_SELECT_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_START.name

    def _handle_update_reservation_checkin(
        self, user_message, next_status, user_id, unique_code
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
            self.check_reserves[
                UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.key
            ] = formatted_date
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.key
                },
                ExpressionAttributeValues={":cd": formatted_date},
            )
            message = f"{ymd_format} {self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name]}"
            return message, next_status.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name

    def _handle_update_reservation_checkout(
        self, user_message, next_status, user_id, unique_code
    ):
        system_content = generate_count_of_stay()
        stay_length = self.get_chatgpt_response(system_content, user_message)
        table_datas = self.table.get_item(Key={"unique_code": unique_code})
        checkin_date = table_datas["Item"]["check_in"]

        if checkin_date and is_single_digit_number(stay_length):
            checkout_date = self._calculate_checkout_date(checkin_date, stay_length)
            formatted_checkout_date = datetime.strptime(
                checkout_date, "%Y-%m-%d"
            ).strftime("%Y-%m-%d")
            ymd_format_checkout = datetime.strptime(checkout_date, "%Y-%m-%d").strftime(
                "%Y年%m月%d日"
            )
            ymd_format_checkin = datetime.strptime(checkin_date, "%Y-%m-%d").strftime(
                "%Y年%m月%d日"
            )

            self.check_reserves[
                UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.key
            ] = formatted_checkout_date
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.key
                },
                ExpressionAttributeValues={":cd": formatted_checkout_date},
            )
            message = textwrap.dedent(
                f"チェックイン日は{ymd_format_checkin}、宿泊数は {stay_length}泊、チェックアウト日は {ymd_format_checkout}になります。 {self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name]}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name

    def _handle_update_reservation_count_of_person(
        self, user_message, next_status, user_id, unique_code
    ):
        system_content = generate_count_of_person()
        count_of_person = self.get_chatgpt_response(system_content, user_message)

        if is_single_digit_number(count_of_person):
            count_of_person = int(count_of_person)
            if count_of_person > 2:
                return self.messages[
                    ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name + "_OVER"
                ], UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name
            count_of_person = int(count_of_person)
            self.check_reserves[
                UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.key
            ] = count_of_person
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.key
                },
                ExpressionAttributeValues={":cd": count_of_person},
            )
            message = textwrap.dedent(
                f"利用者人数を {count_of_person} 人に変更いたします。{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name]}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name

    def _handle_update_smoker(self, user_message, next_status, user_id, unique_code):
        system_content = generate_judge_smoker()
        smoker = self.get_chatgpt_response(system_content, user_message)
        if is_valid_smoker(smoker):
            if smoker == "喫煙":
                message = textwrap.dedent(
                    f"禁煙か喫煙かは {smoker}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_SMOKER.name]}"
                ).strip()
                next_status = (
                    UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_SMOKER
                )
                return message, next_status.name
            elif smoker == "禁煙":
                message = textwrap.dedent(
                    f"禁煙か喫煙かは {smoker}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_NO_SMOKER.name]}"
                ).strip()
                next_status = (
                    UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_NO_SMOKER
                )
                return message, next_status.name
        else:
            return self.messages[
                ReservationStatus.NEW_RESERVATION_SMOKER.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_SMOKER.name

    def _handle_update_room_type_smoker(
        self, user_message, next_status, user_id, unique_code
    ):
        system_content = generate_room_type_smoker()
        room_type_smoker = self.get_chatgpt_response(system_content, user_message)
        print("room_type_smoker", room_type_smoker)

        if is_valid_room_type_smoker(room_type_smoker):
            self.check_reserves[
                UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.key
            ] = room_type_smoker
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.key
                },
                ExpressionAttributeValues={":cd": room_type_smoker},
            )
            message = textwrap.dedent(
                f"部屋タイプは {room_type_smoker} ですね。 {self.messages[UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name]}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_SMOKER.name

    def _handle_update_room_type_no_smoker(
        self, user_message, next_status, user_id, unique_code
    ):
        system_content = generate_room_type_no_smoker()
        room_type_no_smoker = self.get_chatgpt_response(system_content, user_message)

        if is_valid_room_type_no_smoker(room_type_no_smoker):
            self.check_reserves[
                UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.key
            ] = room_type_no_smoker
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.key
                },
                ExpressionAttributeValues={":cd": room_type_no_smoker},
            )
            message = textwrap.dedent(
                f"部屋タイプは {room_type_no_smoker} ですね。 {self.messages[UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name]}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE_SMOKER.name

    def _handle_update_name(self, user_message, next_status, user_id, unique_code):
        name = user_message
        if is_valid_japaneses_character(name):
            self.check_reserves[UpdateReservationStatus.UPDATE_RESERVATION_NAME.key] = (
                name
            )
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": UpdateReservationStatus.UPDATE_RESERVATION_NAME.key
                },
                ExpressionAttributeValues={":cd": name},
            )

            system_content = generate_name_kana()
            name_kana = self.get_chatgpt_response(system_content, name)
            if is_valid_japanese_katakana(name_kana):
                self.check_reserves[UpdateReservationStatus.UPDATE_RESERVATION_NAME_KANA.key] = (
                    name_kana
                )
                self.table.update_item(
                    Key={"unique_code": unique_code},
                    UpdateExpression="SET #co = :cd",
                    ExpressionAttributeNames={
                        "#co": UpdateReservationStatus.UPDATE_RESERVATION_NAME_KANA.key
                    },
                    ExpressionAttributeValues={":cd": name_kana},
                )
            else:
                return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_NAME.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_NAME.name
            message = textwrap.dedent(
                f"変更する代表者氏名は {name} ({name_kana})でよろしいでしょうか。 {self.messages[UpdateReservationStatus.UPDATE_RESERVATION_NAME.name]}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_NAME.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_NAME.name

    def _handle_update_phone_number(
        self, user_message, next_status, user_id, unique_code
    ):
        phone_number = user_message
        phone_number = clean_phone_number(phone_number)
        if is_valid_phone_number(phone_number):
            self.check_reserves[
                UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.key
            ] = phone_number
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.key
                },
                ExpressionAttributeValues={":cd": phone_number},
            )
            message = textwrap.dedent(
                f"変更する電話番号は {phone_number} でよろしいでしょうか。 {self.messages[UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name]}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name

    def _handle_update_reservation_confirm(
        self, user_message, next_status, user_id, unique_code
    ):
        reserve_confirm = user_message
        system_content = generate_confirm_reserve()
        reserve_confirm = self.get_chatgpt_response(system_content, user_message)

        if (
            reserve_confirm == "True"
            or reserve_confirm == "はい"
            or reserve_confirm is True
            or reserve_confirm == 1
        ):
            table_datas = self.table.get_item(Key={"unique_code": unique_code})
            reserve_datas = table_datas["Item"]

            if "new_name" in reserve_datas and "new_phone_number" in reserve_datas:
                message_template = self.messages[
                    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name
                    + "_NAME_PHONE"
                ]
            elif "new_phone_number" in reserve_datas:
                message_template = self.messages[
                    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name + "_PHONE"
                ]
            else:
                message_template = self.messages[
                    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name
                ]
            reserve_datas["check_in"] = datetime.strptime(reserve_datas["check_in"], '%Y-%m-%d').strftime('%m月%d日')
            reserve_datas["check_out"] = datetime.strptime(reserve_datas["check_out"], '%Y-%m-%d').strftime('%m月%d日')

            message = message_template.format(**reserve_datas)
            return message, next_status.name
        else:
            # self.table.delete_item(Key={"unique_code": unique_code})
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_START.name

    def _handle_update_reservation_execute(
        self, user_message, next_status, user_id, unique_code
    ):
        if user_message == "変更":
            table_datas = self.table.get_item(Key={"unique_code": unique_code})
            datas = table_datas["Item"]
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            user_datas = self.set_line_users_data_update(
                user_id, datas, current_datetime
            )
            reserve_datas = self.set_line_reserves_data_update(
                user_id, datas, None, current_date, current_datetime
            )
            reservation_message, reservation_id = self.send_reservation_data_update(
                reserve_datas, user_datas
            )
            message = textwrap.dedent(
                f"{reservation_message}\n{reservation_id}"
            ).strip()

            new_name = datas.get("new_name")
            new_name_kana = datas.get("new_name_kana")
            new_phone_number = datas.get("new_phone_number")

            update_expressions = []
            expression_attribute_values = {}
            expression_attribute_names = {}

            if new_name:
                update_expressions.append("#n = :name")
                expression_attribute_values[":name"] = new_name
                expression_attribute_names["#n"] = "name"
            if new_name_kana:
                update_expressions.append("#k = :name_kana")
                expression_attribute_values[":name_kana"] = new_name_kana
                expression_attribute_names["#k"] = "name_kana"
            if new_phone_number:
                update_expressions.append("#p = :phone")
                expression_attribute_values[":phone"] = new_phone_number
                expression_attribute_names["#p"] = "phone_number"

            if update_expressions:
                self.table.update_item(
                    Key={"unique_code": unique_code},
                    UpdateExpression=f"SET {', '.join(update_expressions)}",
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                )

            remove_expressions = []
            remove_expression_attribute_names = {}

            if "new_name" in datas:
                remove_expressions.append("#new_name")
                remove_expression_attribute_names["#new_name"] = "new_name"
            if "new_name_kana" in datas:
                remove_expressions.append("#new_name_kana")
                remove_expression_attribute_names["#new_name_kana"] = "new_name_kana"
            if "new_phone_number" in datas:
                remove_expressions.append("#new_phone")
                remove_expression_attribute_names["#new_phone"] = "new_phone_number"

            if remove_expressions:
                self.table.update_item(
                    Key={"unique_code": unique_code},
                    UpdateExpression=f"REMOVE {', '.join(remove_expressions)}",
                    ExpressionAttributeNames=remove_expression_attribute_names,
                )
            return message, next_status.name
        else:
            # self.table.delete_item(Key={"unique_code": unique_code})
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_START.name

    def _handle_update_reservation_cancel_confirm(
        self, user_message, next_status, user_id, unique_code
    ):
        print("user_message", user_message)
        cancel_confirm = user_message
        system_content = generate_confirm_cancel()
        cancel_confirm = self.get_chatgpt_response(system_content, user_message)
        print("cancel_confirm", cancel_confirm)
        if (
            cancel_confirm == "True"
            or cancel_confirm == "はい"
            or cancel_confirm is True
            or cancel_confirm == 1
        ):
            message = self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM.name
            ]
            return message, next_status.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_START.name

    def _handle_update_reservation_cancel_execute(
        self, user_message, next_status, user_id, unique_code
    ):
        print("user_message", user_message)
        if user_message == "キャンセル":
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={"#co": "status"},
                ExpressionAttributeValues={":cd": "CANCEL"},
            )
            table_datas = self.table.get_item(Key={"unique_code": unique_code})
            datas = table_datas["Item"]
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reserve_datas = self.set_line_reserves_data_cancel(
                user_id, datas, None, current_date, current_datetime
            )
            reservation_message, reservation_id = self.send_reservation_data_cancel(
                reserve_datas
            )
            message = textwrap.dedent(
                f"{reservation_message}\n{reservation_id}"
            ).strip()
            return message, next_status.name
        else:
            return self.messages[
                UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name + "_ERROR"
            ], UpdateReservationStatus.UPDATE_RESERVATION_START.name

    def _calculate_checkout_date(self, checkin_date, stay_length):
        return (
            datetime.strptime(checkin_date, "%Y-%m-%d")
            + timedelta(days=int(stay_length))
        ).strftime("%Y-%m-%d")

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(
            self.api_key, "gpt-4o", 0, system_content, user_message
        )
