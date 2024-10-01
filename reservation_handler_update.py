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

reserves = {}
users = {}
# db = firestore.Client()

class ReservationUpdateHandler:

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
                message = f'{self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name] + "_CHECKIN"}'
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
            current_time = datetime.now()
            expiry_time = current_time + timedelta(minutes=5)
            expiry_timestamp = int(expiry_time.timestamp())
            formatted_date = datetime.strptime(check_in_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            ymd_format = datetime.strptime(check_in_date, '%Y-%m-%d').strftime('%Y年%m月%d日')
            self.check_reserves[UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.key] = formatted_date
            self.table.put_item(
                Item={
                    'unique_code': unique_code,
                    'line_id': user_id,
                    'ExpirationTime' :expiry_timestamp,
                    UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.key: formatted_date
                }
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
            formatted_date = datetime.strptime(checkout_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            ymd_format = datetime.strptime(checkout_date, '%Y-%m-%d').strftime('%Y年%m月%d日')

            self.check_reserves[UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.key] = formatted_date
            self.table.update_item(
                Key={'unique_code': unique_code},
                UpdateExpression="SET #co = :cd",
                ExpressionAttributeNames={'#co': UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.key},
                ExpressionAttributeValues={':cd': formatted_date}
            )
            message = textwrap.dedent(f'チェックイン日は{checkin_date}、宿泊数は {stay_length}泊、チェックアウト日は {ymd_format}になります。 {self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name]}').strip()
            return message, next_status.name
        else:
            return self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name + '_ERROR'], UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name


    def _handle_update_reservation_confirm(self, user_message, next_status, user_id ,unique_code):
        reserve_confirm = user_message
        system_content = generate_reserve_confirm()
        reserve_confirm = self.get_chatgpt_response(system_content, user_message)
        if reserve_confirm == "True":
            table_datas = self.table.get_item(
                Key={
                    'unique_code': unique_code
                }
            )
            reserve_datas = table_datas['Item']
            message_template = self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name]
            message = message_template.format(**reserve_datas)
            return message, next_status.name
        else:
            self.table.delete_item(
                Key={
                    'unique_code': unique_code
                }
            )
            return self.messages[UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name + "_ERROR"], ReservationStatus.RESERVATION_MENU.name





    def _calculate_checkout_date(self, checkin_date, stay_length):
        return (datetime.strptime(checkin_date, '%Y-%m-%d') + timedelta(days=int(stay_length))).strftime('%Y-%m-%d')

    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(self.api_key, 'gpt-3.5-turbo', 0, system_content, user_message)

