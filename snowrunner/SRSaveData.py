import json
from os import path

from twitchAPI.chat import ChatMessage
from userpaths import get_my_documents

from config import Config


async def post_money(msg: ChatMessage):
    money = get_current_money()
    await msg.chat.send_message(msg.room, f"Current cash: {money[1]}")


def get_current_money() -> tuple:
    return get_value(["CompleteSave1", "SslValue", "persistentProfileData", "money"])


def get_value(keys: list[str]) -> tuple | None:
    with open(get_game_directory(), "r") as save:
        saveData: dict = json.loads(save.readline()[:-1])
    for key in keys:
        matching_key = next((k for k in saveData.keys() if k.lower() == key.lower()), None)
        if matching_key:
            saveData = saveData[matching_key]
            value = (matching_key, saveData)
        else:
            return None
    return value


def get_game_directory() -> str:
    docs_path = Config.get_configs()["SNOWRUNNER_SAVE_DIRECTORY"]
    save_name = Config.get_configs()["SNOWRUNNER_SAVE_NAME"]
    return path.abspath(path.join(get_my_documents(), docs_path, save_name))


async def post_save_data(msg: ChatMessage):
    path = msg.text.lower().removeprefix("!srsave ").replace(" ", "").split(",")
    value = get_value(path)
    if value:
        await msg.reply(f"The value of {value[0]} is: {value[1]}")
    else:
        await msg.reply(f"Sorry, wasn't able to find a value.")
