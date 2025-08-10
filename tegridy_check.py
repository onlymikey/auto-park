import os
import subprocess
import sys

# Tiempo máximo (en segundos) para que ffmpeg analice un archivo
TIMEOUT = 60

def is_corrupt(file_path):
    try:
        result = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", file_path, "-f", "null", "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT
        )
        errors = result.stderr.decode("utf-8", errors="ignore").strip()
        return bool(errors)  # Si hay errores en stderr, lo marcamos como dañado
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {file_path}")
        return True
    except Exception as e:
        print(f"[ERROR] {file_path} -> {e}")
        return True

def main():
    root_folder = os.path.dirname(os.path.abspath(__file__))
    damaged_files = []

    for folder, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith((".mp4", ".mkv", ".avi", ".mov")):
                full_path = os.path.join(folder, file)
                print(f"Analizando: {full_path}")
                if is_corrupt(full_path):
                    damaged_files.append(full_path)

    print("\n===== RESULTADO =====")
    if damaged_files:
        print(f"Se encontraron {len(damaged_files)} archivos posiblemente dañados:")
        for f in damaged_files:
            print(f"  - {f}")
    else:
        print("No se detectaron archivos dañados.")

if __name__ == "__main__":
    main()
