#!/usr/bin/python3
import json
from pathlib import Path
from os import path, mkdir, system, remove, name as os_name
import links
import downloads

# Para obtener el directorio en línea de comando:
#from tkinter import Tk, filedialog as fd
#a = Tk()
# a.withdraw()
#dest_folder = fd.askdirectory()
# a.destroy()

if os_name == 'nt':
    dest_folder = Path('C:\\Users\\maicol\\Downloads\\Series\\')
else:
    dest_folder = Path('/home/makiol/Descargas/Anime/')
current_download_file = 'current_download.json'
register_log_file = 'register_log.json'


def init_files():
    '''Initializes files in case they do not exist'''
    if not path.isfile(current_download_file):
        with open(current_download_file, "w+") as cur_down:
            cur_down.write("{}")

    if not path.isfile("register_log.json"):
        dr = {}
        dr['animes'] = {}
        with open(register_log_file, "w+") as reg_log:
            json.dump(dr, reg_log, indent=4)


if __name__ == "__main__":
    init_files()
    with open(current_download_file, "r") as ong:
        ongoing = json.load(ong)
    if ongoing == {}:
        serie = input('Serie: ')
        success = links.links(serie)
        if not success:
            raise Exception
    else:
        ans = input(
            f"¿Desea continuar con la descarga de {ongoing['name']}?(y/n): ")
        while not ans in ["y", "Y", "n", "N"]:
            ans = input("(y/n): ")
        if not (ans == "y" or ans == "Y"):
            remove(current_download_file)
            serie = input('Serie: ')
            success = links.links(serie)
            if not success:
                raise Exception
    with open(current_download_file, 'r') as cur:
        anime_info = json.load(cur)
    full_path = dest_folder / anime_info['parsed_name']
    if not path.exists(full_path):
        mkdir(full_path)
    chapters = anime_info['chapters']
    for enum in range(anime_info['first'], anime_info['last']+1):
        downloads.download(
            chapters[str(enum)],
            anime_info['parsed_name'],
            enum,
            dest_folder
        )
    remove(current_download_file)
