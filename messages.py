# message.py
import textwrap

MESSAGES = {
    "reservation_reception_first": textwrap.dedent("""
        日本語で応答してください。
        あなたはホテルの予約受付担当です。
        userは予約に関して､問い合わせをしてきます。
        その問い合わせ内容に合わせて､下記5パターンのどれに属するかを回答して下さい。
        その際の回答は､振り分けられたパターン名のみ回答してください。
        ---
        1.新規宿泊予約
        2.予約確認
        3.予約変更
        4.予約キャンセル
        5.よくある質問
        ---
        予約が目的だと判断したら「新規宿泊予約」
        予約の確認が目的だと思ったら「予約確認」
        予約の変更が目的だと思ったら「予約変更」
        予約のキャンセルが目的だと思ったら「予約キャンセル」
        予約以外の内容が目的だと思ったら「よくある質問」

        また番号でも判別してください。
        1だったら「新規宿泊予約」
        2だったら「予約確認」
        3だったら「予約変更」
        4だったら「予約キャンセル」
        5だったら「よくある質問」

        そのどれにも属さないようなメッセージであれば、何も返さないでください。
    """).strip(),
    "NEW_RESERVATION_CHECKIN": textwrap.dedent("""
        ですね。宿泊開始日（到着日）のご記入ありがとうございます。続きましては、宿泊予定数をお教えください。
    """).strip(),
    "NEW_RESERVATION_CHECKIN_ERROR": textwrap.dedent("""
        正しい宿泊開始日(yyyy-mm-dd)を再度、ご記入してメッセージを送付してください。
    """).strip(),
    "NEW_RESERVATION_CHECKOUT": textwrap.dedent("""\n宿泊予定数のご記入ありがとうございます。\n続きましては、ご利用者人数をお教えください。""").strip(),
    "NEW_RESERVATION_CHECKOUT_ERROR":textwrap.dedent("""
        正しいを宿泊予定数を再度、数値のみでご記入してメッセージを送付してください。
    """).strip(),
    "NEW_RESERVATION_COUNT_OF_PERSON":textwrap.dedent("""
        人ですね。ご利用者人数のご記入ありがとうございます。続きましては、部屋は禁煙と喫煙、どちらがよろしいでしょうか？
    """).strip(),
    "NEW_RESERVATION_COUNT_OF_PERSON_ERROR":textwrap.dedent("""
        ご利用者人数を再度、数値のみでご記入してメッセージを送付してください。
    """).strip(),
    "NEW_RESERVATION_SMOKER":textwrap.dedent("""ですね。
        続きましては、希望する部屋タイプを選んでください。
        部屋タイプは下記から選んでください。

        シングル(S)
        シングルA(SA)
        スモールシングルA(XS)
        エコノミーダブル(WA)
        キングダブル(QW)
        エコノミーツイン(ET)
    """).strip(),
    "NEW_RESERVATION_NO_SMOKER":textwrap.dedent("""ですね。
        続きましては、希望する部屋タイプを選んでください。
        部屋タイプは下記から選んでください。

        シングル(SK)
        シングルA(SAK)
        スモールシングルA(XSK)
        エコノミーダブル(WAK)
        キングダブル(QWK)
        エコノミーツイン(ETK)
        ハートフルツイン(HTK)
        ハートフルシングル(HSK)
    """).strip(),
    "NEW_RESERVATION_SMOKER_ERROR":textwrap.dedent("""
        喫煙、禁煙のどちらかをお答えください。
    """).strip(),
    "NEW_RESERVATION_ROOM_TYPE":textwrap.dedent("""ですね。
        部屋タイプのご記入ありがとうございます。
        続きましては、代表者の氏名を教えてください。
    """).strip(),
    "NEW_RESERVATION_ROOM_TYPE_ERROR":textwrap.dedent("""
        正しい部屋タイプ名を記入してメッセージを送信してください。
    """).strip(),

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

        シングル(SK)
        シングルA(SAK)
        スモールシングルA(XSK)
        エコノミーダブル(WAK)
        キングダブル(QWK)
        エコノミーツイン(ETK)
        ハートフルツイン(HTK)
        ハートフルシングル(HSK)
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
