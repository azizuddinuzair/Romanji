from pathlib import Path
from arabic2latin import arabic_to_latin
#-------------------------------------------------------------------------------------------#
project_folder_path = Path(__file__).resolve().parent       #.parent gets the parent folder of the main python file
input_folder_path = project_folder_path / "input"  
output_folder_path = project_folder_path / "output"


def romanizing_Arabic():
    txt_files = list(input_folder_path.glob("*.txt"))       #finds all .txt files in the folder and put their addresses into a list

    for file_path in txt_files:
        with open(file_path, encoding="utf-8") as file:
            lines = file.read().splitlines()

        size = len(lines)

        for i in range(size):
            lines[i] = arabic_to_latin(lines[i])

        romanized_lyrics = "\n".join(lines)
        #print(romanized_lyrics) - check

        romanized_file_name = f"{file_path.stem}_romanized{file_path.suffix}"
        output_file_path = output_folder_path / romanized_file_name 
        output_file_path.write_text(romanized_lyrics, encoding="utf-8")

if __name__ == "__main__":
    romanizing_Arabic()    


