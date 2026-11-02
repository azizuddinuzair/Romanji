import os
import lyricsgenius
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(TOKEN)

userSong = input("What song?")
userArtist = input("What artist?")
tokenizedSong = []
temp = ""


song = genius.search_song(userSong, userArtist)

if song is None:
    print("No song exists, try a different song title or artist")
else:
    for line in song.lyrics.splitlines():
        line = line.strip()

        if (
            line != ""
            and not line.startswith("[Verse")
            and not line.startswith("[Chorus")
            and not line.startswith("[Bridge")
        ):
            tokenizedSong.append(line)
    
    with open("song_lyrics.txt", "w",encoding="utf-8") as file_out:
        for line in tokenizedSong:
            file_out.write(line + '\n')
    








