from typing import Union, Optional

from decouple import config

from pysettings_yaml.providers.interfaces import SettingsProvider, NoValue, OriginModel


class DecoupleSettingsProvider(SettingsProvider):
    name = "env"

    def get(
        self, setting_name: str, origin: OriginModel
    ) -> Union[Optional[str], NoValue]:
        return config(setting_name, default=NoValue())
