from openai import OpenAI

def get_chatgpt_response(api_key, model, temperature, system_content, user_message):
    OPENAI_API_KEY = api_key
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )

    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content

