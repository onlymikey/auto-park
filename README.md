# South Park Downloader

Proyecto para obtener la lista completa de episodios de South Park (temporadas y episodios) con URLs en español e inglés desde [southpark.lat](https://www.southpark.lat), y descargar automáticamente los episodios con audio en ambos idiomas usando Selenium y FFmpeg.

---

## Descripción general

Este proyecto consta de dos scripts principales:

### 1. `south_scrapper.py`

- Obtiene la lista completa de temporadas y episodios de South Park en español e inglés.
- Extrae los identificadores MGID únicos para cada temporada.
- Consulta la API pública para listar episodios de cada temporada con metadatos.
- Genera un archivo JSON `all_southpark_episodes.json` con la información de episodios, incluyendo URLs en español e inglés correctamente formateadas.

### 2. `auto_park.py`

- Lee el archivo `all_southpark_episodes.json`.
- Usa Selenium Wire con Firefox para cargar las páginas de episodios (tanto en español como en inglés).
- Interactúa con el reproductor para iniciar la reproducción y seleccionar calidad HD.
- Captura las peticiones de red para obtener los enlaces `.m3u8` de video y audio.
- Descarga por separado el video y las pistas de audio en español e inglés usando FFmpeg.
- Fusiona los streams en un solo archivo MKV con audio multilingüe.
- Guarda los episodios organizados por temporada en una carpeta local.

---

## Requisitos

- Python 3.8+
- [Firefox](https://www.mozilla.org/firefox/)
- [Geckodriver](https://github.com/mozilla/geckodriver/releases) (en PATH)
- Selenium y Selenium Wire:
  ```bash
  pip install selenium selenium-wire
* BeautifulSoup4:

  ```bash
  pip install beautifulsoup4
  ```
* FFmpeg (instalado y accesible desde línea de comandos)
* Conexión a internet para scraping y descarga
* Perfil de Firefox configurado para evitar ciertos bloqueos (ruta en `profile_path` en `auto_park.py`)

---

## Uso

### 1. Obtener el archivo JSON con episodios

Ejecuta:

```bash
python south_scrapper.py
```

Esto creará `all_southpark_episodes.json` con la estructura:

```json
[
  {
    "temporada": 1,
    "numero": 1,
    "nombre": "Cartman consigue una sonda anal",
    "url_es": "https://www.southpark.lat/episodios/940f8z/south-park-cartman-consigue-una-sonda-anal-temporada-1-ep-1",
    "url_en": "https://www.southpark.lat/en/episodes/940f8z/south-park-cartman-consigue-una-sonda-anal-temporada-1-ep-1"
  },
  ...
]
```

---

### 2. Descargar episodios con audio en español e inglés

Ejecuta:

```bash
python auto_park.py
```

* Asegúrate de modificar la variable `profile_path` para apuntar a tu perfil de Firefox local.
* Los archivos se descargarán en la carpeta `descargas`, organizados en subcarpetas por temporada.
* El script detecta enlaces `.m3u8` para video y audio, descarga y los fusiona usando FFmpeg.
* En caso de error, podrás decidir si reintentar o saltar el episodio.

---

## Detalles técnicos

* Se usa Selenium Wire para interceptar las peticiones HTTP y obtener los enlaces de streaming (video/audio).
* FFmpeg descarga y fusiona los streams sin recodificar para mantener calidad original.
* Las URLs en inglés se corrigen para apuntar a la ruta `/en/episodes/` para evitar problemas de idioma.
* El script `south_scrapper.py` maneja paginación para obtener todos los episodios de cada temporada.
* `auto_park.py` permite seleccionar calidad 720p o 1080p si está disponible.

---

## Advertencias y notas

* El scraping y descarga dependen de la estructura actual de la web `southpark.lat`, que puede cambiar en cualquier momento.
* Este proyecto es solo para uso personal y educativo. Respeta siempre los términos de servicio y derechos de autor.
* Asegúrate de tener suficiente espacio en disco para almacenar episodios completos.
* El perfil de Firefox debe permitir reproducir videos sin intervención de captcha o bloqueos.
* El script puede tardar bastante tiempo en descargar toda la serie completa.

---

## Archivos principales

* `south_scrapper.py`: Obtiene temporadas, episodios y URLs en español e inglés.
* `auto_park.py`: Automatiza la descarga y fusión de streams para cada episodio.
* `all_southpark_episodes.json`: Archivo generado con la lista completa de episodios y URLs.

---

## Ejemplo de configuración `profile_path` en `auto_park.py`

```python
profile_path = r"C:\Users\mikey\AppData\Roaming\Mozilla\Firefox\Profiles\r7l8sa9w.default-release"
```

Modifica según tu sistema operativo y perfil Firefox.

---

## Licencia

Este proyecto es de uso personal y educativo. No distribuyas ni publiques contenidos protegidos sin permiso.

---

¡Disfruta descargando South Park con audio multilenguaje!
