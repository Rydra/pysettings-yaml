from abc import ABC, abstractmethod
from typing import Any, Union, Optional


class NoValue:
    pass


class SettingsProvider(ABC):
    @staticmethod
    @property
    @abstractmethod
    def name() -> str:
        pass

    @abstractmethod
    def get(self, *args: Any, **kwargs: Any) -> Union[Optional[str], NoValue]:
        raise NotImplementedError
