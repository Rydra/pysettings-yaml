from abc import ABC, abstractmethod
from typing import Union, Optional, Dict

from pydantic import BaseModel


class NoValue:
    pass


class OriginModel(BaseModel):
    name: str


class SettingsProvider(ABC):
    @staticmethod
    @property
    @abstractmethod
    def name() -> str:
        pass

    schema = OriginModel

    def parse_option(
        self, setting_name: str, origin_data: Optional[Dict] = None
    ) -> Union[Optional[str], NoValue]:
        origin = self.schema(**origin_data) if origin_data else self.schema(name="N/A")

        return self.get(setting_name, origin)

    @abstractmethod
    def get(
        self, setting_name: str, origin_data: OriginModel
    ) -> Union[Optional[str], NoValue]:
        raise NotImplementedError
