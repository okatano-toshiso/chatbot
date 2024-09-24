import os, textwrap
from datetime import datetime, timedelta
from reservation_status import ReservationStatus, CheckReservationStatus
# from google.cloud import firestore, storage
from chatgpt_api import get_chatgpt_response
from generate import (
    generate_reserve_number
)
from validation import (
    is_valid_phone_number,
    is_valid_reserve_number
)
import requests
import json
import boto3

reserves = {}
users = {}
# db = firestore.Client()

class ReservationCheckHandler:


    def __init__(self, table_name, api_key, messages):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.api_key = os.environ['OPENAI_API_KEY']
        self.access_token = os.environ['ACCESS_TOKEN']
        self.messages = messages
        self.check_reserves = {}
        self.temp_data = {}
        self.handlers = {
            # CheckReservationStatus.CHECK_RESERVATION_NUMBER: self._handle_check_reservation_number,
            CheckReservationStatus.CHECK_RESERVATION_NAME: self._handle_check_reservation_name,
            CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER: self._handle_check_reservation_phone_number,
            CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER: self._handle_check_reservation_get_number,
            CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE: self._handle_check_reservation_get_number_more
        }


    def handle_reservation_step(self, status, user_message, next_status, user_id=None ,unique_code=None):
        if status in self.handlers:
            return self.handlers[status](user_message, next_status, user_id=user_id ,unique_code=unique_code)
        else:
            raise ValueError(f'Unsupported reservation status: {status}')


    def _handle_check_reservation_name(self, user_message, next_status, user_id ,unique_code):

        reservation_name = user_message

        current_time = datetime.now()
        expiry_time = current_time + timedelta(minutes=5)
        expiry_timestamp = int(expiry_time.timestamp())

        if reservation_name:
            self.check_reserves[CheckReservationStatus.CHECK_RESERVATION_NAME.key] = reservation_name
            self.table.put_item(
                Item={
                    'unique_code': unique_code,
                    'line_id': user_id,
                    'ExpirationTime' :expiry_timestamp,
                    'name': reservation_name,
                }
            )
            message = f'{reservation_name}\n{self.messages[CheckReservationStatus.CHECK_RESERVATION_NAME.name]}'
            return message, next_status.name
        else:
            return self.messages[CheckReservationStatus.CHECK_RESERVATION_NAME.name + '_ERROR'], CheckReservationStatus.CHECK_RESERVATION_NAME.name

    def _handle_check_reservation_phone_number(self, user_message, next_status, user_id ,unique_code):
        reservation_phone_number = user_message
        if is_valid_phone_number(reservation_phone_number):
            self.check_reserves[CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.key] = reservation_phone_number
            self.table.update_item(
                Key={'unique_code': unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={'#co': CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.key},
                ExpressionAttributeValues={':cd': reservation_phone_number}
            )
            message = f'{reservation_phone_number}\n{self.messages[CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name]}'
            return message, next_status.name
        else:
            return self.messages[CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name + '_ERROR'], CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name

    def _handle_check_reservation_get_number(self, user_message, next_status, user_id ,unique_code):

        if user_message == '確認':
            self.table.update_item(
                Key={'unique_code': unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={
                    '#co': 'line_id'
                },
                ExpressionAttributeValues={
                    ':cd': user_id
                }
            )
            table_datas = self.table.get_item(
                Key={
                    'unique_code': unique_code
                }
            )
            reserve_datas = table_datas.get('Item', {})
            keys_to_remove = ['ExpirationTime', 'unique_code']
            for key in keys_to_remove:
                if key in reserve_datas:
                    del reserve_datas[key]
            if reserve_datas:
                data = reserve_datas
                url = os.environ['API_SAVE_RESERVE_DATA']
            try:
                json_data = json.dumps(data)
                response = requests.get(url, json=json.loads(json_data))
                print("response", response)
                try:
                    response = requests.get(url, params=reserve_datas)
                    if response.status_code != 200:
                        print(f"error: status_code is {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"error message: {e}")

                if response.status_code == 200:
                    reserve_datas = json.loads(response.json().get('body', []))
                    print('予約内容', reserve_datas)
                    if not reserve_datas:
                        return "予約データはありませんでした。", ReservationStatus.RESERVATION_MENU.name

                    message = "予約内容を出力します。\n"
                    for index, reserve_data in enumerate(reserve_datas):
                        if index >= 5:
                            break
                        message_template = self.messages[CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name]
                        message += message_template.format(**reserve_data) + "\n"
                    if len(reserve_datas) > 5:
                        message += """----------------------------------------\n予約内容を変更したいときは変更したい予約番号を入力してください。\n続きの予約を見たい場合は「もっと見る」と応答してください。"""
                        next_stage = CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER_MORE.name
                    else:
                        message += """----------------------------------------\n予約内容を変更したいときは変更したい予約番号を入力してください。
                        """
                        next_stage = ReservationStatus.RESERVATION_MENU.name
                    message = message.strip()
                    return message, next_stage
                else:
                    print(f'Error: Received unexpected status code {response.status_code}')
                    return self.messages[str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name) + '_ERROR_API'], ReservationStatus.RESERVATION_MENU.name
            except requests.exceptions.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                return self.messages[str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name) + '_ERROR'], ReservationStatus.RESERVATION_MENU.name
            except Exception as err:
                print(f'An error occurred: {err}')
                return self.messages[str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name) + '_ERROR'], ReservationStatus.RESERVATION_MENU.name
        else:
            return self.messages[str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name) + '_ERROR'], ReservationStatus.RESERVATION_MENU.name

    def _handle_check_reservation_get_number_more(self, user_message, next_status, user_id):
        if user_message == 'もっと見る':
            self.db_ref.set({
                'line_id': user_id,
                'token': self.access_token,
            }, merge=True)
            data_doc = self.db_ref.get()
            if data_doc.exists:
                data = data_doc.to_dict()
                url = os.environ['API_CHECK_RESERVE_DATA']
            try:
                json_data = json.dumps(data)
                response = requests.post(url, json=json.loads(json_data))
                if response.status_code == 200:
                    reserve_datas = response.json().get('reservations', [])
                    message = "続きの予約内容を出力します。\n"
                    for index, reserve_data in enumerate(reserve_datas):
                        if index < 5:
                            continue
                        message_template = self.messages[CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name]
                        message += message_template.format(**reserve_data) + "\n"
                    message += """----------------------------------------
                        予約内容を変更したいときは変更したい予約番号を入力してください。
                    """
                    next_pahase = next_status.name
                    message = message.strip()
                    return message, next_pahase
                else:
                    print(f'Error: Received unexpected status code {response.status_code}')
                    return self.messages[str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name) + '_ERROR_API'], ReservationStatus.RESERVATION_MENU.name
            except requests.exceptions.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                return self.messages[str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name) + '_ERROR'], ReservationStatus.RESERVATION_MENU.name
            except Exception as err:
                print(f'An error occurred: {err}')
                return self.messages[str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name) + '_ERROR'], ReservationStatus.RESERVATION_MENU.name
        else:
            return self.messages[str(CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name) + '_ERROR'], ReservationStatus.RESERVATION_MENU.name



    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(self.api_key, 'gpt-3.5-turbo', 0, system_content, user_message)

