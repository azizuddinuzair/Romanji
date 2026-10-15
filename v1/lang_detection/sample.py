from langdetect import detect


# Detects if code is Japanese or not
def is_japanese(file_path):
   try:
       with open(file_path, "r", encoding="utf-8") as file:
           lyrics = file.read().strip()


       if not lyrics:
           print("Error: The file is empty.")
           return False


       language = detect(lyrics)


       if language == "ja":
           print("This is Japanese")
           return True
       else:
           print("This is not Japanese")
           return False


   except FileNotFoundError:
       print("Error: The file was not found.")
       return False



