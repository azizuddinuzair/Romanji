from langdetect import detect_langs, LangDetectException

def detect_languages(file_path, confidence_threshold=0.25):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lyrics = file.read().strip()

        if not lyrics:
            print("Error: The file is empty.")
            return []

        detected_langs = detect_langs(lyrics)
        filtered_langs = [lang for lang in detected_langs if lang.prob >= confidence_threshold]
        return filtered_langs

    except FileNotFoundError:
        print("Error: The file was not found.")
        return []
    except LangDetectException:
        print("Error: Failed to detect language.")
        return []


if __name__ == "__main__":
    japanese_file_path = "v1/lang_detection/japaneseTestFile.txt"
    korean_file_path = "v1/lang_detection/koreanTestFile.txt"
    arabic_file_path = "v1/lang_detection/arabicTestFile.txt"
    spanish_file_path = "v1/lang_detection/spanish.txt"

    arabic_portuguese_file_path = "v1/lang_detection/arabic_portugueseTestFile.txt"

    print("Testing Japanese file:")
    print(detect_languages(japanese_file_path))

    print("Testing Korean file:")
    print(detect_languages(korean_file_path))

    print("Testing Arabic file:")
    print(detect_languages(arabic_file_path))

    print("Testing Spanish file:")
    print(detect_languages(spanish_file_path))

    print("\nTesting Arabic-Portuguese file:")

    print(detect_languages(arabic_portuguese_file_path))



