import json
import threading
import re
from urllib.parse import unquote
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
import tempfile
import os
import string
import datetime

LOG_FILE = "descargas.log"

def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts} {msg}\n")
    print(msg)


def sanitize_filename(name):
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c if c in valid_chars else '_' for c in name)

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

def extract_mtp(url):
    """
    Extrae el valor mtp del parámetro CMCD en la URL del stream.
    Ejemplo: CMCD=mtp=58300,ot=m,sf=h,...
    """
    try:
        url_decoded = unquote(url)
        m = re.search(r"mtp=(\d+)", url_decoded)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return 0

def filter_streams(m3u8_list, lang):
    """
    Devuelve (video_url, audio_url) para el idioma indicado.
    - Para video, el stream con mtp más alto (cualquier fX-vX)
    - Para audio, el primer stream f8-aX del idioma (esp o en)
    """
    video_candidates = []
    audio_url = None

    for url in m3u8_list:
        # Audio, típicamente f8-aX, y el idioma depende de lang
        if lang == "es" and "f8-a" in url:
            if not audio_url:
                audio_url = url
        elif lang == "en" and "f8-a" in url:
            if not audio_url:
                audio_url = url

        # Video streams, puede ser f1-v1, f6-v1, etc.
        if re.search(r"f\d+-v\d+", url):
            mtp = extract_mtp(url)
            video_candidates.append((mtp, url))

    video_url = None
    if video_candidates:
        video_url = max(video_candidates, key=lambda x: x[0])[1]

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

def es_1080p(file_path):
    """Verifica si el archivo tiene resolución 1080p."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=height",
            "-of", "csv=p=0",
            file_path
        ]
        salida = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        return salida.isdigit() and int(salida) >= 1080
    except Exception:
        return False

def procesar_capitulo(cap, base_folder, profile_path, max_retries=3, delay_between_retries=5):
    temporada = cap["temporada"]
    numero = cap["numero"]
    nombre = cap["nombre"]
    url_es = cap.get("url_es", "").strip()
    url_en = cap.get("url_en", "").strip()

    season_folder = os.path.join(base_folder, f"Season {temporada:02d}")
    os.makedirs(season_folder, exist_ok=True)

    safe_name = sanitize_filename(nombre)
    output_filename = os.path.join(season_folder, f"S{temporada:02d}E{numero:02d}_{safe_name}.mkv")

    old_safe_name = nombre.replace(" ", "_").replace("/", "-")
    output_filename_old = os.path.join(season_folder, f"S{temporada:02d}E{numero:02d}_{old_safe_name}.mkv")

    try:
        if os.path.exists(output_filename) and es_1080p(output_filename):
            log(f"✅ Saltando S{temporada:02d}E{numero:02d} '{nombre}' (ya existe en 1080p)")
            return True
        if os.path.exists(output_filename_old) and es_1080p(output_filename_old):
            log(f"✅ Saltando S{temporada:02d}E{numero:02d} '{nombre}' (ya existe en 1080p con nombre antiguo)")
            return True
    except Exception as e:
        log(f"⚠️ Advertencia al comprobar archivo existente: {e}")

    for p in (output_filename, output_filename_old):
        if os.path.exists(p) and not es_1080p(p):
            try:
                log(f"⚠️ Eliminando {p} (no es 1080p)")
                os.remove(p)
            except Exception as e:
                log(f"⚠️ No se pudo eliminar {p}: {e}")

    if not url_es or not url_en:
        log(f"⚠️ Saltando S{temporada:02d}E{numero:02d} '{nombre}' (faltan URLs)")
        return True

    log(f"\n=== Procesando Temporada {temporada} Episodio {numero}: {nombre} ===")

    attempt = 1
    while attempt <= max_retries:
        try:
            log(f"➡️ Intento {attempt}/{max_retries}")

            m3u8_es = get_all_m3u8_links(url_es, profile_path)
            m3u8_en = get_all_m3u8_links(url_en, profile_path)

            if not m3u8_es or not m3u8_en:
                raise RuntimeError("No se pudieron obtener enlaces .m3u8")

            video_url, audio_es_url = filter_streams(m3u8_es, "es")
            _, audio_en_url = filter_streams(m3u8_en, "en")

            if not video_url or not audio_es_url or not audio_en_url:
                raise RuntimeError("Faltan streams de video o audio")

            download_and_merge(video_url, audio_es_url, audio_en_url, output_filename)

            if not es_1080p(output_filename):
                if os.path.exists(output_filename):
                    os.remove(output_filename)
                raise RuntimeError("El archivo no es 1080p")

            log(f"🎬 ✔️ S{temporada:02d}E{numero:02d} completado -> {output_filename}")
            return True

        except Exception as e:
            log(f"❌ Error en intento {attempt}/{max_retries}: {e}")

            for p in (output_filename, output_filename_old):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

            if attempt == 1:
                log(f"❓ Falló S{temporada:02d}E{numero:02d}. Reintentando...")


            attempt += 1
            if attempt <= max_retries:
                log(f"⏳ Esperando {delay_between_retries}s antes del siguiente intento...")
                time.sleep(delay_between_retries)
            else:
                log(f"❌ Falló tras {max_retries} intentos. Saltando.")
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
