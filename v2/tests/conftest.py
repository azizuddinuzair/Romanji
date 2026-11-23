from pathlib import Path

import pytest

from romanji.config import load_settings

V1_TEST_FILES = Path(__file__).resolve().parents[2] / "v1" / "lang_detection"


@pytest.fixture
def settings():
    """Default settings, independent of any local v2/.env or environment variables."""
    return load_settings(env_file=None, environ={})


@pytest.fixture
def japanese_file():
    return V1_TEST_FILES / "japaneseTestFile.txt"


@pytest.fixture
def korean_file():
    return V1_TEST_FILES / "koreanTestFile.txt"
