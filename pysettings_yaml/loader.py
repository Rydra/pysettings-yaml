import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Union, Any, cast

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
        self, setting_providers: Dict[str, SettingsProvider], registry: "RegistryModel"
    ) -> None:
        self.setting_providers = setting_providers
        self.registry = registry

    def get_config_value(
        self,
        setting_name: str,
        default: Any = undefined,
        cast: Any = undefined,
    ) -> Optional[Any]:
        if setting_name in self.registry.settings:
            # If there is no registry, only the ConfigSettingsGetter can be used
            setting_metadata = self.registry.settings[setting_name]
            origins = setting_metadata.origins

            value: Union[NoValue, Any] = NoValue()
            for origin in origins:
                name = origin.get("name")
                if not name:
                    raise ValueError(
                        "Any definition of origin must contain at least the name property"
                    )
                getter = self.setting_providers.get(name)
                if not getter:
                    raise ValueError(f"Unknown origin {name}")

                value = getter.parse_option(
                    setting_name=setting_name, origin_data=origin
                )
                if not isinstance(value, NoValue):
                    break
        else:
            # If there is no registry for the given settings,
            # only the ConfigSettingsGetter can be used
            value = DecoupleSettingsProvider().parse_option(setting_name=setting_name)

        if isinstance(value, NoValue):
            if isinstance(default, Undefined):
                raise UndefinedValueError(
                    "{} not found. Declare it as envvar or define a default value.".format(
                        setting_name
                    )
                )

            value = default

        return cast_value(value, cast)


class RegistryModel(BaseModel):
    class SettingsModel(BaseModel):
        origins: List[Dict]

    settings: Dict[str, SettingsModel]


def get_config(
    setting_paths: Optional[List[Union[str, Path, _Optional]]] = None,
    registry: Optional[RegistryModel] = None,
    additional_providers: Optional[List[SettingsProvider]] = None,
) -> Any:
    """

    :param setting_paths: a list of `Path` or strings that point to the
    path of the yaml files. This is ignored if registry is supplied
    :param registry: a registry that contains all the data
    that defines where and how to obtain a setting
    :param additional_providers: a list of additional `SettingsProvider` you
    would like to include
    :return:
    """

    setting_paths = setting_paths or []
    if not setting_paths and not registry:
        raise ValueError(
            "Either the settings_paths or the registry variables must be set"
        )

    additional_providers = additional_providers or []
    setting_providers: Dict[str, SettingsProvider] = dict(
        (cast(str, p.name), p)
        for p in [
            *additional_providers,
            DecoupleSettingsProvider(),
            DirectValueSettingsProvider(),
        ]
    )

    return SettingsRepository(
        setting_providers, registry or load_registry(setting_paths)
    ).get_config_value


def load_registry(setting_paths: List[Union[str, _Optional]]) -> RegistryModel:
    registry: Dict = {}
    for path in setting_paths:
        if os.path.exists(path):
            with open(path) as fs:
                registry = merge(registry, yaml.safe_load(fs))
        elif not isinstance(path, _Optional):
            raise IOError("No such file: {0}".format(path))

    return RegistryModel(**registry)
