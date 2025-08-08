import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import json

def get_mgid_season_1(lang="es"):
    url_map = {
        "es": "https://www.southpark.lat/seasons/south-park/yjy8n9/season-1",
        "en": "https://www.southpark.lat/en/seasons/south-park/yjy8n9/season-1"
    }
    url = url_map.get(lang)
    if not url:
        return None

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    mgid = None
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string and "mgid:arc:season" in script.string:
            mgid_search = re.search(r'mgid:arc:season:southpark.intl:[a-z0-9\-]+', script.string)
            if mgid_search:
                mgid = mgid_search.group(0)
                break
    return mgid

def get_seasons():
    url_es = "https://www.southpark.lat/seasons/south-park"
    url_en = "https://www.southpark.lat/en/seasons/south-park"

    r_es = requests.get(url_es)
    soup_es = BeautifulSoup(r_es.text, "html.parser")

    r_en = requests.get(url_en)
    soup_en = BeautifulSoup(r_en.text, "html.parser")

    seasons = {}

    # Agregar temporada 1 manualmente, obteniendo su MGID
    seasons[1] = {
        "es": get_mgid_season_1("es"),
        "en": get_mgid_season_1("en")
    }

    # Extraer temporadas español (temporadas 2 en adelante)
    seasons_links_es = soup_es.select('a.css-1u8qly9.ejngw060')
    mgids_es = {}
    for link in seasons_links_es:
        href = link.get('href')
        if href is None:
            continue
        m = re.search(r'temporada[-/]?(\d+)', href)
        if not m:
            continue
        season_number = int(m.group(1))
        if season_number == 1:
            continue  # Ya la agregamos manualmente
        season_page_url = f"https://www.southpark.lat{href}"
        season_page = requests.get(season_page_url)
        season_soup = BeautifulSoup(season_page.text, "html.parser")

        mgid = None
        scripts = season_soup.find_all("script")
        for script in scripts:
            if script.string and "mgid:arc:season" in script.string:
                mgid_search = re.search(r'mgid:arc:season:southpark.intl:[a-z0-9\-]+', script.string)
                if mgid_search:
                    mgid = mgid_search.group(0)
                    break

        if mgid:
            mgids_es[season_number] = mgid

    # Extraer temporadas inglés (temporadas 2 en adelante)
    seasons_links_en = soup_en.select('a.css-1u8qly9.ejngw060')
    mgids_en = {}
    for link in seasons_links_en:
        href = link.get('href')
        if href is None:
            continue
        m = re.search(r'season[-/]?(\d+)', href)
        if not m:
            continue
        season_number = int(m.group(1))
        if season_number == 1:
            continue  # Ya la agregamos manualmente
        season_page_url = f"https://www.southpark.lat{href}"
        season_page = requests.get(season_page_url)
        season_soup = BeautifulSoup(season_page.text, "html.parser")

        mgid = None
        scripts = season_soup.find_all("script")
        for script in scripts:
            if script.string and "mgid:arc:season" in script.string:
                mgid_search = re.search(r'mgid:arc:season:southpark.intl:[a-z0-9\-]+', script.string)
                if mgid_search:
                    mgid = mgid_search.group(0)
                    break

        if mgid:
            mgids_en[season_number] = mgid

    # Combinar MGIDs español e inglés para temporadas 2 en adelante
    for season_num in set(list(mgids_es.keys()) + list(mgids_en.keys())):
        seasons[season_num] = {
            "es": mgids_es.get(season_num),
            "en": mgids_en.get(season_num)
        }

    return seasons

def get_episodes(season_number, season_mgid, lang):
    if not season_mgid:
        return []
    season_encoded = urllib.parse.quote(season_mgid, safe='')
    page = 1
    per_page = 20
    episodes = []

    while True:
        url = f"https://www.southpark.lat/api/context/{season_encoded}/episode/{page}/{per_page}"
        r = requests.get(url)
        data = r.json()

        if not data.get("items"):
            break

        for i, item in enumerate(data["items"], 1):
            # Construir URL correcta según idioma
            url_rel = item['url']  # ej: /episodios/940f8z/...
            if lang == "en":
                # reemplazar "/episodios/" por "/en/episodes/"
                url_correcta = "https://www.southpark.lat" + url_rel.replace("/episodios/", "/en/episodes/")
            else:
                url_correcta = "https://www.southpark.lat" + url_rel

            episodes.append({
                "temporada": season_number,
                "numero": ((page - 1) * per_page) + i,
                "nombre": item["meta"]["subHeader"],
                f"url_{lang}": url_correcta
            })

        page += 1

    return episodes

if __name__ == "__main__":
    seasons = get_seasons()
    all_episodes = []

    for season, mgids in seasons.items():
        print(f"Obteniendo episodios temporada {season}...")
        eps_es = get_episodes(season, mgids.get("es"), "es")
        eps_en = get_episodes(season, mgids.get("en"), "en")

        # Unir episodios español e inglés según número, llenando url_en y url_es
        combined = {}
        for ep in eps_es:
            combined[ep["numero"]] = ep
            if "url_en" not in combined[ep["numero"]]:
                combined[ep["numero"]]["url_en"] = ""

        for ep in eps_en:
            if ep["numero"] in combined:
                combined[ep["numero"]]["url_en"] = ep.get("url_en", "")
            else:
                combined[ep["numero"]] = ep
                if "url_es" not in combined[ep["numero"]]:
                    combined[ep["numero"]]["url_es"] = ""

        for numero in sorted(combined):
            all_episodes.append(combined[numero])

    with open("all_southpark_episodes.json", "w", encoding="utf-8") as f:
        json.dump(all_episodes, f, indent=2, ensure_ascii=False)

    print("Archivo all_southpark_episodes.json creado con episodios en español e inglés.")
