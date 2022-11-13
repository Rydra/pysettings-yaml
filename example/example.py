from decouple import config as config_dec
from split_settings.tools import optional
from pathlib import Path

from pysettings_yaml.loader import get_config

ENVIRONMENT = config_dec("ENVIRONMENT", default="dev")

BASE_DIR = Path(__file__).parent

setting_files = [
    BASE_DIR / "settings.yaml",
    optional(BASE_DIR / f"settings.{ENVIRONMENT}.yaml"),
]


config = get_config(setting_files)

SAMPLE_SETTING_BOOL = config("SAMPLE_SETTING_BOOL", cast=bool)
SAMPLE_SETTING_STR = config("SAMPLE_SETTING_STR", cast=str)
SAMPLE_SETTING_INT = config("SAMPLE_SETTING_INT", cast=int)

if __name__ == "__main__":
    print(SAMPLE_SETTING_BOOL)
    print(SAMPLE_SETTING_STR)
    print(SAMPLE_SETTING_INT)
