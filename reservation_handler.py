import os, textwrap
from datetime import datetime, timedelta
from reservation_status import ReservationStatus
from chatgpt_api import get_chatgpt_response
from generate import (
    generate_index,
    generate_start_date,
    generate_stay,
    generate_number,
    generate_smoker,
    generate_room_type_smoker,
    generate_room_type_no_smoker,
    generate_select,
)
from validation import (
    is_valid_date,
    is_single_digit_number,
    is_valid_smoker,
    is_valid_phone_number,
    is_valid_room_type_smoker,
    is_valid_room_type_no_smoker
)


class ReservationHandler:


    def __init__(self, db_ref, api_key, messages):
        self.db_ref = db_ref
        self.api_key = os.environ["OPENAI_API_KEY"]
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
            # 他のステータスとメソッドをここに追加NEW_RESERVATION_ROOM_TYPE_NO_SMOKER
        }


    def handle_reservation_step(self, status, user_message, next_status):
        if status in self.handlers:
            return self.handlers[status](user_message, next_status)
        else:
            raise ValueError(f"Unsupported reservation status: {status}")


    def _handle_checkin(self, user_message, next_status):
        system_content = generate_start_date()
        check_in_date = self.get_chatgpt_response(system_content, user_message)

        if is_valid_date(check_in_date):
            formatted_date = datetime.strptime(check_in_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            self.reserves[ReservationStatus.NEW_RESERVATION_CHECKIN.key] = formatted_date
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_CHECKIN.key: formatted_date})
            message = f"{formatted_date} {self.messages[ReservationStatus.NEW_RESERVATION_CHECKIN.name]}"
            return message, next_status.name
        else:
            return self.messages["NEW_RESERVATION_CHECKIN_ERROR"], ReservationStatus.NEW_RESERVATION_CHECKIN.name


    def _handle_checkout(self, user_message, next_status):
        system_content = generate_stay()
        stay_length = self.get_chatgpt_response(system_content, user_message)
        reserves_doc = self.db_ref.get()
        reserve_datas = reserves_doc.to_dict()
        checkin_date = reserve_datas.get(ReservationStatus.NEW_RESERVATION_CHECKIN.key)

        if checkin_date and is_single_digit_number(stay_length):
            checkout_date = self._calculate_checkout_date(checkin_date, stay_length)
            self.reserves[ReservationStatus.NEW_RESERVATION_CHECKOUT.key] = checkout_date
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_CHECKOUT.key: checkout_date}, merge=True)
            message = textwrap.dedent(f"宿泊数は {stay_length}泊、チェックアウト日は {checkout_date}になります。 {self.messages[ReservationStatus.NEW_RESERVATION_CHECKOUT.name]}").strip()
            return message, next_status.name
        else:
            return self.messages["NEW_RESERVATION_CHECKOUT_ERROR"], ReservationStatus.NEW_RESERVATION_CHECKOUT.name


    def _handle_count_of_person(self, user_message, next_status):
        system_content = generate_number()
        count_of_person = self.get_chatgpt_response(system_content, user_message)

        if is_single_digit_number(count_of_person):
            self.reserves[ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.key] = count_of_person
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.key: count_of_person}, merge=True)
            message = textwrap.dedent(f"利用者人数は {count_of_person}  {self.messages[ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name]}").strip()
            return message, next_status.name
        else:
            return self.messages["NEW_RESERVATION_COUNT_OF_PERSON_ERROR"], ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name


    def _handle_smoker(self, user_message, next_status):
        system_content = generate_smoker()
        smoker = self.get_chatgpt_response(system_content, user_message)
        if is_valid_smoker(smoker):
            if smoker == "喫煙":
                message = textwrap.dedent(f"禁煙か喫煙かは {smoker}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_SMOKER.name]}").strip()
                next_status =  ReservationStatus.NEW_RESERVATION_ROOM_TYPE_SMOKER
                return message, next_status.name
            elif smoker == "禁煙":
                message = textwrap.dedent(f"禁煙か喫煙かは {smoker}ですね。{self.messages[ReservationStatus.NEW_RESERVATION_NO_SMOKER.name]}").strip()
                next_status =  ReservationStatus.NEW_RESERVATION_ROOM_TYPE_NO_SMOKER
                return message, next_status.name
        else:
            return self.messages["NEW_RESERVATION_SMOKER_ERROR"], ReservationStatus.NEW_RESERVATION_SMOKER.name


    def _handle_room_type_smoker(self, user_message, next_status):
        system_content = generate_room_type_smoker()
        room_type_smoker = self.get_chatgpt_response(system_content, user_message)

        if is_valid_room_type_smoker(room_type_smoker):
            self.reserves[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key] = room_type_smoker
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key: room_type_smoker}, merge=True)
            message = textwrap.dedent(f"部屋タイプは {room_type_smoker}  {self.messages[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name]}").strip()
            return message, next_status.name
        else:
            return self.messages["NEW_RESERVATION_ROOM_TYPE_ERROR"], ReservationStatus.NEW_RESERVATION_ROOM_TYPE_SMOKER.name

    def _handle_room_type_no_smoker(self, user_message, next_status):
        system_content = generate_room_type_no_smoker()
        room_type_no_smoker = self.get_chatgpt_response(system_content, user_message)

        if is_valid_room_type_no_smoker(room_type_no_smoker):
            self.reserves[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key] = room_type_no_smoker
            self.db_ref.set({ReservationStatus.NEW_RESERVATION_ROOM_TYPE.key: room_type_no_smoker}, merge=True)
            message = textwrap.dedent(f"部屋タイプは {room_type_no_smoker}  {self.messages[ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name]}").strip()
            return message, next_status.name
        else:
            return self.messages["NEW_RESERVATION_ROOM_TYPE_ERROR"], ReservationStatus.NEW_RESERVATION_ROOM_TYPE_NO_SMOKER.name


    def _calculate_checkout_date(self, checkin_date, stay_length):
        return (datetime.strptime(checkin_date, '%Y-%m-%d') + timedelta(days=int(stay_length))).strftime('%Y-%m-%d')


    def get_chatgpt_response(self, system_content, user_message):
        return get_chatgpt_response(self.api_key, "gpt-3.5-turbo", 0, system_content, user_message)
