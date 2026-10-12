import os
import sys


def hay_datos(carpeta):
    if not os.path.isdir(carpeta):
        return False
    for nombre in os.listdir(carpeta):
        if nombre.startswith("events_") and nombre.endswith(".log"):
            return True
    return False


def copiar_bitacora_web(origen="datos_web", destino="logs"):
    # solo en el navegador: ahi el sistema de archivos empieza vacio
    if sys.platform != "emscripten":
        return
    if hay_datos(destino) or not os.path.isdir(origen):
        return
    os.makedirs(destino, exist_ok=True)
    for nombre in sorted(os.listdir(origen)):
        if nombre.startswith("events_") and nombre.endswith(".log"):
            with open(os.path.join(origen, nombre), "r", encoding="utf-8") as src:
                with open(os.path.join(destino, nombre), "a", encoding="utf-8") as dst:
                    for linea in src:
                        dst.write(linea)