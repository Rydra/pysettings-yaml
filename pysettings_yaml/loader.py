import logging
import os
from typing import Optional, List, Dict, Union, Any, cast

import funcy
from decouple import undefined, Undefined, UndefinedValueError, strtobool

import yaml
from pydantic import BaseModel
from split_settings.tools import _Optional

from pysettings_yaml.providers.decouple import DecoupleSettingsProvider
from pysettings_yaml.providers.direct import DirectValueSettingsProvider
from pysettings_yaml.providers.interfaces import SettingsProvider, NoValue
from pysettings_yaml.utils import merge

logger = logging.getLogger()


def _cast_boolean(value: Any) -> bool:
    """
    Helper to convert config values to boolean as ConfigParser do.
    """
    value = str(value)
    return bool(value) if value == "" else bool(strtobool(value))


def _cast_do_nothing(value: Any) -> Any:
    return value


def cast_value(value: Any, cast: Any = undefined) -> Any:
    if isinstance(cast, Undefined):
        cast = _cast_do_nothing
    elif cast is bool:
        cast = _cast_boolean

    return cast(value)


class SettingsRepository:
    def __init__(
        self, setting_providers: Dict[str, SettingsProvider], registry: "RegistrySchema"
    ) -> None:
        self.setting_providers = setting_providers
        self.registry = registry

    def get_config_value(
        self,
        option: str,
        default: Any = undefined,
        cast: Any = undefined,
    ) -> Optional[Any]:
        if option in self.registry.settings:
            # If there is no registry, only the ConfigSettingsGetter can be used
            setting_metadata = self.registry.settings[option]
            origins = setting_metadata.origins

            value: Union[NoValue, Any] = NoValue()
            for origin in origins:
                getter = self.setting_providers[origin.name]
                params = funcy.omit(origin.dict(), ["name"])
                kwargs = {"option": option, **params}
                value = getter.get(**kwargs)
                if not isinstance(value, NoValue):
                    break
        else:
            # If there is no registry for the given settings,
            # only the ConfigSettingsGetter can be used
            value = DecoupleSettingsProvider().get(option=option)

        if isinstance(value, NoValue):
            if isinstance(default, Undefined):
                raise UndefinedValueError(
                    "{} not found. Declare it as envvar or define a default value.".format(
                        option
                    )
                )

            value = default

        return cast_value(value, cast)


class RegistrySchema(BaseModel):
    class SettingsSchema(BaseModel):
        class OriginSchema(BaseModel):
            name: str
            path: Optional[str]
            decrypt: Optional[bool]
            value: Optional[str]

        origins: List[OriginSchema]

    settings: Dict[str, SettingsSchema]


def get_config(
    registry: Optional[RegistrySchema] = None,
    additional_providers: Optional[List[SettingsProvider]] = None,
) -> Any:
    """
    Factory method to construct a settings retriever
    """

    additional_providers = additional_providers or []
    origins: Dict[str, SettingsProvider] = dict(
        (cast(str, p.name), p)
        for p in [
            *additional_providers,
            DecoupleSettingsProvider(),
            DirectValueSettingsProvider(),
        ]
    )

    return SettingsRepository(
        origins, registry or RegistrySchema(settings={})
    ).get_config_value


def load_registry(setting_paths: List[Union[str, _Optional]]) -> RegistrySchema:
    registry: Dict = {}
    for path in setting_paths:
        if os.path.exists(path):
            with open(path) as fs:
                registry = merge(registry, yaml.safe_load(fs))
        elif not isinstance(path, _Optional):
            raise IOError("No such file: {0}".format(path))

    return RegistrySchema(**registry)
