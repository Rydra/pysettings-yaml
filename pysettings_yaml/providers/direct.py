from typing import Any, Union, Optional

from pysettings_yaml.providers.interfaces import SettingsProvider, NoValue


class DirectValueSettingsProvider(SettingsProvider):
    name = "direct"

    def get(  # type: ignore
        self, value: str, *args: Any, **kwargs: Any
    ) -> Union[Optional[str], NoValue]:
        return value
