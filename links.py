import requests as rq
import urllib.parse as url
import json
import AdvancedHTMLParser

html = AdvancedHTMLParser.AdvancedHTMLParser()


def get_anime_info(browse):
    html.parseStr(browse)
    lista = html.getElementsByClassName("Anime alt B")
    if len(lista) == 0:
        print("No existe ningun anime con ese nombre")
        return None
    else:
        for i in range(len(lista)):
            a = lista[i].getChildren()[0].getChildren()[1].innerHTML
            print(i+1, a)
        choice = int(input("Selecione un título: "))
        link = lista[choice-1].getChildren()[0].getAttribute("href")
        name = lista[choice-1].getChildren()[0].getChildren()[1].innerHTML
        return [link, name]


def get_episodes(anime):
    text = anime.text
    epiindex1 = text.find("var episodes")
    epiindex1 += text[epiindex1:].find("=")
    epiindex2 = text[epiindex1:].find(";")
    episodes = eval(text[epiindex1+2:epiindex2+epiindex1])
    episodes.reverse()
    return len(episodes)


def links(serie):
    try:
        from control import current_download_file, register_log_file
        browse = rq.get("https://animeflv.net/browse?q="+serie).text
        l = get_anime_info(browse)
        print("Descargando:", l[1])
        if l == None:
            return None
        else:
            link = l[0]
            name = l[1]
            parsed_name = link.split("/")[2]
            try:
                anime = rq.get("https://animeflv.net"+link)
                print("Cuenta con:", get_episodes(anime), "episodios")
            except:
                print("Hubo un problema al intentar acceder a la pagina del anime")
            with open(register_log_file, "r") as file:
                reg_log = json.load(file)
            if not parsed_name in reg_log['animes']:
                reg_log['animes'][parsed_name] = {'chapters': {}, 'name': name}
            ongoing = {
                'chapters': {},
                'name': name,
                'parsed_name': parsed_name
            }
            ongoing['first'] = int(input("Primer capitulo a descargar: "))
            ongoing['last'] = int(input("Ultimo capitulo: "))
            if anime.status_code != 200:
                print("Al parecer hay un error en el nombre, intenta de nuevo")
                return False
            else:
                for i in range(ongoing['first'], ongoing['last'] + 1):
                    if str(i) in reg_log['animes'][parsed_name]['chapters']:
                        ongoing['chapters'][i] = reg_log['animes'][parsed_name]['chapters'][str(
                            i)]
                    else:
                        try:
                            chapter = rq.get(
                                "https://animeflv.net/ver/"+parsed_name+"-"+str(i))
                        except:
                            print("Hubo un problema al intentar acceder al capitulo")
                        if (chapter.status_code != 200):
                            print(name, i)
                            print("Capitulo fuera de rango")
                            return False
                        else:
                            text = chapter.text
                            html.parseStr(text)
                            table_body = html.getElementsByClassName("RTbl Dwnl")[
                                0][1]
                            children = table_body.getChildren()
                            for child in children:
                                if child[0].innerHTML == "Zippyshare":
                                    link = child[-1].firstChild.attributes["href"]
                            reg_log["animes"][parsed_name]['chapters'][i] = link
                            ongoing['chapters'][i] = link
            json.dump(reg_log, open(register_log_file, "w+"), indent=4)
            json.dump(ongoing, open(current_download_file, 'w+'), indent=4)
            return True
    except Exception as e:
        print("Hubo un problema con la busqueda", e)
        return False
