#!/usr/bin/python3
import links
import downloads
from os import path, mkdir, system
from pathlib import Path
import json

#Para obtener el directorio en línea de comando:
#from tkinter import Tk, filedialog as fd
#a = Tk()
#a.withdraw()
#dest_folder = fd.askdirectory()
#a.destroy()
dest_folder = Path("/home/makiol/Descargas/Anime/")

def init_files():
    if not path.isfile("current_download"):
        file = open("current_download", "w+")
        file.write("{}")
        file.close()

    if not path.isfile("register_log.json"):
        dr = {}
        dr["animes"] = {}
        with open("register_log.json","w+") as reg_log:
            json.dump(dr,reg_log,indent=4)

def normal_download():
    anime_info = None
    while anime_info == None:
        serie = input("Serie: ")
        anime_info = links.links(serie)
    if anime_info[0]:
        full_path = dest_folder / anime_info[1][7:]
        with open("current_download","w+") as cur:
            json.dump(anime_info, cur, indent = 4)
        if not path.exists(full_path):
            mkdir(full_path)
        e = anime_info[5][anime_info[2]]
        for enum in range(anime_info[3],anime_info[4]+1):
            downloads.download(e[enum], anime_info[1][7:], enum, dest_folder)
        with open("current_download","w+") as ff1:
            ff1.write("{}")

if __name__ == "__main__":
    init_files()
    with open("current_download","r") as ong:
        try:
            ongoing = json.load(ong)
        except json.decoder.JSONDecodeError:
            ongoing = {}
    if ongoing == {}:
        normal_download()
    else:
        ans = input("¿Desea continuar la descarga anterior?(y/n): ")
        while not ans in ["y","Y","n","N"]:
            ans = input("(y/n): ")
        if ans == "y" or ans == "Y":
            anime_info = ongoing
            e = anime_info[5][anime_info[2]]
            for enum in range(anime_info[3],anime_info[4]+1):
                downloads.download(e[str(enum)], anime_info[1][7:], enum, dest_folder)
            open("current_download","w+").close()
        else:
            normal_download()
