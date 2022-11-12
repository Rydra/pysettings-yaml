from typing import Any, Union, Optional

from decouple import config

from pysettings_yaml.providers.interfaces import SettingsProvider, NoValue


class DecoupleSettingsProvider(SettingsProvider):
    name = "env"

    def get(  # type: ignore
        self, option: str, *args: Any, **kwargs: Any
    ) -> Union[Optional[str], NoValue]:
        return config(option, default=NoValue())
