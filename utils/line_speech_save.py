import boto3

def LineSpeechSave(text, user_id, polly_client, s3_client, bucket_name, voice_id='Mizuki'):
    voice_data = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=voice_id
    )

    file_path = f'/tmp/{user_id}_speech.mp3'

    with open(file_path, 'wb') as file:
        file.write(voice_data['AudioStream'].read())
    s3_key = f'{user_id}_speech.mp3'
    s3_client.upload_file(file_path, bucket_name, s3_key)
    s3_url = f'https://{bucket_name}.s3.ap-northeast-1.amazonaws.com/{s3_key}'
    return s3_url

