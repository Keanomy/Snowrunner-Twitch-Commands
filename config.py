import json
import logging
import logging.config
import sys
from datetime import date
from logging import Logger
from pathlib import Path
from typing import Any


class Config:
    @staticmethod
    def get_config() -> dict:
        global APP_CONFIG
        if APP_CONFIG:
            return APP_CONFIG

        default: dict[str, str | None | dict] = {
            "COMMANDS": {
                "Winch": None,
                "HandBreak": None,
                "Horn": None,
                "Lights": None,
                "Fuel_Roulette": None,
                "Fuel_Roulette_Stats": None,
                "PostMoney": None,
                "GenericSave": None,
                "Timeout_Roulette": None,
            },
            "MOD_ACCOUNT": None,
            "TARGET_CHANNEL": None,
            "USER_COOLDOWN": None,
            "CHANNEL_COOLDOWN": None,
            "SNOWRUNNER_SAVE_DIRECTORY": "My Games/SnowRunner/base/storage/ec216826fe2f4ca4b55d84a631128619",
            "SNOWRUNNER_SAVE_NAME": "CompleteSave.dat",
            "APP_ID": None,
            "APP_SECRET": None,
            "OBS-WEBSOCKET-PASSWORD": None,
        }
        try:
            with open(".config.json", "r") as file:
                APP_CONFIG = json.load(file)
                for item in default:
                    APP_CONFIG.setdefault(item, default[item])
                for item in default["COMMANDS"]:
                    APP_CONFIG["COMMANDS"].setdefault(item, default["COMMANDS"][item])
        except FileNotFoundError:
            APP_CONFIG = default
            print("Loaded default config.")
        return APP_CONFIG

    def save_config() -> None:
        with open(".config.json", "w") as file:
            json.dump(APP_CONFIG, file, indent=4)

    def update_config(key: str, value: Any) -> None:
        global APP_CONFIG
        APP_CONFIG[key] = value
        Config.save_config()

    def setup_logger():

        dir = "./logs/"
        Path.mkdir(Path(f"{dir}/chat_logs/"), exist_ok=True)
        file_handler = logging.FileHandler(
            f"{dir}/chat_logs/{date.today().strftime("%d%m%Y")}.log", encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
        logger: Logger = logging.getLogger("ChatLog")
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.propagate = False
        logging.basicConfig(
            filename=f"{dir}{date.today().strftime("%d%m%Y")}.log",
            encoding="utf-8",
            level=logging.DEBUG,
            datefmt="%m/%d/%y %H:%M:%S",
            format="[%(levelname)s] %(asctime)s | %(name)s - %(message)s",
        )

    def check() -> None:
        if not Config.get_config()["TARGET_CHANNEL"]:
            Config.update_config("TARGET_CHANNEL", input("What CHANNEL should we join?\n"))
        if not Config.get_config()["APP_ID"]:
            Config.update_config("APP_ID", input("Input you APP ID:\n"))
        if not Config.get_config()["APP_ID"]:
            Config.update_config("APP_SECRET", input("Input you APP SECRET:\n"))

    def command_is_active(str) -> bool:
        APP_CONFIG = Config.get_config()
        return APP_CONFIG["COMMANDS"][str]

    def get_config_key(key: str) -> Any:
        APP_CONFIG = Config.get_config()
        return APP_CONFIG[key]


APP_CONFIG: dict[str, str | dict] = None
