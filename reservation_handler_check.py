import os
import re

# import textwrap  # noqa: F401
# from datetime import datetime, timedelta
from reservation_status import (
    ReservationStatus,
    CheckReservationStatus,
    UpdateReservationStatus,
)
from chatgpt_api import get_chatgpt_response
from prompts.confirm_reserve import generate_confirm_reserve
from prompts.name_yomi import generate_name_yomi
from prompts.name_extractor import generate_name_extractor
from prompts.stop_update import generate_stop_update

from validation import is_valid_phone_number
import requests  # type: ignore
import json
import boto3  # type: ignore
from utils.digit_extractor import extract_number


reserves = {}
users = {}


class ReservationCheckHandler:
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

    def __init__(self, table_name, api_key, messages):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.messages = messages
        self.check_reserves = {}
        self.temp_data = {}
        self.handlers = {
            # CheckReservationStatus.CHECK_RESERVATION_NUMBER: self._handle_check_reservation_number,
            CheckReservationStatus.CHECK_RESERVATION_NAME: self._handle_check_reservation_name,
            CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER: self._handle_check_reservation_phone_number,
            CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER: self._handle_check_reservation_get_number,
            CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE: self._handle_check_reservation_get_number_more,
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
                message_type=message_type,
            )
        else:
            raise ValueError(f"Unsupported reservation status: {status}")

    def _handle_check_reservation_name(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        name_pattern = r"[、。0-9!-/:-@≠[-`{-~]"
        user_message = re.sub(name_pattern, "", user_message)
        if message_type == "audio":
            system_content = generate_name_yomi()
            reservation_name = self.get_chatgpt_response(system_content, user_message)
        else:
            system_content = generate_name_extractor()
            reservation_name = self.get_chatgpt_response(system_content, user_message)
        reservation_name = reservation_name[:20]
        if reservation_name:
            self.check_reserves[CheckReservationStatus.CHECK_RESERVATION_NAME.key] = (
                reservation_name
            )
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": CheckReservationStatus.CHECK_RESERVATION_NAME.key
                },
                ExpressionAttributeValues={":cd": reservation_name},
            )
            message = f"{reservation_name}\n{self.messages[CheckReservationStatus.CHECK_RESERVATION_NAME.name]}"
            return message, next_status.name
        else:
            return self.messages[
                CheckReservationStatus.CHECK_RESERVATION_NAME.name + "_ERROR"
            ], CheckReservationStatus.CHECK_RESERVATION_NAME.name

    def _handle_check_reservation_phone_number(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        reservation_phone_number = user_message
        reservation_phone_number = extract_number(reservation_phone_number, 10, 11)
        if is_valid_phone_number(reservation_phone_number):
            self.check_reserves[
                CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.key
            ] = reservation_phone_number
            self.table.update_item(
                Key={"unique_code": unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    "#co": CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.key
                },
                ExpressionAttributeValues={":cd": reservation_phone_number},
            )
            message = f"{reservation_phone_number}\n{self.messages[CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name]}"
            return message, next_status.name
        else:
            return self.messages[
                CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name + "_ERROR"
            ], CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name

    def _handle_check_reservation_get_number(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        check_confirm = user_message
        system_content = generate_confirm_reserve()
        check_confirm = self.get_chatgpt_response(system_content, user_message)
        reserve_datas = self._fetch_reservation_data(unique_code, user_id)
        if reserve_datas is None or reserve_datas == [] or reserve_datas == {}:
            return self.messages[
                CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name + "_ERROR_API"
            ], ReservationStatus.RESERVATION_MENU.name
        if check_confirm in ["True", "TRUE", "1"]:
            message = "ご予約内容を確認いたします。\n"
            for index, reserve_data in enumerate(reserve_datas):
                reserve_data["reservation_id_yomi"] = str(
                    reserve_data["reservation_id"]
                )
                reserve_data["reservation_id_yomi"] = " ".join(
                    reserve_data["reservation_id_yomi"]
                )
                message_template = self.messages[
                    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name
                ]
                message += message_template.format(**reserve_data) + "\n"
            message += """----------------------------------------\n予約内容の変更をご希望の場合、変更したいご予約の予約番号を教えてください。"""
            message = message.strip()
            return message, next_status.name
        elif check_confirm in ["False", "FALSE", "0"]:
            return self.messages[
                str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name)
                + "_REFUSE"
            ], ReservationStatus.RESERVATION_MENU.name
        else:
            return self.messages[
                str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name) + "_ERROR"
            ], CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name

    def _handle_check_reservation_get_number_more(
        self, user_message, next_status, user_id, unique_code, message_type
    ):
        reserve_datas = self._fetch_reservation_data(unique_code, user_id)
        if not reserve_datas:
            return self.messages[
                CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name + "_ERROR_API"
            ], ReservationStatus.RESERVATION_MENU.name
        system_content = generate_stop_update()
        stop_update = self.get_chatgpt_response(system_content, user_message)
        if stop_update == "True":
            return self.messages[
                str(UpdateReservationStatus.UPDATE_RESERVATION_START.name) + "_REFUSE"
            ], ReservationStatus.RESERVATION_MENU.name
        if user_message:
            user_message = extract_number(user_message, 7)
            if not user_message:
                return self.messages[
                    str(UpdateReservationStatus.UPDATE_RESERVATION_START.name)
                    + "_ERROR"
                ], CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE.name
            if user_message.isdigit():
                if any(
                    item["reservation_id"] == int(user_message)
                    for item in reserve_datas
                ):
                    self.check_reserves["reservation_id"] = int(user_message)
                    self.table.update_item(
                        Key={"unique_code": unique_code},
                        UpdateExpression="SET #co = :cd",
                        ExpressionAttributeNames={"#co": "reservation_id"},
                        ExpressionAttributeValues={":cd": int(user_message)},
                    )
                    return self.messages[
                        str(UpdateReservationStatus.UPDATE_RESERVATION_START.name)
                    ], next_status.name
                else:
                    return self.messages[
                        str(UpdateReservationStatus.UPDATE_RESERVATION_START.name)
                        + "_RESERVATION_ID_ERROR"
                    ], CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE.name
            else:
                return self.messages[
                    str(UpdateReservationStatus.UPDATE_RESERVATION_START.name)
                    + "_RESERVATION_ID_ERROR"
                ], CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE.name
        else:
            return self.messages[
                str(UpdateReservationStatus.UPDATE_RESERVATION_START.name) + "_ERROR"
            ], CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE.name

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(
            self.api_key, "gpt-4o", 0, system_content, user_message
        )
