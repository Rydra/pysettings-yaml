from decouple import UndefinedValueError
from hamcrest import *
from split_settings.tools import optional

from pysettings_yaml.loader import load_registry, get_config


class TestPySettingsYaml:
    def test_load_settings_from_direct_value_vars(self, shared_datadir):
        setting_files = [
            shared_datadir / "settings.yaml",
            optional(shared_datadir / "settings.dev.yaml"),
            optional(shared_datadir / "settings.prod.yaml"),
        ]

        config = get_config(registry=load_registry(setting_files))

        assert_that(config("SAMPLE_SETTING_BOOL", cast=bool), is_(True))
        assert_that(config("SAMPLE_SETTING_STR", cast=str), is_("banana"))
        assert_that(config("SAMPLE_SETTING_INT", cast=int), is_(2))

    def test_load_settings_from_env_vars(self, shared_datadir, monkeypatch):
        monkeypatch.setenv("SAMPLE_SETTING_STR", "apple")

        setting_files = [
            shared_datadir / "settings.yaml",
            optional(shared_datadir / "settings.dev.yaml"),
            optional(shared_datadir / "settings.prod.yaml"),
        ]

        config = get_config(registry=load_registry(setting_files))

        assert_that(config("SAMPLE_SETTING_STR", cast=str), is_("apple"))

    def test_settings_order_is_relevant(self, shared_datadir, monkeypatch):
        monkeypatch.setenv("SAMPLE_SETTING_STR", "apple")

        setting_files = [
            shared_datadir / "settings_ordered_altered.yaml",
            optional(shared_datadir / "settings.dev.yaml"),
            optional(shared_datadir / "settings.prod.yaml"),
        ]

        config = get_config(registry=load_registry(setting_files))

        assert_that(config("SAMPLE_SETTING_STR", cast=str), is_("banana"))

    def test_undefined_variables_default_to_env(self, shared_datadir, monkeypatch):
        monkeypatch.setenv("NON_EXISTANT_VAR", "apple")

        setting_files = [
            shared_datadir / "settings.yaml",
            optional(shared_datadir / "settings.dev.yaml"),
            optional(shared_datadir / "settings.prod.yaml"),
        ]

        config = get_config(registry=load_registry(setting_files))

        assert_that(config("NON_EXISTANT_VAR", cast=str), is_("apple"))

    def test_calling_undefined_settings_raises_exceptions(self, shared_datadir):
        setting_files = [
            shared_datadir / "settings.yaml",
            optional(shared_datadir / "settings.dev.yaml"),
            optional(shared_datadir / "settings.prod.yaml"),
        ]

        config = get_config(registry=load_registry(setting_files))

        assert_that(
            calling(config).with_args("NON_EXISTANT_VAR", cast=str),
            raises(UndefinedValueError),
        )
