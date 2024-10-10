# message.py
import textwrap
from menu_items import MenuItem
from reservation_status import (
    ReservationStatus,
    CheckReservationStatus,
    UpdateReservationStatus,
    ErrorReservationStatus,
)

MESSAGES = {
    ReservationStatus.RESERVATION_MENU.name: textwrap.dedent(f"""
        ご連絡ありがとうございます。こちら〇〇ホテルAI予約応答サービスです。
        {MenuItem.NEW_RESERVATION.value}、{MenuItem.CONFIRM_RESERVATION.value}、{MenuItem.MODIFY_RESERVATION.value}、{MenuItem.CANCEL_RESERVATION.value}といったご用件を受けたまっております。
        ご用件をおっしゃってください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_START.name: textwrap.dedent("""
        新規の宿泊予約についてのお問い合わせですね。
        予約のためにいくつかご質問をさせてください。
        チェックインする日はいつのご予定でしょうか。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKIN.name: textwrap.dedent("""
        がチェックインする日ですね。教えていただきありがとうございます。何泊ほどお泊りになる予定でしょうか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKIN.name + "_ERROR": textwrap.dedent("""
        チェックインする日がうまく聞き取れませんでした。恐れ入りますが、もう一度、何月何日など具体的な日付で教えてください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKOUT.name: textwrap.dedent("""
        宿泊日数をおしえていただきありがとうございます。一緒にお泊りをする人がいらっしゃいましたら、人数を教えてください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_CHECKOUT.name + "_ERROR": textwrap.dedent("""
        宿泊日数がうまく聞き取れませんでした。一泊や三日など、または数値のみでよろしいので、もう一度、教えていただいてもよろしいでしょうか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name: textwrap.dedent("""
        宿泊者数をおしえていただきありがとうございます。
        続きましては、お泊りになりたいお部屋を選んでください。まずは禁煙のお部屋と喫煙のお部屋がございますが、どちらをご希望いたしますか？
    """).strip(),
    ReservationStatus.NEW_RESERVATION_COUNT_OF_PERSON.name
    + "_ERROR": textwrap.dedent("""
        ご利用者人数を聞き取れませんでした。人数または夫婦で、夫婦と子供一人、両親となど一緒に行く人の続柄をおっしゃってください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_SMOKER.name: textwrap.dedent("""
        喫煙のお部屋ですね。つづいて部屋タイプを選んでください。
        ダブルサイズのベッドを用意したシングル、ベッド幅が140cm未満のスモールシングル、ダブルサイズのベッドを用意したエコノミーダブル、キングサイズのベッドを用意したキングダブル、標準より幅が少し狭いベッドを二つご用意したエコノミーツインのご用意があります。
        ご希望の部屋タイプをお申し付けください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_NO_SMOKER.name: textwrap.dedent("""
        禁煙のお部屋ですね。つづいて部屋タイプを選んでください。
        ダブルサイズのベッドを用意したシングル、ベッド幅が140cm未満のスモールシングル、ダブルサイズのベッドを用意したエコノミーダブル、キングサイズのベッドを用意したキングダブル、標準より幅が少し狭いベッドを二つご用意したエコノミーツイン、どなたでも便利で快適にホテルを利用していただくために開発されたのがハートフルルームのハートフルシングル、ハートフルツインのご用意がございます。
        ご希望の部屋タイプをお申し付けください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_SMOKER.name + "_ERROR": textwrap.dedent("""
        恐れ入りますが、喫煙、禁煙のどちらかのご希望をおっしゃってください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ROOM_TYPE.name: textwrap.dedent("""
        ご希望の部屋タイプを教えていただきありがとうございます。
        ご予約をするために、宿泊者代表のお名前をお伺いできますでしょうか？
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
        ありがとうございます。続きまして、宿泊代表者様のご連絡先電話番号を教えていただけますか？当日にご連絡する可能性がございますので、確認のためよろしくお願いいたします。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_ADULT.name + "_ERROR": textwrap.dedent("""
        申し訳ございませんが、未成年の方はご宿泊の代表者としてのご予約をお受けできかねます。成人の方が代表者としてご予約いただくようお願い申し上げます。ご理解のほどよろしくお願いいたします。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name: textwrap.dedent("""
        当日ご連絡が可能な電話番号をお伺いしました。これでご予約に必要な情報はすべて揃いましたので、最後に予約内容の確認をさせていただいてもよろしいでしょうか？『はい』または『YES』とお答えいただければと思います。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_PHONE_NUMBER.name + "_ERROR": textwrap.dedent("""
        お伝えいただいた電話番号が有効ではないようです。恐れ入りますが、ハイフンなしの10桁または11桁の数字のみで、当日ご連絡が可能な電話番号をお教えいただけますか？
    """).strip(),
    # このタイミングで空き室検索APIを実施(return bool)。 空き室がある場合は下記メッセージを表示する。
    ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name: textwrap.dedent("""
        それでは、予約内容を確認させていただきますね。代表者様のお名前は{name}様、チェックインが{check_in}、チェックアウトが{check_out}、ご宿泊人数は{count_of_person}名様、部屋タイプは{room_type}、ご連絡先は{phone_number}でお間違いないでしょうか。この内容で空室をお調べいたしますので、少々お待ちくださいませ。問題がなければ『予約』とご返事いただけますと、ご予約を進めさせていただきます。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_CONFIRM.name
    + "_ERROR": textwrap.dedent("""
        かしこまりました。ご予約の確認は不要とのこと、承知いたしました。もしご不明な点や追加のご要望がございましたら、どうぞお気軽にお知らせくださいませ。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name: textwrap.dedent("""
        ご予約ありがとうございます。お客様のご予約が無事に完了いたしました。「 {} 」が予約番号になりますので、控えとしてメモなどにお書き留めくださいませ。今後ご不明点や変更がございましたら、いつでもお気軽にお問い合わせください。
    """).strip(),
    ReservationStatus.NEW_RESERVATION_RESERVE_COMPLETE.name
    + "_ERROR": textwrap.dedent("""
        申し訳ございません。システムの不具合により、予約の登録ができませんでした。お手数ですが、もう一度ご予約のお申し込みをお願いいたします。ご迷惑をおかけして大変申し訳ございませんが、何かご不明点やご質問がございましたら、どうぞお気軽にお知らせくださいませ。
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
        予約時の代表者様の電話番号を確認いたしました。お伝えいただいた内容について確認をご希望の場合は、『確認したい』とお伝えください。もし確認や予約を行わない場合は、その旨をお知らせください。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_PHONE_NUMBER.name
    + "_ERROR": textwrap.dedent("""
        お伝えいただいた電話番号が正しくないようです。お手数ですが、もう一度正しい電話番号を教えてください。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name: textwrap.dedent("""
        予約日時は {reservation_date} で、予約番号は {reservation_id} のご予約です。代表者様のお名前は {name} 様、チェックインは {check_in}、チェックアウトは {check_out}、ご宿泊人数は {count_of_person} 名様、ルームタイプは {room_type}、ご連絡先の電話番号は {phone_number} でございます。
    """).strip(),
    CheckReservationStatus.CHECK_RESERVATION_GET_NUMBER.name
    + "_ERROR": textwrap.dedent("""
        承知いたしました。予約内容の確認は行わずに、そのままにしておきます。もし他にご希望やご質問がございましたら、いつでもお知らせください。
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
        上記の日程で変更する場合は、変更内容の確認を行いますので、『確認したい』とお伝えください。もし確認や予約の変更を行わない場合は、その旨をお知らせください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CHECKOUT.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、お伝えいただいた宿泊日数を確認できませんでした。もう一度、具体的な日数を教えてください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name: textwrap.dedent("""
        ご利用者人数の変更を承りました。変更内容を確認したい場合は、『確認したい』とお知らせください。もし確認や予約の変更を行わない場合は、その旨をお伝えください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_COUNT_OF_PERSON.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、もう一度ご利用人数を教えていただけますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_ROOM_TYPE.name: textwrap.dedent("""
        部屋タイプの変更を承りました。変更内容の確認をご希望でしたら、『確認したい』とお伝えください。もし確認や予約の変更を行わない場合は、その旨をお知らせください。
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
        当日の連絡用として登録している代表者様の電話番号の変更を承りました。変更内容の確認をご希望の場合は、『確認したい』とお伝えください。もし確認や予約の変更を行わない場合は、その旨をお知らせください。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_PHONE_NUMBER.name
    + "_ERROR": textwrap.dedent("""
        恐れ入りますが、ご連絡用の電話番号をお伺いしております。正しい電話番号をもう一度お教えいただけますか？
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name: textwrap.dedent("""
        それでは、予約の変更内容を確認させていただきます。お名前は {name} 様、チェックインは {check_in}、チェックアウトは {check_out}、ご連絡先は {phone_number}、部屋タイプは {room_type}、ご利用者人数は {count_of_person} 名様です。
        この変更内容で問題がなければ、必ず『変更』とだけお知らせください。
        """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name
    + "_NAME_PHONE": textwrap.dedent("""
        それでは、予約の変更内容を確認させていただきます。お名前は {name} 様から{new_name}様に変更、ご連絡先は {phone_number}から{new_phone_number}に変更となります。
        チェックインは {check_in}、チェックアウトは {check_out}、部屋タイプは {room_type}、ご利用者人数は {count_of_person} 名様です。
        この変更内容で問題がなければ、必ず『変更』とだけお知らせください。
        """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name
    + "_PHONE": textwrap.dedent("""
        それでは、予約の変更内容を確認させていただきます。ご連絡先は {phone_number}から{new_phone_number}に変更となります。
        お名前は {name} 様、チェックインは {check_in}、チェックアウトは {check_out}、部屋タイプは {room_type}、ご利用者人数は {count_of_person} 名様です。
        この変更内容で問題がなければ、必ず『変更』とだけお知らせください。
        """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CONFIRM.name
    + "_ERROR": textwrap.dedent("""
        今回のご予約内容の変更は行わず、現状のままにしておきます。もし今後変更やキャンセルのご希望がございましたら、いつでもお気軽にお知らせくださいませ。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name: textwrap.dedent("""
        ご予約内容の変更が完了いたしました。なお、予約番号に変更はございません。
        引き続き、他の変更内容や確認事項がございましたらお知らせくださいませ。特にご用件がなければ、これにて対応を終了いたします。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_EXECUTE.name
    + "_ERROR": textwrap.dedent("""
        申し訳ございません。ただいまご予約内容の変更が正常に反映されませんでした。お手数ですが、もう一度お試しいただけますでしょうか。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM.name: textwrap.dedent("""
        キャンセルということでお間違いないでしょうか？お手数ですが、改めて『キャンセル』とだけおっしゃってください。なお、一度キャンセルされたご予約は、本サービス上では取り消しできませんので、ご了承くださいませ。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_CONFIRM.name
    + "_ERROR": textwrap.dedent("""
        キャンセルを取りやめるということで、承知いたしました。ご予約内容は現状のままとなりますので、引き続き何かございましたらお知らせくださいませ。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_EXECUTE.name: textwrap.dedent("""
        ご指定のご予約のキャンセルが完了いたしました。今後、何かご不明点やご要望がございましたら、いつでもお気軽にお知らせくださいませ。
    """).strip(),
    UpdateReservationStatus.UPDATE_RESERVATION_CANCEL_EXECUTE.name
    + "_ERROR": textwrap.dedent("""
        申し訳ございません。ただいまご指定のご予約のキャンセルが正常に反映されませんでした。お手数ですが、もう一度お試しいただけますでしょうか。
    """).strip(),
    ErrorReservationStatus.ERROR_RESERVATION_MENU.name: textwrap.dedent("""
        正しい用件を再度、おっちゃってください。
    """).strip(),
}
