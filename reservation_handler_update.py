import os, textwrap
from datetime import datetime, timedelta
from reservation_status import ReservationStatus, CheckReservationStatus, UpdateReservationStatus, ErrorReservationStatus
# from google.cloud import firestore, storage
from chatgpt_api import get_chatgpt_response
from generate import (
    generate_update_menu,
    generate_start_date,
    generate_stay,
    generate_reserve_confirm
)
from validation import (
    is_valid_phone_number,
    is_valid_date,
    is_single_digit_number
)
import requests
import json
import boto3
from decimal import Decimal

reserves = {}
users = {}
# db = firestore.Client()

class ReservationUpdateHandler:

    def _convert_decimal_to_int(self, data):
        if isinstance(data, dict):
            return {key: self._convert_decimal_to_int(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_decimal_to_int(element) for element in data]
        elif isinstance(data, Decimal):
            return int(data)
        else:
            return data


    def _fetch_reservation_data(self, unique_code, user_id):
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

        reserve_datas = self._convert_decimal_to_int(reserve_datas)

        if reserve_datas:
            data = reserve_datas
            url = os.environ['API_SAVE_RESERVE_DATA']
            access_token = os.environ.get('ACCESS_TOKEN')
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
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
            print(f'HTTP error occurred: {http_err}')
            return None
        except Exception as err:
            print(f'An error occurred: {err}')
            return None
        if response.status_code == 200:
            print(f"Response text: {response.text}")
            print(f"Response text の型: {type(response.text)}")
            if response.text is None or response.text == '' or response.text == 'null':
                return None
            return json.loads(response.json().get('body', []))
        else:
            print(f'Error: Received unexpected status code {response.status_code}')
            return None


    def __init__(self, table_name, api_key, messages):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.api_key = os.environ['OPENAI_API_KEY']
        self.access_token = os.environ['ACCESS_TOKEN']
        self.messages = messages
        self.check_reserves = {}
        self.temp_data = {}
        self.handlers = {
            UpdateReservationStatus.UPDATE_RESERVATION_START: self._handle_update_reservation_start,
            UpdateReservationStatus.UPDATE_RESERVATION_START: self._handle_update_reservation_start,
            UpdateReservationStatus.UPDATE_RESERVATION_START: self._handle_update_reservation_start,
            UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN: self._handle_update_reservation_checkin,
            UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT: self._handle_update_reservation_checkout,
            UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM: self._handle_update_reservation_confirm,
            # UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE: self._handle_update_reservation_execute,
            # UpdateReservationStatus.UPDATE_RESERVATION_COMPLETE: self._handle_update_reservation_complete
        }

    def handle_reservation_step(self, status, user_message, next_status, user_id=None ,unique_code=None):
        if status in self.handlers:
            return self.handlers[status](user_message, next_status, user_id=user_id ,unique_code=unique_code)
        else:
            raise ValueError(f'Unsupported reservation status: {status}')


    def _handle_update_reservation_start(self, user_message, next_status, user_id ,unique_code):
        system_content = generate_update_menu()
        update_menu = self.get_chatgpt_response(system_content, user_message)

        current_time = datetime.now()
        expiry_time = current_time + timedelta(minutes=5)
        expiry_timestamp = int(expiry_time.timestamp())

        reserve_datas = self._fetch_reservation_data(unique_code, user_id)

        if isinstance(reserve_datas, list):
            for data in reserve_datas:
                data['unique_code'] = unique_code
                data['ExpirationTime'] = expiry_timestamp

        elif isinstance(reserve_datas, dict):
            reserve_datas['unique_code'] = unique_code
            reserve_datas['ExpirationTime'] = expiry_timestamp

        print('reserve_datas', reserve_datas)

        try:
            response = self.table.put_item(Item=reserve_datas)
            print("Data inserted successfully:", response)
        except Exception as e:
            print("An error occurred222222:", e)

        # 1. チェックイン日と宿泊数
        # 2. 利用者人数
        # 3. 部屋タイプ
        # 4. 代表者氏名
        # 5. 連絡先電話番号

        if isinstance(update_menu, str) and update_menu.isdigit():
            update_menu = int(update_menu)
        print("prompt's response", update_menu)

        if isinstance(update_menu, int) and 0 <= update_menu <= 5:
            print("int check ok between 0-5")
            if update_menu == 1:
                message = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_CHECKIN"]}'
                return message, UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name
            if update_menu == 2:
                message = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name]}'
                return message, UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name
                # message = f'{update_menu}\n{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name]}'
                # return message, UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name
            if update_menu == 3:
                message = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name]}'
                return message, UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name
                # message = f'{update_menu}\n{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name]}'
                # return message, UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name
            if update_menu == 4:
                message = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name]}'
                return message, UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name
                # message = f'{update_menu}\n{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_NAME.name]}'
                # return message, UpdateReservationStatus.UPDATE_RESERVATION_NAME.name
            if update_menu == 5:
                message = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name]}'
                return message, UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name
                # message = f'{update_menu}\n{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name]}'
                # return message, UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name
            if update_menu == 0:
                return self.messages[UpdateReservationStatus.UPDATE_RESERVATION_START.name + '_SELECT_ERROR'], UpdateReservationStatus.UPDATE_RESERVATION_START.name
        else:
            return self.messages[UpdateReservationStatus.UPDATE_RESERVATION_START.name + '_SELECT_ERROR'], UpdateReservationStatus.UPDATE_RESERVATION_START.name

    def _handle_update_reservation_checkin(self, user_message, next_status, user_id ,unique_code):
        system_content = generate_start_date()
        check_in_date = self.get_chatgpt_response(system_content, user_message)
        if is_valid_date(check_in_date):
            formatted_date = datetime.strptime(check_in_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            ymd_format = datetime.strptime(check_in_date, '%Y-%m-%d').strftime('%Y年%m月%d日')
            self.check_reserves[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.key] = formatted_date
            self.table.update_item(
                Key={'unique_code': unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={'#co': UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.key},
                ExpressionAttributeValues={':cd': formatted_date}
            )
            message = f'{ymd_format} {self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name]}'
            return message, next_status.name
        else:
            return self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name + '_ERROR'], UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name

    def _handle_update_reservation_checkout(self, user_message, next_status, user_id ,unique_code):
        system_content = generate_stay()
        stay_length = self.get_chatgpt_response(system_content, user_message)
        table_datas = self.table.get_item(
            Key={
                'unique_code': unique_code
            }
        )
        checkin_date = table_datas['Item']['check_in']

        if checkin_date and is_single_digit_number(stay_length):
            checkout_date = self._calculate_checkout_date(checkin_date, stay_length)
            formatted_checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            ymd_format_checkout = datetime.strptime(checkout_date, '%Y-%m-%d').strftime('%Y年%m月%d日')
            ymd_format_checkin = datetime.strptime(checkin_date, '%Y-%m-%d').strftime('%Y年%m月%d日')

            self.check_reserves[UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.key] = formatted_checkout_date
            self.table.update_item(
                Key={'unique_code': unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={'#co': UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.key},
                ExpressionAttributeValues={':cd': formatted_checkout_date}
            )
            message = textwrap.dedent(f'チェックイン日は{ymd_format_checkin}、宿泊数は {stay_length}泊、チェックアウト日は {ymd_format_checkout}になります。 {self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name]}').strip()
            return message, next_status.name
        else:
            return self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name + '_ERROR'], UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name


    def _handle_update_reservation_confirm(self, user_message, next_status, user_id ,unique_code):
        reserve_confirm = user_message
        system_content = generate_reserve_confirm()
        reserve_confirm = self.get_chatgpt_response(system_content, user_message)
        print(type(reserve_confirm))
        print(reserve_confirm)

        if reserve_confirm == "True" or reserve_confirm == "はい" or  reserve_confirm == True or  reserve_confirm == 1:
            print("OK")
            table_datas = self.table.get_item(
                Key={
                    'unique_code': unique_code
                }
            )
            reserve_datas = table_datas['Item']
            print(reserve_datas)
            message_template = self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name]
            message = message_template.format(**reserve_datas)
            return message, next_status.name
        else:
            print("NG")
            self.table.delete_item(
                Key={
                    'unique_code': unique_code
                }
            )
            return self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name + "_ERROR"], ReservationStatus.RESERVATION_MENU.name





    def _calculate_checkout_date(self, checkin_date, stay_length):
        return (datetime.strptime(checkin_date, '%Y-%m-%d') + timedelta(days=int(stay_length))).strftime('%Y-%m-%d')

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(self.api_key, 'gpt-4o', 0, system_content, user_message)

