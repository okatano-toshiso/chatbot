# message.py
import textwrap
from menu_items import MenuItem
from reservation_status import (
    ReservationStatus,
    CheckReservationStatus,
    UpdateReservationStatus,
    InquiryReservationStatus,
    GourmetReservationStatus,
    TourismReservationStatus,
    GuestReservationStatus,
    ErrorReservationStatus,
)

MESSAGES = {
    ReservationStatus.RESERVATION_MENU.name: textwrap.dedent(f"""
        ご連絡ありがとうございます。こちら〇〇ホテルAI予約応答サービスになります。
        {MenuItem.NEW_RESERVATION.value}、{MenuItem.CONFIRM_RESERVATION.value}、{MenuItem.MODIFY_RESERVATION.value}(キャンセル)、{MenuItem.FAQ.value}、{MenuItem.GOURMET.value}、{MenuItem.TOURISM.value}、{MenuItem.GUEST.value}といったご用件を受けたまっております。
        ご用件をおっしゃってください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_START.name: textwrap.dedent("""
        新規の宿泊予約についてのお問い合わせですね。
        予約のためにチェックインと泊数、利用者人数、部屋タイプ、代表者様のお名前、当日連絡可能の電話番号についてお聞かせください。
        まずは何からお聞かせいただけますか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name +  "_CHECKIN": textwrap.dedent("""
        チェックインとチェックアウトについてのご回答ですね。チェックイン日付についてお答えください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_COUNT_OF_PERSON": textwrap.dedent("""
        ご利用者人数についてのご回答ですね。ご利用者人数は何名様になりますか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_ROOM_TYPE": textwrap.dedent("""
        部屋タイプについてのご回答ですね。禁煙をご希望ですか？喫煙をご希望ですか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_NAME": textwrap.dedent("""
        代表者氏名についてのご回答ですね。お名前を教えてください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_PHONE_NUMBER": textwrap.dedent("""
        当日の連絡先についてのご回答ですね。連絡可能の電話番号を教えてください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_JUDGE_INTENT.name + "_ERROR": textwrap.dedent("""
        申し訳ございません。うまく聞き取れませんでしたのでもう一度お願いいたします。
    """).strip(),


    ReservationStatus.NEW_RESERVATION_CHECKIN.name: textwrap.dedent("""
        がチェックインする日ですね。教えていただきありがとうございます。ご利用泊数を教えてください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKIN.name + "_ERROR": textwrap.dedent("""
        チェックインする日がうまく聞き取れませんでした。恐れ入りますが、もう一度、何月何日など具体的な日付で教えてください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKOUT.name: textwrap.dedent("""
        宿泊日数をおしえていただきありがとうございます。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKOUT.name + "_ERROR": textwrap.dedent("""
        宿泊日数がうまく聞き取れませんでした。一泊や三日など、または数値のみでよろしいので、もう一度、教えていただいてもよろしいでしょうか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name: textwrap.dedent("""
        宿泊者数をおしえていただきありがとうございます。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name
    + "_OVER": textwrap.dedent("""
        申し訳ございません。ご利用者人数の上限は1部屋につき2名様までとなっております。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name
    + "_ERROR": textwrap.dedent("""
        ご利用者人数を聞き取れませんでした。人数または夫婦で、夫婦と子供一人、両親となど一緒に行く人の続柄をおっしゃってください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_SMOKER.name: textwrap.dedent("""
        つづいて部屋タイプを選んでください。
        幅140～150cmのベッドを用意したシングル(S)、ダブルサイズのベッドを用意したエコノミーダブル(WA),クイーンサイズのベッドを用意したダブル(W)のご用意があります。
        ご希望の部屋タイプをお申し付けください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_NO_SMOKER.name: textwrap.dedent("""
        つづいて部屋タイプを選んでください。
        幅140～150cmのベッドを用意したシングル(SK)、ダブルサイズのベッドを用意したエコノミーダブル(WAK),クイーンサイズのベッドを用意したダブル(WK)のご用意があります。
        ご希望の部屋タイプをお申し付けください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_SMOKER.name + "_ERROR": textwrap.dedent("""
        恐れ入りますが、喫煙、禁煙のどちらかのご希望をおっしゃってください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name: textwrap.dedent("""
        ご希望の部屋タイプを教えていただきありがとうございます。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name + "_ERROR": textwrap.dedent("""
        恐れ入りますが、ご提案した部屋タイプの中からおっしゃってください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_NAME.name: textwrap.dedent("""
        代表者様のお名前を教えていただきありがとうございます。
        確認のためお伺いしますが、代表者様はご成年でしょうか？未成年の方は宿泊の代表者として登録いただけないため、成人されているかどうかの確認をお願いしております。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_NAME.name + "_ERROR": textwrap.dedent("""
        代表者様のお名前を教えていただいてもよろしいでしょうか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_NAME_KANA.name + "_ERROR": textwrap.dedent("""
        申し訳ございません。お名前の読みがわかりませんでした。再度、ご入力をお願いいたします。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ADULT.name: textwrap.dedent("""
        ありがとうございます。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ADULT.name + "_ERROR": textwrap.dedent("""
        代表者様が未成年かどうか判断できませんでした。恐れ入りますが、未成年かどうか教えていただけますでしょうか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ADULT.name + "_ERROR_CHILD": textwrap.dedent("""
        申し訳ございませんが、未成年の方はご宿泊の代表者としてのご予約をお受けできかねます。成人の方が代表者としてご予約いただくようお願い申し上げます。ご理解のほどよろしくお願いいたします。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name: textwrap.dedent("""
        当日ご連絡が可能な電話番号をお伺いしました。ありがとうございます。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name + "_ERROR": textwrap.dedent("""
        お伝えいただいた電話番号が有効ではないようです。恐れ入りますが、ハイフンなしの10桁または11桁の数字のみで、当日ご連絡が可能な電話番号をお教えいただけますか？
    """).strip(),
    # このタイミングで空き室検索APIを実施(return bool)。 空き室がある場合は下記メッセージを表示する。
    ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name: textwrap.dedent("""
        それでは、予約内容を確認させていただきますね。代表者様のお名前は{name}様、チェックインが{check_in}、チェックアウトが{check_out}、ご宿泊人数は{count_of_person}名様、部屋タイプは{room_type}、ご連絡先は{phone_number}でお間違いないでしょうか。予約内容に問題がなければ、このまま予約を進めてもよろしいでしょうか。修正したい場合は、『修正したい』とお伝えいただき、変更したい項目を教えてください。予約をしない場合は『いいえ』とお答えください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
    + "_REFUSE": textwrap.dedent("""
        かしこまりました。ご予約の確認は不要とのこと、承知いたしました。もしご不明な点や追加のご要望がございましたら、どうぞお気軽にお知らせくださいませ。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、いただいたご回答がご予約確認とは異なるようです。予約内容の確認をさせていただいてもよろしいでしょうか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
    + "_MODIFY": textwrap.dedent("""
        かしこましました。変更したい予約の項目をお教えください。チェックインと泊数、利用者人数、部屋タイプ、代表者様のお名前、当日連絡可能の電話番号のどれを変更されますでしょうか？
    """).strip(),


    ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name: textwrap.dedent("""
        ご予約ありがとうございます。お客様のご予約が無事に完了いたしました。「 {} 」が予約番号になりますので、控えとしてメモなどにお書き留めくださいませ。今後ご不明点や変更がございましたら、いつでもお気軽にお問い合わせください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name
    + "_REFUSE": textwrap.dedent("""
        承知いたしました。ご予約の手続きは中断させていただきました。もしまた機会がございましたら、いつでもご連絡をお待ちしております。ありがとうございました。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、いただいたご回答がご予約を進めるかどうかとは異なるようです。予約をしてもよろしいでしょうか？
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_START.name: textwrap.dedent("""
        {title}ですね。予約時にご登録いただいた代表者様のお名前をお教えください。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_NAME.name: textwrap.dedent("""
        代表者様のお名前を確認いたしました。予約時にご登録いただいた連絡先をお伺いしたいので、代表者様の電話番号を教えてください。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_NAME.name + "_ERROR": textwrap.dedent("""
        お伝えいただいた代表者様のお名前が登録情報と一致しないようです。お手数ですが、もう一度正しいお名前をお知らせいただけますか？
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name: textwrap.dedent("""
        ご予約時にいただいた電話番号が確認できました。引き続き、予約内容の確認を行ってよろしいでしょうか？
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name
    + "_ERROR": textwrap.dedent("""
        お伝えいただいた電話番号が正しくないようです。お手数ですが、もう一度正しい電話番号を教えてください。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name: textwrap.dedent("""
        予約日時は {reservation_date} で、予約番号は {reservation_id_yomi} のご予約です。代表者様のお名前は {name} 様、チェックインは {check_in}、チェックアウトは {check_out}、ご宿泊人数は {count_of_person} 名様、ルームタイプは {room_type}、ご連絡先の電話番号は {phone_number} でございます。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name
    + "_REFUSE": textwrap.dedent("""
        承知いたしました。予約内容の確認は行わずに、そのままにしておきます。もし他にご希望やご質問がございましたら、いつでもお知らせください。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、いただいたご回答がご予約確認とは異なるようです。予約内容の確認をさせていただいてもよろしいでしょうか？
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name
    + "_ERROR_API": textwrap.dedent("""
        お伝えいただいた代表者様のお名前および電話番号に該当する予約が見つかりませんでした。
        恐れ入りますが、もう一度正しい情報をご確認いただき、再度お試しください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name: textwrap.dedent("""
        変更をご希望される項目をおっしゃってください。変更できる項目は、チェックイン日と宿泊数、利用者人数、部屋タイプ、代表者様の情報、連絡先、もしくはキャンセルとなります。どの項目を変更されたいか、教えてください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name
    + "_SELECT_ERROR": textwrap.dedent("""
        恐れ入りますが、お話しいただいた内容は変更できる項目には該当しないようです。変更をご希望される場合は、チェックイン日と宿泊数、利用者人数、部屋タイプ、代表者様の情報、連絡先、もしくはキャンセルの中から選んでお知らせください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name
    + "_ERROR": textwrap.dedent("""
        有効な予約番号ではありませんでした。再度、予約内容を変更したいお予約番号をお知らせください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name
    + "_REFUSE": textwrap.dedent("""
        かしこまりました。変更やキャンセルのご希望はないとのこと、承知いたしました。引き続き現在のご予約内容で対応させていただきますので、もし今後ご要望がございましたら、いつでもお知らせくださいませ。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name
    + "_RESERVATION_ID_ERROR": textwrap.dedent("""
        申し訳ございません。お伝えいただいた予約番号が正しくないようです。もう一度、正しい予約番号をお知らせいただけますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name
    + "_CHECKIN": textwrap.dedent("""
        {title} の変更ですね。現在のご予約では、チェックイン日は {check_in}、チェックアウト日は {check_out} となっております。チェックイン日をいつに変更されますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name
    + "_COUNT_OF_PERSON": textwrap.dedent("""
        {title} の変更ですね。現在のご予約では、{title} は {count_of_person} 名様です。何名様に変更されますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name
    + "_SMOKER": textwrap.dedent("""
        {title} の変更ですね。現在のご予約では、お部屋タイプは {room_type} となっております。禁煙のお部屋と喫煙のお部屋がございますが、どちらをご希望されますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name + "_NAME": textwrap.dedent("""
        代表者様のお名前の変更ですね。現在のご予約では、代表者様のお名前は {name} 様となっております。新しい代表者様のお名前をお知らせいただけますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name
    + "_PHONE_NUMBER": textwrap.dedent("""
        {title} の変更ですね。現在のご予約では、登録されている電話番号は {phone_number} です。変更後の電話番号をおっしゃってください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_START.name
    + "_CANCEL": textwrap.dedent("""
        {title} ですね。
        予約されている内容をお知らせします。
        予約日時は {reservation_date} で、予約番号は {reservation_id} のご予約です。代表者様のお名前は {name} 様、チェックインは {check_in}、チェックアウトは {check_out}、ご宿泊人数は {count_of_person} 名様、ルームタイプは {room_type}、ご連絡先の電話番号は {phone_number} でございます。
        この予約の{title}で間違いなければ、{title} したい旨をおっしゃってください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name: textwrap.dedent("""
        に変更ですね。に変更ですね。次に、何泊されるかを教えてください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CHECKIN.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、ただいまお伝えいただいた日付を確認できませんでした。もう一度、具体的な日付をお知らせいただけますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name: textwrap.dedent("""
        上記の日程で変更する場合は、変更内容の確認を行います。よろしいでしょうか。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、お伝えいただいた宿泊日数を確認できませんでした。もう一度、具体的な日数を教えてください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name: textwrap.dedent("""
        ご利用者人数の変更を承りました。変更内容を確認いたしますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、もう一度ご利用人数を教えていただけますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name: textwrap.dedent("""
        部屋タイプの変更を承りました。変更内容の確認いたしますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、正しい部屋タイプ名を教えていただけますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_NAME.name: textwrap.dedent("""
        代表者の変更を承りました。続いて、新しい代表者様のご連絡先電話番号をお教えください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_NAME.name + "_ERROR": textwrap.dedent("""
        恐れ入りますが、代表者様のお名前をお伺いしております。正しいお名前をもう一度おっしゃっていただけますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name: textwrap.dedent("""
        当日の連絡用として登録している代表者様の電話番号の変更を承りました。変更内容の確認をいたしますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、ご連絡用の電話番号をお伺いしております。正しい電話番号をもう一度お教えいただけますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name: textwrap.dedent("""
        それでは、予約の変更内容を確認させていただきます。お名前は {name} 様、チェックインは {check_in}、チェックアウトは {check_out}、ご連絡先は {phone_number}、部屋タイプは {room_type}、ご利用者人数は {count_of_person} 名様です。
        この変更内容で問題ございませんでしょうか。
        """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name
    + "_NAME_PHONE": textwrap.dedent("""
        それでは、予約の変更内容を確認させていただきます。お名前は {name} 様から{new_name}様に変更、ご連絡先は {phone_number}から{new_phone_number}に変更となります。
        チェックインは {check_in}、チェックアウトは {check_out}、部屋タイプは {room_type}、ご利用者人数は {count_of_person} 名様です。
        この変更内容で問題ございませんでしょうか。
        """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name
    + "_PHONE": textwrap.dedent("""
        それでは、予約の変更内容を確認させていただきます。ご連絡先は {phone_number}から{new_phone_number}に変更となります。
        お名前は {name} 様、チェックインは {check_in}、チェックアウトは {check_out}、部屋タイプは {room_type}、ご利用者人数は {count_of_person} 名様です。
        この変更内容で問題ございませんでしょうか。
        """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name
    + "_REFUSE": textwrap.dedent("""
        今回のご予約内容の変更は行わず、現状のままにしておきます。もし今後変更やキャンセルのご希望がございましたら、いつでもお気軽にお知らせくださいませ。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、いただいたご回答がご予約確認とは異なるようです。予約内容の確認をさせていただいてもよろしいでしょうか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name: textwrap.dedent("""
        ご予約内容の変更が完了いたしました。なお、予約番号に変更はございません。
        引き続き、他の変更内容や確認事項がございましたらお知らせくださいませ。特にご用件がなければ、これにて対応を終了いたします。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name
    + "_AGAIN": textwrap.dedent("""
        恐れ入りますが、いただいたご回答がご予約実行の確認とは異なるようです。予約内容の反映をさせてもよろしいでしょうか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name
    + "_ERROR": textwrap.dedent("""
        申し訳ございません。ただいまご予約内容の変更が正常に反映されませんでした。お手数ですが、もう一度お試しいただけますでしょうか。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM.name: textwrap.dedent("""
        キャンセルということでお間違いないでしょうか？なお、一度キャンセルされたご予約は、本サービス上では取り消しできませんので、ご了承くださいませ。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM.name
    + "_ERROR": textwrap.dedent("""
        キャンセルを取りやめるということで、承知いたしました。ご予約内容は現状のままとなりますので、引き続き何かございましたらお知らせくださいませ。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM.name
    + "_ELSE": textwrap.dedent("""
        恐れ入りますが、いただいたご回答がキャンセルの確認とは異なるようです。キャンセルをしてもよろしいでしょうか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_EXECUTE.name: textwrap.dedent("""
        ご指定のご予約のキャンセルが完了いたしました。今後、何かご不明点やご要望がございましたら、いつでもお気軽にお知らせくださいませ。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_EXECUTE.name
    + "_ERROR": textwrap.dedent("""
        申し訳ございません。ただいまご指定のご予約のキャンセルが正常に反映されませんでした。お手数ですが、もう一度お試しいただけますでしょうか。
    """).strip(),
    InquiryReservationStatus.INQUIRY_RESERVATION_MENU.name: textwrap.dedent("""
        {title} についてのお問い合わせでよろしいでしょうか。こちらではよくある質問やホテルについてのお問い合わせを教えてください。
    """).strip(),
    GourmetReservationStatus.GOURMET_RESERVATION_MENU.name: textwrap.dedent("""
        ホテル近辺の{title} についてのお問い合わせでよろしいでしょうか。レストラン・飲食店情報をご提供いたします。
    """).strip(),
    GourmetReservationStatus.GOURMET_RESERVATION_MENU.name + "_RAG": textwrap.dedent("""
        ### 目的
        system はホテル近辺の飲食店情報を提供する役割を担っています。
        ユーザーの質問に対して、おすすめの人気レストラン・飲食店・グルメ情をもとに、正確で簡潔な回答を行ってください。
        ### ユーザーの質問とおすすめの人気レストラン・飲食店・グルメ情報
        ーーーーーーーーーーーーーーーーーーー
        - **ユーザーの質問**
            {question}
        ーーーーーーーーーーーーーーーーーーー
        - **おすすめの人気レストラン・飲食店・グルメ情報**
            {context}
        ーーーーーーーーーーーーーーーーーーー
        ### 指示
        - `おすすめの人気レストラン・飲食店・グルメ情報` には、ユーザーの質問に関連する飲食店情報が含まれています。必ず `おすすめの人気レストラン・飲食店・グルメ情報` の内容に基づいて回答してください。
        - ユーザーが「おすすめの店」や「ランキング上位の飲食店」について質問した場合、`おすすめの人気レストラン・飲食店・グルメ情報` に含まれる飲食店のうちランキング上位の店舗を優先して紹介してください。
        - 必ず**おすすめの人気レストラン・飲食店・グルメ情報**の中にある「店舗名：」に続く店名を回答の中に含めてください。なるべく最初に入れてください。
        - 回答には質問に関連する内容のみを含め、追加の情報や推測は行わないでください。
        - **検討外れな質問**（飲食店情報に関係ない質問）が含まれる場合は、「申し訳ございません。お客様の質問に回答できる情報がございませんでした。」と返答してください。
        - 情報が不足している場合でも、`おすすめの人気レストラン・飲食店・グルメ情報` 以外の内容を使わず、わかる範囲で答えるようにしてください。
        - **おすすめの人気レストラン・飲食店・グルメ情報**は人気順に記述されています。上から順におすすめしてください。

        ### 振り分けルール
        - 寿司、天ぷら、刺身、すき焼き、しゃぶしゃぶ、おでん、そば、うどん、焼き鳥、味噌汁は日本料理・和食のジャンルになります。
        - カレー、カリー、カレーライス、カリーライス、タンドリーチキン、ビリヤニ、ビリアニ、ネパール料理、スリランカ料理はインド料理のジャンルになります。
        - トムヤムクン、ガパオライス、パッタイ、グリーンカレー、カオマンガイ、ソムタムはタイ料理のジャンルになります。
        - ピッツァ、パスタ、リゾット、ラザニア、カルボナーラ、ボンゴレビアンコ、ティラミス、ジェラートはイタリア料理のジャンルになります。
        - 麻婆豆腐、餃子、エビチリ、酢豚、青椒肉絲（チンジャオロース）、回鍋肉（ホイコーロー）、小籠包、春巻き、炒飯、担々麺は中華料理のジャンルになります。
        - エスカルゴ、フォアグラ、ラタトゥイユ、ブフ・ブルギニョン、キッシュ、テリーヌ、コンフィ、ブイヤベース、ポトフ、クレームブリュレはフレンチのジャンルになります。

        ### 回答例
        - ユーザーが「近くでおすすめのレストランはありますか？」と質問し、おすすめの人気レストラン・飲食店・グルメ情報にランキング上位の店舗が含まれている場合:
            - 「ホテル近くのおすすめのレストランは、 Aレストランです。」
        - ユーザーが「ホテル周辺で食事ができる場所を教えてください」と質問し、おすすめの人気レストラン・飲食店・グルメ情報に飲食店一覧がある場合:
            - 「ホテル周辺の飲食店として、Dカフェなどがございます。」
        - ユーザーが「現在の為替レートは？」と質問し、飲食店情報に無関係な場合:
            - 「申し訳ございません。お客様の質問に回答できる情報がございませんでした。」
    """).strip(),
    TourismReservationStatus.TOURISM_RESERVATION_MENU.name: textwrap.dedent("""
        ホテル近辺の{title} についてのお問い合わせでよろしいでしょうか。お近くの観光スポットをお知らせします。
    """).strip(),
    TourismReservationStatus.TOURISM_RESERVATION_MENU.name + "_RAG": textwrap.dedent("""
    ### 目的
        system はホテル近辺の観光スポット情報を提供する役割を担っています。ユーザーの質問に対して、ベクトル類似検索によって得られた おすすめの人気観光スポット・観光地・観光施設 をもとに、正確で簡潔な回答を行ってください。
        ### 指示
        - おすすめの人気観光スポット・観光地・観光施設 には、ユーザーの質問に関連する観光スポット情報が含まれています。必ず おすすめの人気観光スポット・観光地・観光施設 の内容に基づいて回答してください。
        - ユーザーが「おすすめの観光スポット」や「ランキング上位のスポット」について質問した場合、おすすめの人気観光スポット・観光地・観光施設 に含まれる観光スポットのうちランキング上位の場所を優先して紹介してください。
        - 必ず観光スポット名を回答の中に含めてください。
        - 回答には質問に関連する内容のみを含め、追加の情報や推測は行わないでください。
        - **検討外れな質問**（観光スポット情報に関係ない質問）が含まれる場合は、「申し訳ございません。お客様の質問に回答できる情報がございませんでした。」と返答してください。
        - 情報が不足している場合でも、おすすめの人気観光スポット・観光地・観光施設 以外の内容を使わず、わかる範囲で答えるようにしてください。

        ### ユーザーの質問とおすすめの人気観光スポット・観光地・観光施設

        - **ユーザーの質問**
            {question}

        - **おすすめの人気観光スポット・観光地・観光施設**
            {context}

        ### 回答例
        - ユーザーが「近くでおすすめの観光スポットはありますか？」と質問し、おすすめの人気観光スポット・観光地・観光施設にランキング上位のスポットが含まれている場合:
            - 「ホテル近くのおすすめの観光スポットは、ランキング上位の Aスポットと Bスポットです。」
        - ユーザーが「人気の観光地は？」「人気の観光スポットは？」「おすすめは？」「おすすめの観光スポットは？」と質問し、おすすめの人気観光スポット・観光地・観光施設にランキング上位のスポットが含まれている場合:
            - 「ホテル近くのおすすめの観光スポットは、ランキング上位の Aスポットと Bスポットです。」
        - ユーザーが「近くでおすすめの観光スポットはありますか？」と質問し、おすすめの人気観光スポット・観光地・観光施設にランキング上位のスポットが含まれている場合:
            - 「ホテル近くのおすすめの観光スポットは、ランキング上位の Aスポットと Bスポットです。」
        - ユーザーが「ホテル周辺で行ける場所を教えてください」と質問し、おすすめの人気観光スポット・観光地・観光施設に観光スポット一覧がある場合:
            - 「ホテル周辺の観光スポットとして、Cスポット、Dスポットなどがございます。」

        - ユーザーが「現在の為替レートは？」と質問し、観光スポット情報に無関係な場合:
            - 「申し訳ございません。お客様の質問に回答できる情報がございませんでした。」

 上記プロンプトで、
「人気の観光地は？」」「おすすめは？」と聞いたら情報がありませんと回答されました。
ランキング順に並んでいるので、おすすめや人気はランキング上位を返すように修正してください。
    """).strip(),
    GuestReservationStatus.GUEST_RESERVATION_MENU.name: textwrap.dedent("""
        ホテルの{title} についてのお問い合わせでよろしいでしょうか。
    """).strip(),
    GuestReservationStatus.GUEST_RESERVATION_MENU.name + "_RAG": textwrap.dedent("""
        ### 目的
        system はホテルの宿泊者情報を提供する役割を担っています。ユーザーの質問に対して、ベクトル類似検索によって得られた `参考情報` をもとに、正確で簡潔な回答を行ってください。

        ### 指示
        - `参考情報` には、ユーザーの質問に関連する宿泊者情報が含まれています。必ず `参考情報` の内容に基づいて回答してください。
        - ユーザーが「宿泊者の情報」や「部屋番号や予約状況」について質問した場合、`参考情報` に含まれる情報のうち、該当する情報を優先して提供してください。
        - 必ず宿泊者氏名や部屋番号など、該当の宿泊者に関連する情報を回答の中に含めてください。
        - 回答には質問に関連する内容のみを含め、追加の情報や推測は行わないでください。
        - **検討外れな質問**（宿泊者情報に関係ない質問）が含まれる場合は、「申し訳ございません。該当する宿泊者情報を見つけることができませんでした。」と返答してください。
        - 情報が不足している場合でも、`参考情報` 以外の内容を使わず、わかる範囲で答えるようにしてください。
        - 口語っぽい口調で回答してください。表やグラフ、箇条書きのような回答は絶対にしないでください。

        ### ユーザーの質問と参考情報

        - **ユーザーの質問**
            {question}

        - **参考情報**
            {context}

        ### 回答例
        - ユーザーが「宿泊者の情報を教えてください」と質問し、参考情報に該当の宿泊者情報が含まれている場合:
            - 「宿泊者情報として、氏名: A様、部屋番号: 302号室、チェックイン日: YYYY/MM/DDです。」

        - ユーザーが「予約状況を確認したい」と質問し、参考情報に予約状況が含まれている場合:
            - 「A様の予約状況として、現在のチェックイン予定日は YYYY/MM/DD です。」

        - ユーザーが「Wi-Fiのパスワードを教えてください」と質問し、宿泊者情報に無関係な場合:
            - 「申し訳ございません。該当する宿泊者情報を見つけることができませんでした。」
    """).strip(),
    ErrorReservationStatus.ERROR_RESERVATION_MENU.name: textwrap.dedent("""
        正しい用件を再度、お申し付けください。
    """).strip(),
    "SEND_RESERVATION_DATA_ERROR": textwrap.dedent("""
        予約登録に失敗いたしました。恐れ入りますが再度、予約の登録をお願いいたします。
    """).strip(),
}
