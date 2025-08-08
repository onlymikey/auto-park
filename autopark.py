import json
import threading
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
import tempfile
import os

def input_con_timeout(prompt, timeout=10, default="n"):
    respuesta = [default]

    def preguntar():
        try:
            r = input(prompt).strip().lower()
            if r:
                respuesta[0] = r
        except EOFError:
            pass

    hilo = threading.Thread(target=preguntar)
    hilo.daemon = True
    hilo.start()
    hilo.join(timeout)

    return respuesta[0]

def get_all_m3u8_links(url, firefox_profile_path):
    options = Options()
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    options.profile = firefox_profile_path

    driver = webdriver.Firefox(options=options)
    driver.get(url)

    wait = WebDriverWait(driver, 20)
    try:
        play_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Play"]')))
        play_button.click()
        print("Play clicked")
    except Exception:
        print("No se encontró botón Play o ya está en reproducción")

    try:
        quality_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.quality-selector')))
        quality_button.click()
        print("Calidad selector abierto")

        hd_option = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), '720p') or contains(text(), '1080p')]")))
        hd_option.click()
        print("Calidad HD seleccionada")
    except Exception:
        print("No se encontró selector de calidad o no se pudo cambiar")

    time.sleep(7)

    m3u8_urls = []
    for request in driver.requests:
        if request.response and ".m3u8" in request.url:
            m3u8_urls.append(request.url)

    driver.quit()

    if not m3u8_urls:
        print("No se encontraron enlaces .m3u8")
        return []

    print(f"Se encontraron {len(m3u8_urls)} URLs .m3u8")
    return m3u8_urls

def filter_streams(m3u8_list, lang):
    video_url = None
    audio_url = None

    for url in m3u8_list:
        if lang == "es":
            if "f1-v1" in url and not video_url:
                video_url = url
            elif "f8-a1" in url and not audio_url:
                audio_url = url
        elif lang == "en":
            if "f1-v1" in url and not video_url:
                video_url = url
            elif "f8-a1" in url and not audio_url:
                audio_url = url

    return video_url, audio_url

def download_and_merge(video_url, audio_es_url, audio_en_url, output_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, "video.ts")
        audio_es_path = os.path.join(tmpdir, "audio_es.ts")
        audio_en_path = os.path.join(tmpdir, "audio_en.ts")

        def ffmpeg_download(url, out_path):
            cmd = ["ffmpeg", "-y", "-i", url, "-c", "copy", out_path]
            print(f"Descargando {url} a {out_path}")
            subprocess.run(cmd, check=True)

        ffmpeg_download(video_url, video_path)
        ffmpeg_download(audio_es_url, audio_es_path)
        ffmpeg_download(audio_en_url, audio_en_path)

        merge_cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_es_path,
            "-i", audio_en_path,
            "-map", "0:v",
            "-map", "1:a",
            "-map", "2:a",
            "-c", "copy",
            "-metadata:s:a:0", "language=spa",
            "-metadata:s:a:1", "language=eng",
            output_file
        ]
        print(f"Merging streams en {output_file}")
        subprocess.run(merge_cmd, check=True)

def procesar_capitulo(cap, base_folder, profile_path):
    temporada = cap["temporada"]
    numero = cap["numero"]
    nombre = cap["nombre"]
    url_es = cap.get("url_es", "").strip()
    url_en = cap.get("url_en", "").strip()

    if not url_es or not url_en:
        print(f"Saltando capítulo S{temporada:02d}E{numero:02d} '{nombre}' porque no tiene URL en español o inglés.")
        return True  

    season_folder = os.path.join(base_folder, f"Season {temporada:02d}")
    os.makedirs(season_folder, exist_ok=True)

    print(f"\n=== Procesando Temporada {temporada} Episodio {numero}: {nombre} ===")

    try:
        m3u8_es = get_all_m3u8_links(url_es, profile_path)
        m3u8_en = get_all_m3u8_links(url_en, profile_path)

        if not m3u8_es or not m3u8_en:
            raise ValueError("No se pudieron obtener enlaces .m3u8")

        video_url, audio_es_url = filter_streams(m3u8_es, "es")
        video_en_url, audio_en_url = filter_streams(m3u8_en, "en")

        if not video_url or not audio_es_url or not audio_en_url:
            raise ValueError("Faltan streams de video o audio")

        safe_name = nombre.replace(" ", "_").replace("/", "-")
        output_filename = os.path.join(season_folder, f"S{temporada:02d}E{numero:02d}_{safe_name}.mkv")

        download_and_merge(video_url, audio_es_url, audio_en_url, output_filename)
        print(f"Capítulo {numero} de la temporada {temporada} completado y guardado en {output_filename}")
        return True

    except Exception as e:
        print(f"Error procesando capítulo S{temporada:02d}E{numero:02d}: {e}")
        r = input_con_timeout("¿Quieres reintentar este capítulo? (s/n) [auto: no en 10s]: ", 10)
        if r == "s":
            return procesar_capitulo(cap, base_folder, profile_path)
        else:
            print("Saltando capítulo...")
            return False

if __name__ == "__main__":
    profile_path = r"C:\Users\mikey\AppData\Roaming\Mozilla\Firefox\Profiles\r7l8sa9w.default-release"
    base_folder = "descargas"
    os.makedirs(base_folder, exist_ok=True)

    with open("all_southpark_episodes.json", "r", encoding="utf-8") as f:
        capitulos = json.load(f)

    fallidos = []

    for cap in capitulos:
        exito = procesar_capitulo(cap, base_folder, profile_path)
        if not exito:
            fallidos.append(f"S{cap['temporada']:02d}E{cap['numero']:02d} - {cap['nombre']}")

    print("\nTodos los capítulos procesados.")
    if fallidos:
        print("\n❌ Capítulos que no se pudieron descargar:")
        for f in fallidos:
            print(f" - {f}")
