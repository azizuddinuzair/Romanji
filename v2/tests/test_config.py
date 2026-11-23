import pytest

from romanji.config import PROJECT_ROOT, ConfigError, load_settings, require_genius_token


def test_defaults(settings):
    assert settings.whisper_model == "small"
    assert settings.whisper_device == "auto"
    assert settings.default_language == ""
    assert settings.japanese_romanization == "hepburn"
    assert settings.align_width == 75
    assert settings.lang_confidence == 0.25
    assert settings.ffmpeg_path == ""
    assert settings.output_dir == PROJECT_ROOT / "output"


def test_missing_token_is_not_an_error_until_genius_mode(settings):
    assert settings.genius_access_token == ""
    with pytest.raises(ConfigError, match="GENIUS_ACCESS_TOKEN"):
        require_genius_token(settings)


def test_token_is_returned_when_set():
    settings = load_settings(env_file=None, environ={"GENIUS_ACCESS_TOKEN": "fake-token-for-test"})
    assert require_genius_token(settings) == "fake-token-for-test"


def test_environment_overrides_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("WHISPER_MODEL=tiny\nDEFAULT_LANGUAGE=ko\n", encoding="utf-8")
    settings = load_settings(env_file=env_file, environ={"WHISPER_MODEL": "medium"})
    assert settings.whisper_model == "medium"
    assert settings.default_language == "ko"


def test_blank_values_use_defaults():
    settings = load_settings(env_file=None, environ={"WHISPER_MODEL": "", "ALIGN_WIDTH": "", "OUTPUT_DIR": ""})
    assert settings.whisper_model == "small"
    assert settings.align_width == 75


@pytest.mark.parametrize(
    "key, value",
    [
        ("WHISPER_MODEL", "huge"),
        ("WHISPER_DEVICE", "gpu"),
        ("DEFAULT_LANGUAGE", "fr"),
        ("JAPANESE_ROMANIZATION", "nihon"),
        ("ALIGN_WIDTH", "wide"),
        ("ALIGN_WIDTH", "3"),
        ("LANG_CONFIDENCE", "2"),
    ],
)
def test_invalid_values_name_the_setting(key, value):
    with pytest.raises(ConfigError, match=key):
        load_settings(env_file=None, environ={key: value})


def test_output_dir_absolute_is_kept(tmp_path):
    settings = load_settings(env_file=None, environ={"OUTPUT_DIR": str(tmp_path)})
    assert settings.output_dir == tmp_path
