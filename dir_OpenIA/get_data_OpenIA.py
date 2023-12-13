import openai
import configparser
config = configparser.ConfigParser()
config.read("dir_bot/config.ini")

openai.api_key = config["TOKEN"]["OpenIA"]


async def get_data(human_last, ia_last, message):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"You: {human_last}\n"
               f"Friend:{ia_last}\n"
               f"You: {message}\n"
               f"Friend:",
        temperature=0.5,
        max_tokens=500,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0,
        stop=["You:"]
    )
    return response['choices'][0]['text']

    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are a virtual companion for learning English, not an artificial intelligence"},
    #         {"role": "user", "content": f"{human_last}"},
    #         {"role": "assistant", "content": f"{ia_last}"},
    #         {"role": "user", "content": f"{message}"},
    #     ],
    # )
    # return response.choices[0].message.content
