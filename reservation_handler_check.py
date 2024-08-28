import os, textwrap
from datetime import datetime, timedelta
from reservation_status import CheckReservationStatus
from google.cloud import firestore, storage
from chatgpt_api import get_chatgpt_response
from generate import (
    generate_reserve_number
)
from validation import (
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
        self.reserves = {}
        self.temp_data = {}
        self.handlers = {
            CheckReservationStatus.CHECK_RESERVATION_NUMBER: self._handle_check_reservation_number
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
            self.reserves[CheckReservationStatus.CHECK_RESERVATION_NUMBER.key] = reservation_number
            self.db_ref.set({CheckReservationStatus.CHECK_RESERVATION_NUMBER.key: reservation_number})
            message = f'{reservation_number} {self.messages[CheckReservationStatus.CHECK_RESERVATION_NUMBER.name]}'
            return message, next_status.name
        else:
            return self.messages['NEW_RESERVATION_CHECKIN_ERROR'], CheckReservationStatus.CHECK_RESERVATION_NUMBER.name


    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(self.api_key, 'gpt-3.5-turbo', 0, system_content, user_message)

