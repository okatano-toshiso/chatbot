import os, textwrap
from datetime import datetime, timedelta
from reservation_status import ReservationStatus
from google.cloud import firestore, storage
from chatgpt_api import get_chatgpt_response
from generate import (
    generate_start_date,
    generate_stay,
    generate_number,
    generate_smoker,
    generate_room_type_smoker,
    generate_room_type_no_smoker,
    generate_reserve_confirm,
    generate_judge_adult,
    generate_name,
    generate_name_kana
)
from validation import (
    is_valid_date,
    is_single_digit_number,
    is_valid_smoker,
    is_valid_phone_number,
    is_valid_room_type_smoker,
    is_valid_room_type_no_smoker,
    is_valid_reserve_confirm,
    is_valid_japaneses_character,
    is_valid_japanese_katakana
)
import requests
import uuid

reserves = {}
users = {}
db = firestore.Client()
unique_code = str(uuid.uuid4())

class ReservationHandler:


    def get_new_reserve_id(self):
        token_data = {'token': self.access_token}
        getReserveIdUrl = os.environ['API_SET_RESERVE_ID']
        response = requests.post(getReserveIdUrl, json=token_data)
        if response.status_code == 200:
            latest_reserve_id = response.json().get('latest_reserve_id')
            return int(latest_reserve_id) + 1
        else:
            print('Cannot get the latest reserve ID')
            return None


    def set_line_users_data(self, user_id, datas, current_datetime):
        line_users = {
            'line_id': user_id,
            'token': self.access_token,
            'name': datas['name'],
            'name_kana': datas['name_kana'],
            'adult': datas['adult'],
            'phone_number': datas['phone_number'],
            'created_at': current_datetime,
            'updated_at': current_datetime
        }
        return line_users


    def set_line_reserves_data(self, user_id, datas, new_reserve_id, current_date, current_datetime):
        line_reserves = {
            'token': self.access_token,
            'reservation_date': current_date,
            'reservation_id': new_reserve_id,
            'line_id': user_id,
            'name': datas['name'],
            'phone_number': datas['phone_number'],
            'check_in': datas['check_in'],
            'check_out': datas['check_out'],
            'room_type': datas['room_type'],
            'count_of_person': datas['count_of_person'],
            'status': 'RESERVE',
            'created_at': current_datetime,
            'updated_at': current_datetime
        }
        return  line_reserves

    def send_reservation_data(self, reserve_datas, user_datas):
        data = {
            'line_reserves': [reserve_datas],
            'line_users': [user_datas]
        }
        url = os.environ['API_SAVE_RESERVE_DATA']
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            reservation_id = reserve_datas.get('reservation_id')
            return self.messages[ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name], reservation_id
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return f'Failed to submit reservation: {http_err}', 'ERROR_STATUS'
        except Exception as err:
            print(f'An error occurred: {err}')
            return f'An unexpected error has occurred.: {err}', 'ERROR_STATUS'


    def __init__(self, db_ref, api_key, messages):
        self.db_ref = db_ref
        self.api_key = os.environ['OPENAI_API_KEY']
        self.access_token = os.environ['ACCESS_TOKEN']
        self.messages = messages
        self.reserves = {}
        self.temp_data = {}
        self.handlers = {
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
            ReservationStatus.NEW_RESERVATION_RESERVE_EXECUTE: self._handle_reserve_execute
        }


    def handle_reservation_step(self, status, user_message, next_status, user_id=None):
        if status in self.handlers:
            return self.handlers[status](user_message, next_status, user_id=user_id)
        else:
            raise ValueError(f'Unsupported reservation status: {status}')


    def _handle_checkin(self, user_message, next_status, **kwargs):
        system_content = generate_start_date()
        check_in_date = self.get_chatgpt_response(system_content, user_message)

        if is_valid_date(check_in_date):
            formatted_date = datetime.strptime(check_in_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            self.reserves[ReservationStatus.NEW_RESERVATION_CHECKIN.key] = formatted_date
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_CHECKIN.key: formatted_date})
            message = f'{formatted_date} {self.messages[ReservationStatus.NEW_RESERVATION_CHECKIN.name]}'
            return message, next_status.name
        else:
            return self.messages['NEW_RESERVATION_CHECKIN_ERROR'], ReservationStatus.NEW_RESERVATION_CHECKIN.name


    def _handle_checkout(self, user_message, next_status, **kwargs):
        system_content = generate_stay()
        stay_length = self.get_chatgpt_response(system_content, user_message)
        reserves_doc = self.db_ref.get()
        reserve_datas = reserves_doc.to_dict()
        checkin_date = reserve_datas.get(ReservationStatus.NEW_RESERVATION_CHECKIN.key)

        if checkin_date and is_single_digit_number(stay_length):
            checkout_date = self._calculate_checkout_date(checkin_date, stay_length)
            self.reserves[ReservationStatus.NEW_RESERVATION_CHECKOUT.key] = checkout_date
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_CHECKOUT.key: checkout_date}, merge=True)
            message = textwrap.dedent(f'宿泊数は {stay_length}泊、チェックアウト日は {checkout_date}になります。 {self.messages[ReservationStatus.NEW_RESERVATION_CHECKOUT.name]}').strip()
            return message, next_status.name
        else:
            return self.messages['NEW_RESERVATION_CHECKOUT_ERROR'], ReservationStatus.NEW_RESERVATION_CHECKOUT.name


    def _handle_count_of_person(self, user_message, next_status, **kwargs):
        system_content = generate_number()
        count_of_person = self.get_chatgpt_response(system_content, user_message)

        if is_single_digit_number(count_of_person):
            self.reserves[ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.key] = count_of_person
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.key: count_of_person}, merge=True)
            message = textwrap.dedent(f'利用者人数は {count_of_person} 人ですね。{self.messages[ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name]}').strip()
            return message, next_status.name
        else:
            return self.messages['NEW_RESERVATION_COUNT_OF_PERSON_ERROR'], ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name


    def _handle_smoker(self, user_message, next_status, **kwargs):
        system_content = generate_smoker()
        smoker = self.get_chatgpt_response(system_content, user_message)
        if is_valid_smoker(smoker):
            if smoker == '喫煙':
                message = textwrap.dedent(f'禁煙か喫煙かは {smoker}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_SMOKER.name]}').strip()
                next_status =  ReservationStatus.NEW_RESERVATION_ROOM_TYPE_SMOKER
                return message, next_status.name
            elif smoker == '禁煙':
                message = textwrap.dedent(f'禁煙か喫煙かは {smoker}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_NO_SMOKER.name]}').strip()
                next_status =  ReservationStatus.NEW_RESERVATION_ROOM_TYPE_NO_SMOKER
                return message, next_status.name
        else:
            return self.messages['NEW_RESERVATION_SMOKER_ERROR'], ReservationStatus.NEW_RESERVATION_SMOKER.name


    def _handle_room_type_smoker(self, user_message, next_status, **kwargs):
        system_content = generate_room_type_smoker()
        room_type_smoker = self.get_chatgpt_response(system_content, user_message)

        if is_valid_room_type_smoker(room_type_smoker):
            self.reserves[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key] = room_type_smoker
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key: room_type_smoker}, merge=True)
            message = textwrap.dedent(f'部屋タイプは {room_type_smoker} ですね。 {self.messages[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name]}').strip()
            return message, next_status.name
        else:
            return self.messages['NEW_RESERVATION_ROOM_TYPE_ERROR'], ReservationStatus.NEW_RESERVATION_ROOM_TYPE_SMOKER.name


    def _handle_room_type_no_smoker(self, user_message, next_status, **kwargs):
        system_content = generate_room_type_no_smoker()
        room_type_no_smoker = self.get_chatgpt_response(system_content, user_message)

        if is_valid_room_type_no_smoker(room_type_no_smoker):
            self.reserves[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key] = room_type_no_smoker
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key: room_type_no_smoker}, merge=True)
            message = textwrap.dedent(f'部屋タイプは {room_type_no_smoker}  {self.messages[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name]}').strip()
            return message, next_status.name
        else:
            return self.messages['NEW_RESERVATION_ROOM_TYPE_ERROR'], ReservationStatus.NEW_RESERVATION_ROOM_TYPE_NO_SMOKER.name


    def _handle_name(self, user_message, next_status, **kwargs):
        name = user_message
        # system_content = generate_name()
        # name = self.get_chatgpt_response(system_content, user_message)
        if is_valid_japaneses_character(name):
            self.reserves[ReservationStatus.NEW_RESERVATION_NAME.key] = name
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_NAME.key: name}, merge=True)
            system_content = generate_name_kana()
            name_kana = self.get_chatgpt_response(system_content, name)
            if is_valid_japanese_katakana(name_kana):
                self.reserves[ReservationStatus.NEW_RESERVATION_NAME_KANA.key] = name_kana
                self.db_ref.set({ReservationStatus.NEW_RESERVATION_NAME_KANA.key: name_kana}, merge=True)
            else:
                return self.messages['NEW_RESERVATION_NAME_KANA_ERROR'], ReservationStatus.NEW_RESERVATION_NAME.name
            message = textwrap.dedent(f'代表者氏名は {name} 、読みは{name_kana}でよろしいでしょうか。 {self.messages[ReservationStatus.NEW_RESERVATION_NAME.name]}').strip()
            return message, next_status.name
        else:
            return self.messages['NEW_RESERVATION_NAME_ERROR'], ReservationStatus.NEW_RESERVATION_NAME.name


    def _handle_adult(self, user_message, next_status, **kwargs):
        adult = user_message
        system_content = generate_judge_adult()
        adult = self.get_chatgpt_response(system_content, user_message)
        if adult == "True":
            is_adult = (adult == "True")
            self.reserves[ReservationStatus.NEW_RESERVATION_ADULT.key] = is_adult
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_ADULT.key: is_adult}, merge=True)
            message = textwrap.dedent(f'{self.messages[ReservationStatus.NEW_RESERVATION_ADULT.name]}').strip()
            return message, next_status.name
        else:
            self.db_ref.delete()
            return self.messages['NEW_RESERVATION_ADULT_ERROR'], ReservationStatus.RESERVATION_MENU.name


    def _handle_phone_number(self, user_message, next_status, **kwargs):
        phone_number = user_message
        if is_valid_phone_number(phone_number):
            self.reserves[ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.key] = phone_number
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.key: phone_number}, merge=True)
            message = textwrap.dedent(f'代表者の連絡先は{phone_number}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name]}').strip()
            return message, next_status.name
        else:
            return self.messages['NEW_RESERVATION_PHONE_NUMBER_ERROR'], ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name


    def _handle_reserve_confirm(self, user_message, next_status, **kwargs):
        reserve_confirm = user_message
        system_content = generate_reserve_confirm()
        reserve_confirm = self.get_chatgpt_response(system_content, user_message)
        if is_valid_reserve_confirm(reserve_confirm):
            reserve_doc = self.db_ref.get()
            reserve_datas = reserve_doc.to_dict()
            message_template = self.messages[ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name]
            message = message_template.format(**reserve_datas)
            return message, next_status.name
        else:
            self.db_ref.delete()
            return self.messages['NEW_RESERVATION_RESERVE_CONFIRM_ERROR'], ReservationStatus.RESERVATION_MENU.name


    def _handle_reserve_execute(self, user_message, next_status, user_id):
        if user_message == '予約':
            new_reserve_id = self.get_new_reserve_id()
            if new_reserve_id is None:
                self.db_ref.delete()
                return 'Failed to obtain a reservation number.', ReservationStatus.RESERVATION_MENU.name
            data_doc = self.db_ref.get()
            datas = data_doc.to_dict()
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_datas = self.set_line_users_data(user_id, datas, current_datetime)
            reserve_datas = self.set_line_reserves_data(user_id, datas, new_reserve_id, current_date, current_datetime)
            reservation_message, reservation_id = self.send_reservation_data(reserve_datas, user_datas)
            self.db_ref.delete()
            message = textwrap.dedent(f'{reservation_message}\n{reservation_id}').strip()
            return message, next_status.name
        else:
            self.db_ref.delete()
            return self.messages['NEW_RESERVATION_RESERVE_CONFIRM_ERROR'], ReservationStatus.RESERVATION_MENU.name


    def _calculate_checkout_date(self, checkin_date, stay_length):
        return (datetime.strptime(checkin_date, '%Y-%m-%d') + timedelta(days=int(stay_length))).strftime('%Y-%m-%d')


    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(self.api_key, 'gpt-3.5-turbo', 0, system_content, user_message)

