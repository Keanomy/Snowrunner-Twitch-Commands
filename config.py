import json


class Config:

    def get_configs() -> dict:
        global APP_CONFIG
        if APP_CONFIG:
            return APP_CONFIG

        default: dict[str, str | None | dict] = {
            "MOD_ACCOUNT": None,
            "TARGET_CHANNEL": None,
            "USER_COOLDOWN": None,
            "CHANNEL_COOLDOWN": None,
            "SNOWRUNNER_SAVE_DIRECTORY": "My Games/SnowRunner/base/storage/ec216826fe2f4ca4b55d84a631128619",
            "SNOWRUNNER_SAVE_NAME": "CompleteSave.dat",
            "COMMANDS": {
                "Winch": None,
                "HandBreak": None,
                "Horn": None,
                "Lights": None,
                "Fuel_Roulette": None,
                "PostMoney": None,
                "GenericSave": None,
                "Timeout_Roulette": None,
            },
            "APP_ID": None,
            "APP_SECRET": None,
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

    def update_config(key, value) -> None:
        global APP_CONFIG
        APP_CONFIG[key] = value
        Config.save_config()

    def check() -> None:
        if not Config.get_configs()["TARGET_CHANNEL"]:
            Config.update_config("TARGET_CHANNEL", input("What CHANNEL should we join?\n"))
        if not Config.get_configs()["APP_ID"]:
            Config.update_config("APP_ID", input("Input you APP ID:\n"))
        if not Config.get_configs()["APP_ID"]:
            Config.update_config("APP_SECRET", input("Input you APP SECRET:\n"))

    def command_is_active(str) -> bool:
        return APP_CONFIG["COMMANDS"][str]

    def get_config_key(config) -> dict:
        return APP_CONFIG[config]


APP_CONFIG: dict[str, str | dict] = None
