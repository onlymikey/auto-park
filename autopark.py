from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
import tempfile
import os

def get_all_m3u8_links(url, firefox_profile_path):
    options = Options()
    # No usar headless para evitar problemas con DRM
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

    # Esperar un poco para que se carguen las requests
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
    """
    Filtra las URLs según idioma y tipo:
    Español: video "f6-v1", audio "f8-a1"
    Inglés: video "f1-v1" (opcional), audio "f8-a1"
    """
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
                video_url = url  # Opcional si quieres video en inglés también
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

if __name__ == "__main__":
    profile_path = r"C:\Users\mikey\AppData\Roaming\Mozilla\Firefox\Profiles\r7l8sa9w.default-release"

    url_es = input("Introduce URL del capítulo en español: ").strip()
    url_en = input("Introduce URL del capítulo en inglés: ").strip()

    # Obtener todas las URLs .m3u8 de cada página
    m3u8_es = get_all_m3u8_links(url_es, profile_path)
    m3u8_en = get_all_m3u8_links(url_en, profile_path)

    if not m3u8_es or not m3u8_en:
        print("No se pudieron obtener enlaces .m3u8")
        exit(1)

    video_url, audio_es_url = filter_streams(m3u8_es, "es")
    video_en_url, audio_en_url = filter_streams(m3u8_en, "en")

    if not video_url:
        print("No se encontró stream de video español (f6-v1)")
        exit(1)
    if not audio_es_url:
        print("No se encontró stream de audio español (f8-a1)")
        exit(1)
    if not audio_en_url:
        print("No se encontró stream de audio inglés (f8-a1)")
        exit(1)

    # Nota: video_en_url es opcional, solo usamos video_url español

    output_filename = "SouthPark_Episode_Final.mkv"

    download_and_merge(video_url, audio_es_url, audio_en_url, output_filename)

    print("Proceso completado.")
