from typing import Union, Optional

from pysettings_yaml.providers.interfaces import SettingsProvider, NoValue, OriginModel


class DirectValueModel(OriginModel):
    value: str


class DirectValueSettingsProvider(SettingsProvider):
    name = "direct"
    schema = DirectValueModel

    def get(
        self, setting_name: str, origin_data: DirectValueModel
    ) -> Union[Optional[str], NoValue]:
        return origin_data.value
