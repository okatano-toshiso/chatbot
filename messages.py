# message.py
import textwrap
from menu_items import MenuItem
from reservation_status import ReservationStatus, CheckReservationStatus, UpdateReservationStatus, ErrorReservationStatus

MESSAGES = {
    ReservationStatus.RESERVATION_MENU.name:textwrap.dedent(f"""
        こちら〇〇ホテルAI予約応答サービスです。
        下記ご用件を承っております。
        ----
        1.{MenuItem.NEW_RESERVATION.value}
        2.{MenuItem.CONFIRM_RESERVATION.value}
        3.{MenuItem.MODIFY_RESERVATION.value}
        4.{MenuItem.CANCEL_RESERVATION.value}
        5.{MenuItem.FAQ.value}
        ----
    """).strip(),
    ReservationStatus.NEW_RESERVATION_START.name:textwrap.dedent("""
        新規宿泊予約ありがとうございます。
        予約に必要な情報を得るためにいくつか質問をさせていただきます。
        宿泊開始日（到着日）はいつのご予定でしょうか。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKIN.name:textwrap.dedent("""
        ですね。宿泊開始日（到着日）のご記入ありがとうございます。続きましては、宿泊予定数をお教えください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKIN.name + "_ERROR":textwrap.dedent("""
        恐れ入りますが、入力された日付を確認できませんでした。もう一度、わかりやすい日付や日数を教えてください。例：明日、来週、2024年8月15日など。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKOUT.name:textwrap.dedent("""
        宿泊予定数のご記入ありがとうございます。\n続きましては、ご利用者人数をお教えください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKOUT.name + "_ERROR":textwrap.dedent("""
        正しいを宿泊予定数を再度、数値のみでご記入してメッセージを送付してください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name:textwrap.dedent("""
        ご利用者人数のご記入ありがとうございます。
        続きましては、部屋タイプを選んでください。禁煙のお部屋と喫煙のお部屋がございますが、どちらをご希望でしょうか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name + "_ERROR":textwrap.dedent("""
        ご利用者人数を再度、数値のみでご記入してメッセージを送付してください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_SMOKER.name:textwrap.dedent("""
        続きましては、希望する部屋タイプを選んでください。
        部屋タイプは下記から選んでください。
        -------------------
        ・シングル(S)
        ・シングルA(SA)
        ・スモールシングルA(XS)
        ・エコノミーダブル(WA)
        ・キングダブル(QW)
        ・エコノミーツイン(ET)
        -------------------
    """).strip(),
    ReservationStatus.NEW_RESERVATION_NO_SMOKER.name:textwrap.dedent("""
        続きましては、希望する部屋タイプを選んでください。
        部屋タイプは下記から選んでください。
        -------------------
        ・シングル(SK)
        ・シングルA(SAK)
        ・スモールシングルA(XSK)
        ・エコノミーダブル(WAK)
        ・キングダブル(QWK)
        ・エコノミーツイン(ETK)
        ・ハートフルツイン(HTK)
        ・ハートフルシングル(HSK)
        -------------------
    """).strip(),
    ReservationStatus.NEW_RESERVATION_SMOKER.name + "_ERROR":textwrap.dedent("""
        喫煙、禁煙のどちらかをお答えください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name:textwrap.dedent("""
        部屋タイプのご記入ありがとうございます。
        続きましては、代表者の氏名を日本語で教えてください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name + "_ERROR":textwrap.dedent("""
        正しい部屋タイプ名を記入してメッセージを送信してください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_NAME.name:textwrap.dedent("""
        代表者様氏名のご記入ありがとうございます。
        代表者様は成人されておりますか、それとも未成年でいらっしゃいますか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_NAME.name + "_ERROR":textwrap.dedent("""
        代表者様氏名をご記入してメッセージを送付してください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_NAME_KANA.name + "_ERROR":textwrap.dedent("""
        申し訳ございません。お名前の読みがわかりませんでした。再度、ご入力をお願いいたします。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ADULT.name:textwrap.dedent("""
        ありがとうございます。
        続きましては、宿泊当日に連絡可能な電話番号を教えてください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ADULT.name + "_ERROR":textwrap.dedent("""
        申し訳ございませんが、未成年の方からのご予約はお受けできません。ご理解のほどよろしくお願い申し上げます。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name:textwrap.dedent("""
        当日連絡可能な電話番号を承りました。予約に必要な情報は以上になります。
        予約内容を確認させていただいてもよろしいでしょうか。
        「YES」または「はい」などの許容のメッセージをお願いします。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name + "_ERROR":textwrap.dedent("""
        当日連絡可能な電話番号をハイフンなしの10-11桁の数値のみでメッセージを送信してください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name:textwrap.dedent("""
        それでは、予約内容を確認させていただきます。
        <!-- このタイミングで空き室検索APIを実施(return bool)。 空き室がある場合は下記メッセージを表示する。 -->
        下記が宿泊予約の内容になりますのでご確認ください。\n
        予約内容
        ----------------------------------------
        お名前：{name}
        オナマエ：{name_kana}
        チェックイン：{check_in}
        チェックアウト：{check_out}
        電話番号：{phone_number}
        ルームタイプ：{room_type}
        ご利用者人数：{count_of_person}
        ----------------------------------------
        この予約内容でよろしければ、「予約」と回答してください｡
        予約いたします｡
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name + "_ERROR":textwrap.dedent("""
        かしこまりました。確認は不要とのこと、承知いたしました。ご不明な点や追加のご要望がございましたら、どうぞお気軽にお知らせください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name:textwrap.dedent("""
        ご予約ありがとうございました。お客様の予約を完了しました。これが予約番号になりますので、メモ帳などにお控えしてください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name + "_ERROR":textwrap.dedent("""
        予約登録ができませんでした。お手数ですが、再度、予約のお申し込みをお願いいたします。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_START.name:textwrap.dedent("""
        予約確認ですね。
        予約時に使用した代表者氏名を教えてください。
    """).strip(),
    # CheckReservationStatus.CHECK_RESERVATION_NUMBER.name:textwrap.dedent("""
    #     予約番号を確認しました。
    #     予約時の代表者様氏名を教えてください。
    # """).strip(),
    # CheckReservationStatus.CHECK_RESERVATION_NUMBER.name + "_ERROR":textwrap.dedent("""
    #     正しい予約番号を入力してください。予約番号は半角数字のみになります。
    # """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_NAME.name:textwrap.dedent("""
        予約時の代表者氏名を確認しました。
        代表者様のご連絡先電話番号を教えてください。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_NAME.name + "_ERROR":textwrap.dedent("""
        正しい代表者氏名を入力してください。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name:textwrap.dedent("""
        予約時の代表者の電話番号を確認しました。
        お答えいただいた予約内容を確認する場合には、確認したい旨をお伝えください。
        確認しない、予約しない場合はその旨をお伝えください。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name + "_ERROR":textwrap.dedent("""
        正しい電話番号を入力してください。
    """).strip(),


    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name:textwrap.dedent("""
        ----------------------------------------
        ID : {id}
        予約番号：{reservation_id}
        予約日時：{reservation_date}
        お名前：{name}
        チェックイン：{check_in}
        チェックアウト：{check_out}
        電話番号：{phone_number}
        ルームタイプ：{room_type}
        ご利用者人数：{count_of_person}
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name + "_ERROR":textwrap.dedent("""
        予約内容を確認しないということですね。メニュー画面に戻ります。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name + "_ERROR_API":textwrap.dedent("""
        LINEユーザーとご入力いただいた代表者氏名、電話番号に該当する予約がございませんでした。\n
        恐れ入りますが、再度ご入力いただきましてご確認をお願いいたします。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name:textwrap.dedent("""
        予約の変更をしたい項目を送信してください。
        ----------------------------------------
        1.チェックインと宿泊数
        2.利用者人数
        3.部屋タイプ
        4.代表者氏名
        5.連絡先電話番号
""").strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_SELECT_ERROR":textwrap.dedent("""
        予約変更したい項目がわかりませんでした。再度、変更したい項目を選びなおしてください。
        ----------------------------------------
        1.チェックインと宿泊数
        2.利用者人数
        3.部屋タイプ
        4.代表者氏名
        5.連絡先電話番号
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_ERROR":textwrap.dedent("""
        予約変更をしないと承りました。
        メニュー画面に戻ります。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_RESERVATION_ID_ERROR":textwrap.dedent("""
        有効な予約番号ではございませんでした。
        恐れ入りますが、再度、予約番号を入力しなおしてください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_CHECKIN":textwrap.dedent("""
        ホテルのチェックイン日はいつに変更いたしますか。
        宿泊日は変更しない場合、予約した日付をおっしゃってください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_COUNT_OF_PERSON":textwrap.dedent("""
        ご利用人数を何名様に変更されますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_SMOKER":textwrap.dedent("""
        部屋タイプの変更ですね。禁煙のお部屋と喫煙のお部屋がございますが、どちらをご希望でしょうか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name:textwrap.dedent("""
        に変更ですね。
        次は変更したい宿泊日数を教えてください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name + "_ERROR":textwrap.dedent("""
        恐れ入りますが、入力された日付を確認できませんでした。もう一度、わかりやすい日付や日数を教えてください。例：明日、来週、2024年8月15日など。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name:textwrap.dedent("""
        上記日程で変更する場合には、変更内容を確認したい旨をお伝えください。
        確認しない、予約しない場合はその旨をお伝えください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name + "_ERROR":textwrap.dedent("""
        恐れ入りますが、入力された宿泊日数を確認できませんでした。もう一度、わかりやすい日数を教えてください。例：3、3日、3泊。一週間など。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name:textwrap.dedent("""
        ご利用者変更人数をうけたまわりました。
        変更内容を確認したい旨をお伝えください。
        確認しない、予約しない場合はその旨をお伝えください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name + "_ERROR":textwrap.dedent("""
        恐れ入りますが、ご利用人数をお伺いしております。例：1、一人、夫婦など
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name:textwrap.dedent("""
        部屋タイプの変更をうけたまわりました。
        変更内容を確認したい旨をお伝えください。
        確認しない、予約しない場合はその旨をお伝えください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name + "_ERROR":textwrap.dedent("""
        正しい部屋タイプ名を記入してメッセージを送信してください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name:textwrap.dedent("""
        それでは、予約内容を確認させていただきます。
        <!-- このタイミングで空き室検索APIを実施(return bool)。 空き室がある場合は下記メッセージを表示する。 -->
        下記が宿泊予約の内容になりますのでご確認ください。\n
        予約内容
        ----------------------------------------
        お名前：{name}
        チェックイン：{check_in}
        チェックアウト：{check_out}
        電話番号：{phone_number}
        ルームタイプ：{room_type}
        ご利用者人数：{count_of_person}
        ----------------------------------------
        この予約内容でよろしければ、「変更」と回答してください｡
        """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name + "_ERROR":textwrap.dedent("""
        予約変更をしないと承りました。
        メニュー画面に戻ります。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name:textwrap.dedent("""
        ご予約内容の変更手続きが完了いたしました。変更処理をいたしました予約番号をお伝えいたします。その他にご不明点やご要望がございましたら、どうぞお申し付けください。
        メニュー画面に戻ります。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name + "_ERROR":textwrap.dedent("""
        申し訳ございません。ただいまご予約内容の変更がうまく反映されませんでした。恐れ入りますが、もう一度お試しいただけますでしょうか。
    """).strip(),
    ErrorReservationStatus.ERROR_RESERVATION_MENU.name:textwrap.dedent("""
        正しい用件を再度、ご記入してメッセージを送付してください。
    """).strip()
}


PAST_MESSAGES = {
    "reservation_reception_start": textwrap.dedent("""
        新規宿泊予約ありがとうございます。
        予約に必要な情報を得るためにいくつか質問をさせていただきます。
        宿泊開始日（到着日）はいつのご予定でしょうか。
    """).strip(),
    "reservation_reception_check": textwrap.dedent("""
        予約確認ですね。
        予約時に控えていただきました予約番号のみを入力してください。
    """).strip(),
    "reservation_reception_updata": textwrap.dedent("""
        予約変更ですね。\n予約時に控えていただきました予約番号のみを入力してください。
    """).strip(),
    "reservation_reception_error": textwrap.dedent("""
        正しい用件を再度、ご記入してメッセージを送付してください。
    """).strip(),
    "reservation_reception_stay": textwrap.dedent("""
        ですね。宿泊開始日（到着日）のご記入ありがとうございます。続きましては、宿泊予定数をお教えください。
    """).strip(),
    "reservation_reception_stay_error": textwrap.dedent("""
        正しい宿泊開始日(yyyy-mm-dd)を再度、ご記入してメッセージを送付してください。
    """).strip(),
    "reservation_reception_number": textwrap.dedent("""泊ですね。\n宿泊予定数のご記入ありがとうございます。\n続きましては、ご利用者人数をお教えください。""").strip(),
    "reservation_reception_number_error":textwrap.dedent("""
        正しいを宿泊予定数を再度、数値のみでご記入してメッセージを送付してください。
    """).strip(),
    "reservation_reception_smoking":textwrap.dedent("""人ですね。
        ご利用者人数のご記入ありがとうございます。
        続きましては、部屋は禁煙と喫煙、どちらがよろしいでしょうか？
    """).strip(),
    "reservation_reception_smoking_error":textwrap.dedent("""
        ご利用者人数を再度、数値のみでご記入してメッセージを送付してください。
    """).strip(),
    "reservation_reception_room":textwrap.dedent("""ですね。
        続きましては、希望する部屋タイプを選んでください。
        部屋タイプは下記から選んでください。
        ----------
        ・シングル(SK)
        ・シングルA(SAK)
        ・スモールシングルA(XSK)
        ・エコノミーダブル(WAK)
        ・キングダブル(QWK)
        ・エコノミーツイン(ETK)
        ・ハートフルツイン(HTK)
        ・ハートフルシングル(HSK)
        ----------

    """).strip(),
    "reservation_reception_room_smoke":textwrap.dedent("""ですね。
        続きましては、希望する部屋タイプを選んでください。
        部屋タイプは下記から選んでください。

        シングル(S)
        シングルA(SA)
        スモールシングルA(XS)
        エコノミーダブル(WA)
        キングダブル(QW)
        エコノミーツイン(ET)
    """).strip(),
    "reservation_reception_room_error":textwrap.dedent("""
        喫煙、禁煙のどちらかをお答えください。
    """).strip(),
    "reservation_reception_name":textwrap.dedent("""ですね。
        部屋タイプのご記入ありがとうございます。
        続きましては、代表者の氏名を教えてください。
    """).strip(),
    "reservation_reception_name_error":textwrap.dedent("""
        正しい部屋タイプ名を記入してメッセージを送信してください。
    """).strip(),
    "reservation_reception_tell":textwrap.dedent("""
        代表者様氏名のご記入ありがとうございます。
        続きましては、宿泊当日に連絡可能の電話番号を教えてください
    """).strip(),
    "reservation_reception_tell_error":textwrap.dedent("""
        代表者様氏名をご記入してメッセージを送付してください。
    """).strip(),
    "reservation_reception_confirm_error":textwrap.dedent("""
        当日連絡可能な電話番号をハイフンなしの10-11桁の数値のみでメッセージを送信してください。
    """).strip(),
    "reservation_reception_search_error":textwrap.dedent("""
        今回の条件で検索しない場合は、再度お問い合わせしなおしてください。
    """).strip(),
    "reservation_reception_complete_error":textwrap.dedent("""
        今回の条件で予約しない場合は、再度お問い合わせしなおしてください。
    """).strip(),
    "reservation_reception_check_result":textwrap.dedent("""
        お客様の予約番号は下記内容になります。
        宿泊開始日：予約番号の検索結果
        宿泊数：予約番号の検索結果
        利用者人数：予約番号の検索結果
        部屋タイプ：予約番号の検索結果
        代表者氏名：予約番号の検索結果
        電話番号：予約番号の検索結果
        予約APIで検索結果を表示させます。予約できればTrue、なんらかのエラーで予約できなければFalseを返します。
        上記予約内容で変更したい場合は「予約変更」とメッセージ送付してください。
    """).strip(),
    "reservation_reception_cancel":textwrap.dedent("""
        予約のキャンセルですね。
        予約時に控えていただきました予約番号のみを入力してください。
    """).strip(),
    "reservation_number_error":textwrap.dedent("""
        有効な予約番号を再度ご入力ください｡
    """).strip()
}
