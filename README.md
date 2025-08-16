# Auto Park

Proyecto educativo que demuestra cómo automatizar la recopilación de metadatos de episodios desde la web de [southpark.lat](https://www.southpark.lat), trabajar con flujos de video/audio y validar archivos multimedia usando **Python**, **Selenium**, **BeautifulSoup** y **FFmpeg**.

⚠️ **Aviso importante**: Este proyecto no está destinado a incentivar la descarga de contenido con derechos de autor. Está diseñado con fines **técnicos, de aprendizaje y experimentación personal** en web scraping, automatización y manejo de streams multimedia.

---

## Descripción general

Este proyecto contiene tres scripts principales:

1. **`south_scrapper.py`** – recopilación de metadatos de episodios.
2. **`autopark.py`** – automatización de la detección de streams y combinación de audio/video.
3. **`tegridy_check.py`** – verificación de integridad de archivos de video.

A continuación se describe el funcionamiento y los detalles de cada script.

---

## 1. `south_scrapper.py`

Este script se encarga de obtener la información estructurada de **todas las temporadas y episodios** de South Park, tanto en español como en inglés.

### Funcionalidad:

* Accede a la página de cada temporada en [southpark.lat](https://www.southpark.lat).
* Extrae los identificadores internos (*MGID*) asociados a cada temporada.
* Consulta la API pública del sitio para obtener la lista de episodios y sus metadatos (títulos, número de episodio, URLs).
* Une los datos en un único archivo `all_southpark_episodes.json` con la estructura:

```json
[
  {
    "temporada": 1,
    "numero": 1,
    "nombre": "Cartman consigue una sonda anal",
    "url_es": "https://www.southpark.lat/episodios/940f8z/...",
    "url_en": "https://www.southpark.lat/en/episodes/940f8z/..."
  },
  ...
]
```

### Detalles técnicos:

* Usa **requests** y **BeautifulSoup** para el scraping.
* Maneja **paginación** de episodios y corrige URLs para idioma inglés.
* Agrega un ejemplo manual para la temporada 1 debido a una estructura especial en el sitio.
* Maneja tanto temporadas en español como en inglés, y las combina por número de episodio.

---

## 2. `autopark.py`

Automatiza la **detección de streams** y la **combinación de pistas de audio/video** usando Selenium y FFmpeg.

### Funcionalidad:

1. **Carga de episodios**

   * Abre Firefox mediante Selenium Wire.
   * Carga la página del episodio en español y en inglés.
   * Interactúa con el reproductor para iniciar reproducción y seleccionar calidad HD.

2. **Captura de enlaces `.m3u8`**

   * Intercepta peticiones de red para obtener URLs de video y audio.
   * Filtra la mejor calidad de video (por ejemplo 1080p) y los streams de audio en español e inglés.

3. **Descarga y combinación de streams**

   * Usa FFmpeg para descargar video y audio por separado.
   * Fusiona en un solo archivo `.mkv` con pistas de audio multilenguaje.
   * Organiza los episodios en carpetas por temporada.

4. **Gestión de errores y validación**

   * Detecta si el archivo ya existe y si cumple con la resolución deseada (1080p).
   * Reintenta descargas fallidas hasta 3 veces con pausas configurables.
   * Mantiene un log detallado (`descargas.log`) con estado de cada episodio.

### Detalles técnicos:

* **Selenium Wire** intercepta todas las peticiones HTTP para capturar flujos `.m3u8`.
* **FFmpeg** se usa en modo copia (`-c copy`) para no recodificar y mantener la calidad original.
* Función `filter_streams` selecciona el mejor stream de video por MTP (Media Time Point) y el primer stream de audio disponible.
* `sanitize_filename` asegura que los nombres de archivo sean válidos en el sistema operativo.
* Soporta selección de calidad 720p o 1080p si está disponible.

---

## 3. `tegridy_check.py`

Verifica la **integridad de archivos de video** en la carpeta del proyecto.

### Funcionalidad:

* Recorre directorios buscando archivos de video (`.mp4`, `.mkv`, `.avi`, `.mov`).
* Analiza cada archivo usando FFmpeg para detectar posibles errores de corrupción o incompletitud.
* Muestra un reporte final indicando los archivos potencialmente dañados.

### Detalles técnicos:

* Usa un **timeout** para evitar bloqueos prolongados al analizar archivos grandes.
* Interpreta los errores que FFmpeg reporta en stderr como posibles corrupciones.
* Permite revisar rápidamente la salud de una colección de archivos multimedia.

---

## Requisitos

* **Python 3.8+**
* **Firefox** y **Geckodriver** en PATH
* Librerías Python:

  ```bash
  pip install selenium selenium-wire beautifulsoup4 requests
  ```
* **FFmpeg** (instalado y accesible desde línea de comandos)
* Conexión a internet para ejecutar scraping y acceder a los streams
* Perfil de Firefox válido y configurado para reproducción sin bloqueos (ruta en `profile_path`)

---

## Ejemplo de uso

### 1. Generar archivo JSON con episodios

```bash
python south_scrapper.py
```

→ Crea `all_southpark_episodes.json` con temporadas, episodios y URLs.

### 2. Automatizar descarga y combinación de streams

```bash
python autopark.py
```

* Configura `profile_path` con tu perfil de Firefox.
* Los episodios se organizan en carpetas `descargas/Season XX/`.
* Los logs quedan registrados en `descargas.log`.

### 3. Verificar integridad de archivos de video

```bash
python tegridy_check.py
```

* Muestra un listado de archivos con posibles errores de corrupción.

---

## Detalles técnicos avanzados

* **Logs y reintentos**: `autopark.py` maneja reintentos automáticos y registra cada paso con timestamps.
* **Selección de streams**: Filtra video por MTP y audio por idioma.
* **Validación de resolución**: Función `es_1080p` usa FFprobe para verificar resolución mínima requerida.
* **Manejo de nombres de archivo**: `sanitize_filename` reemplaza caracteres inválidos para evitar errores de filesystem.

---

## Advertencias y notas

* La estructura del sitio puede cambiar, lo que podría romper los scripts.
* Este proyecto **es solo educativo y técnico**.
* No distribuyas contenido descargado sin permiso.
* Asegúrate de tener suficiente espacio en disco para almacenar archivos grandes.
* La descarga de episodios completos puede tardar considerablemente dependiendo del número de temporadas y la velocidad de internet.
* Configura correctamente tu perfil de Firefox para evitar captchas o bloqueos de reproducción.

---

## Archivos principales

| Archivo                       | Función                                                               |
| ----------------------------- | --------------------------------------------------------------------- |
| `south_scrapper.py`           | Obtiene temporadas, episodios y URLs en español e inglés.             |
| `autopark.py`                 | Automatiza la obtención de streams, descarga y combinación de pistas. |
| `tegridy_check.py`            | Analiza archivos de video y detecta corrupción.                       |
| `all_southpark_episodes.json` | JSON generado con metadatos completos de episodios.                   |

---

## Ejemplo de configuración `profile_path` en `autopark.py`

```python
profile_path = r"C:\Users\mikey\AppData\Roaming\Mozilla\Firefox\Profiles\123456abcd.default-release"
```

Modifica según tu sistema operativo y perfil Firefox.

---

## Licencia

* Uso **personal y educativo**.
* No redistribuir contenido protegido por derechos de autor obtenido mediante estos ejemplos.


