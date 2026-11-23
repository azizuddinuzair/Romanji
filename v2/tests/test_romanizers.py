import pytest

from romanji import romanizers
from romanji.romanizers import REGISTRY, romanize


@pytest.fixture(autouse=True)
def _reset_japanese_system():
    romanizers.configure("hepburn")
    yield
    romanizers.configure("hepburn")


def test_every_module_declares_its_language():
    assert set(REGISTRY) == {"ja", "ko", "ar", "sr"}
    for code, module in REGISTRY.items():
        assert module.LANG == code
        assert callable(module.romanize)


def test_japanese():
    assert romanize("闇の中から新しい人生を始めよう", "ja") == "yami no naka kara atarashii jinsei o hajime you"


def test_japanese_particle_fix_from_v1():
    assert romanize("私は元気です", "ja") == "watashi wa genki desu"
    assert romanize("学校へ行く", "ja") == "gakkou e iku"
    assert romanize("水を飲む", "ja") == "mizu o nomu"


@pytest.mark.xfail(reason="v1 limitation: pykakasi fuses は into the word (bokuha), so the particle fix misses it", strict=True)
def test_japanese_particle_fused_into_word():
    assert romanize("僕は行く", "ja") == "boku wa iku"


def test_japanese_system_setting():
    assert romanize("つづく", "ja") == "tsuzuku"  # hepburn
    romanizers.configure("kunrei")
    assert romanize("つづく", "ja") == "tuzuku"
    assert romanize("しんぶん", "ja") == "sinbun"


def test_korean():
    assert romanize("내 피, 땀, 눈물, 내 마지막 춤을", "ko") == "nae pi, ttam, nunmul, nae majimak chumeul"


def test_korean_line_with_english_keeps_the_english():
    assert romanize("Baby, 취해도 돼", "ko").startswith("Baby, ")


def test_arabic_returns_latin_text():
    result = romanize("أحبك كثيرا", "ar")
    assert result
    assert not any("؀" <= ch <= "ۿ" for ch in result)


def test_serbian_cyrillic():
    assert romanize("Ја волим тебе", "sr") == "Ja volim tebe"


def test_serbian_latin_is_still_processed():
    assert romanize("Šta radiš, đače", "sr") == "Shta radish, djache"


def test_serbian_digraph_letters():
    assert romanize("љубав њега џеп", "sr") == "ljubav njega dzhep"


@pytest.mark.parametrize("lang", ["ja", "ko", "ar"])
def test_latin_only_lines_are_unchanged(lang):
    assert romanize("Baby, I'm falling", lang) == "Baby, I'm falling"


@pytest.mark.parametrize("lang", ["und", "en", "", "xx"])
def test_unknown_language_is_unchanged(lang):
    assert romanize("闇の中", lang) == "闇の中"


def test_blank_line_is_unchanged():
    assert romanize("   ", "ja") == "   "
