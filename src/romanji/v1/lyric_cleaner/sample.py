import os
import lyricsgenius
from dotenv import load_dotenv
import nltk
from nltk.tokenize import sent_tokenize

load_dotenv()
nltk.download('punkt')
nltk.download('punkt_tab')

TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(TOKEN)

song = genius.search_song("Dark Beach", "Pastel Ghost")
sentences = sent_tokenize(song.lyrics)
tokenizedSong = []
temp = ""
for char in sentences[0]:
    if char == '\n':
        if ("[Verse" not in temp) and ("[Chorus" not in temp) and ("[Bridge" not in temp) and (temp != ""):
            tokenizedSong.append(temp)
            temp = "" 
        else:
            temp = ""
    else:
        temp += char

with open("song_lyrics.txt", "w",encoding="utf-8") as file_out:
    for line in tokenizedSong:
        file_out.write(line + '\n')
