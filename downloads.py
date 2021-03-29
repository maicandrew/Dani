#!/usr/bin/python3
import requests as rq
import os
from tqdm import tqdm
from links import html
from urllib.parse import urlparse
import js2py

def get_content(r, f, t, bz):
    for data in r.iter_content(bz):
        t.update(len(data))
        f.write(data)

def eval_js(id):
    node = html.getElementById(id).parentNode.children[-1]
    js_code = """function extract(){ x = {}; y = {};"""
    js_code += node.innerHTML.replace("document.getElementById('dlbutton')", "x")
    js_code = js_code.replace("document.getElementById('fimage')", 'y')
    js_code += """\nreturn x.href;} extract();"""
    local = js2py.eval_js(js_code)
    return local

def download(url, serie, cap, dest_folder):
    path = dest_folder / serie / str(serie + " - " + str(cap) + ".mp4")
    parsed_url = urlparse(url)
    r = rq.get(parsed_url.geturl())
    html.parseStr(r.text)
    local = eval_js('dlbutton')
    print(local)
    link = parsed_url.scheme + '://' + parsed_url.hostname + local
    print(link)
    print("Descargando capitulo: ", cap)
    total_size = int(rq.head(link).headers.get('content-length', 0))
    if not os.path.exists(path):
        open_mode = 'wb'
        headers = {}
    else:
        downloaded = os.stat(path).st_size
        open_mode = 'ab'
        headers = {"Range":f"bytes={downloaded}-{total_size}"}
    try:
        r = rq.get(link, stream  = True, headers=headers)
        bz = 1024 #1 Kibibyte
        t=tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(path, mode=open_mode) as file:
            get_content(r, file, t, bz)
        t.close()
        if total_size != 0 and t.n != total_size:
            print("ERROR, something went wrong")
    except:
        print("Error al intentar descargar el capitulo")
        return False
    print("Listo capitulo: ",cap)
    return True
