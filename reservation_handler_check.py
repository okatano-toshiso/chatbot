import os, textwrap
from datetime import datetime, timedelta
from reservation_status import ReservationStatus, CheckReservationStatus
from google.cloud import firestore, storage
from chatgpt_api import get_chatgpt_response
from generate import (
    generate_reserve_number
)
from validation import (
    is_valid_phone_number,
    is_valid_reserve_number
)
import requests

reserves = {}
users = {}
db = firestore.Client()

class ReservationCheckHandler:

    def __init__(self, db_ref, api_key, messages):
        self.db_ref = db_ref
        self.api_key = os.environ['OPENAI_API_KEY']
        self.access_token = os.environ['ACCESS_TOKEN']
        self.messages = messages
        self.check_reserves = {}
        self.temp_data = {}
        self.handlers = {
            CheckReservationStatus.CHECK_RESERVATION_NUMBER: self._handle_check_reservation_number,
            CheckReservationStatus.CHECK_RESERVATION_NAME: self._handle_check_reservation_name,
            CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER: self._handle_check_reservation_phone_number,
            CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER: self._handle_check_reservation_get_number
        }


    def handle_reservation_step(self, status, user_message, next_status, user_id=None):
        if status in self.handlers:
            return self.handlers[status](user_message, next_status, user_id=user_id)
        else:
            raise ValueError(f'Unsupported reservation status: {status}')


    def _handle_check_reservation_number(self, user_message, next_status, **kwargs):
        system_content = generate_reserve_number()
        reservation_number = self.get_chatgpt_response(system_content, user_message)
        if is_valid_reserve_number(reservation_number):
            self.check_reserves[CheckReservationStatus.CHECK_RESERVATION_NUMBER.key] = reservation_number
            self.db_ref.set({CheckReservationStatus.CHECK_RESERVATION_NUMBER.key: reservation_number}, merge=True)
            message = f'{reservation_number}\n{self.messages[CheckReservationStatus.CHECK_RESERVATION_NUMBER.name]}'
            return message, next_status.name
        else:
            return self.messages[CheckReservationStatus.CHECK_RESERVATION_NUMBER.name + '_ERROR'], CheckReservationStatus.CHECK_RESERVATION_NUMBER.name


    def _handle_check_reservation_name(self, user_message, next_status, **kwargs):
        reservation_name = user_message
        if reservation_name:
            self.check_reserves[CheckReservationStatus.CHECK_RESERVATION_NAME.key] = reservation_name
            self.db_ref.set({CheckReservationStatus.CHECK_RESERVATION_NAME.key: reservation_name}, merge=True)
            message = f'{reservation_name}\n{self.messages[CheckReservationStatus.CHECK_RESERVATION_NAME.name]}'
            return message, next_status.name
        else:
            return self.messages[CheckReservationStatus.CHECK_RESERVATION_NAME.name + '_ERROR'], CheckReservationStatus.CHECK_RESERVATION_NAME.name

    def _handle_check_reservation_phone_number(self, user_message, next_status, **kwargs):
        reservation_phone_number = user_message
        if is_valid_phone_number(reservation_phone_number):
            self.check_reserves[CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.key] = reservation_phone_number
            self.db_ref.set({CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.key: reservation_phone_number}, merge=True)
            message = f'{reservation_phone_number}\n{self.messages[CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name]}'
            return message, next_status.name
        else:
            return self.messages[CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name + '_ERROR'], CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name

    def _handle_check_reservation_get_number(self, user_message, next_status, user_id):
        print(user_id)
        if user_message == '確認':
            data_doc = self.db_ref.get()
            if data_doc.exists:
                datas = data_doc.to_dict()
                print(datas)
                message = str(datas)
            else:
                message = "データが見つかりませんでした。"
            return message, next_status.name
        else:
            return self.messages[CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name + '_ERROR'], ReservationStatus.RESERVATION_MENU.name


    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(self.api_key, 'gpt-3.5-turbo', 0, system_content, user_message)

