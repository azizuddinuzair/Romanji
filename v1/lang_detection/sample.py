from langdetect import detect


<<<<<<< HEAD
# Detects if lyrics are Japanese or not
=======
# Detects if text is Japanese or not
# Returns True if the file contains Japanese text, False otherwise.
>>>>>>> f55ae08d35ff46e0b2053427a1a034e8b475eb0c
def is_japanese(file_path):
   try:
       with open(file_path, "r", encoding="utf-8") as file:
           lyrics = file.read().strip()


       if not lyrics:
           print("Error: The file is empty.")
           return False

       language = detect(lyrics)

       print(f"Detected language: {language}")
       if language == "ja":
           print("This is Japanese")
           return True
       else:
           print("This is not Japanese")
           return False


   except FileNotFoundError:
       print("Error: The file was not found.")
       return False


# Detects if lyrics are Korean or not
def is_korean(file_path):
   try:
       with open(file_path, "r", encoding="utf-8") as file:
           lyrics = file.read().strip()


       if not lyrics:
           print("Error: The file is empty.")
           return False

       language = detect(lyrics)

       print(f"Detected language: {language}")
       if language == "ko":
           print("This is Korean")
           return True
       else:
           print("This is not Korean")
           return False


   except FileNotFoundError:
       print("Error: The file was not found.")
       return False


# Detects if lyrics are Arabic or not
def is_arabic(file_path):
   try:
       with open(file_path, "r", encoding="utf-8") as file:
           lyrics = file.read().strip()


       if not lyrics:
           print("Error: The file is empty.")
           return False

       language = detect(lyrics)

       print(f"Detected language: {language}")
       if language == "ar":
           print("This is Arabic")
           return True
       else:
           print("This is not Arabic")
           return False


   except FileNotFoundError:
       print("Error: The file was not found.")
       return False


if __name__ == "__main__":
    japanese_file_path = "v1/lang_detection/japaneseTestFile.txt"
    korean_file_path = "v1/lang_detection/koreanTestFile.txt" 
    arabic_file_path = "v1/lang_detection/arabicTestFile.txt"
    is_japanese(japanese_file_path)
    is_korean(korean_file_path)
    is_arabic(arabic_file_path)
