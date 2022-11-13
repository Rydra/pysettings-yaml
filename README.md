# Pysettings YAML

This library extends over the concepts of [Decouple](https://github.com/henriquebastos/python-decouple/) 
and [Split Settings](https://django-split-settings.readthedocs.io/en/latest/)
to create a library that is simple to use and expresses your settings in a
yaml file for higher expressivity.

## Installation

```
pip install pysettings-yaml
```

## Usage

Define a YAML file with the definition of your settings, for example, 
a `settings.yaml` in the same path as your settings module:

```yaml
settings:
  SAMPLE_SETTING_BOOL:  # Each entry inside the settings section is the name of your setting
    origins:
      - name: env
      - name: direct
        value: true
  SAMPLE_SETTING_STR:
    origins:
      - name: direct
        value: banana
      - name: env
```

Then you can use this file like this in a `settings.py`:

```python
from split_settings.tools import optional
from pathlib import Path

from pysettings_yaml import get_config

BASE_DIR = Path(__file__).parent

setting_files = [
    BASE_DIR / "settings.yaml",
]


config = get_config(setting_files)

SAMPLE_SETTING_BOOL = config("SAMPLE_SETTING_BOOL", cast=bool)
SAMPLE_SETTING_STR = config("SAMPLE_SETTING_STR")

print(SAMPLE_SETTING_BOOL)
print(SAMPLE_SETTING_STR)  # This will print banana
```

By default the library supports two origin names: `env` (to receive the value of your setting using the _decouple_ library)
or `direct` (to provide a constant value), but you can add your own providers easily
(refer to the "Adding custom providers" section).

Origin are evaluated in strict order. In those examples, `SAMPLE_SETTING_BOOL`
will evaluate first the `env` origin and, if that value is `None`, it will
process the next origin, which would be `direct`. In contrast, for `SAMPLE_SETTING_STR`,
the first origin is the `direct` origin. Since direct can never return `None`,
the env origin will never be evaluated.


## Overriding settings

You can define several setting files to be processed in order.
All of them will be merged together, so any subsequent setting file
will override the settings with the same name defined in a previous file
of the list. Very useful if you need to define different origins
for your settings depending on your deployment environment:

```python
from split_settings.tools import optional
from pathlib import Path
import os

from pysettings_yaml import get_config
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")

BASE_DIR = Path(__file__).parent

setting_files = [
    BASE_DIR / "settings.yaml",
    BASE_DIR / f"settings.{ENVIRONMENT}.yaml",
    optional(BASE_DIR / "settings.nonexistent.yaml")
]


config = get_config(setting_files)

SAMPLE_SETTING_BOOL = config("SAMPLE_SETTING_BOOL", cast=bool)
SAMPLE_SETTING_STR = config("SAMPLE_SETTING_STR")
```

Any path wrapped with the `optional` function will not raise an
exception should that file not exist in the path you specify.

## Adding custom providers

If you need other providers (for example for getting your settings from a vault
like Amazon SSM) you can implement your own providers like this:

```python
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

```

Just make sure to:
* Provide the `name` and a pydantic `schema`
* Implement the `get` method

Then you can obtain your config providing your `SettingProvider` and use it in your yaml:

```python
config = get_config(setting_files, additional_providers=[SampleAWSSettingsProvider()])
```

```yaml
settings:
  SAMPLE_SETTING:
    origins:
      - name: aws
        path: some/path
        decrypt: true
      - name: env
```
