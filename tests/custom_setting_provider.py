from typing import Union, Optional

from pysettings_yaml.providers.interfaces import SettingsProvider, OriginModel, NoValue


class AWSModel(OriginModel):
    path: str
    decrypt: bool


class SampleAWSSettingsProvider(SettingsProvider):
    name = "aws"
    schema = AWSModel

    def get(
        self, setting_name: str, origin_data: AWSModel
    ) -> Union[Optional[str], NoValue]:
        return f"path: {origin_data.path}, decrypt: {origin_data.decrypt}"
