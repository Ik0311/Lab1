import json
import os

RUTA = "config.json"
POR_DEFECTO = {"player": "jugador", "volume": 80, "difficulty": "normal"}


def cargar():
    cfg = dict(POR_DEFECTO)
    if os.path.exists(RUTA):
        try:
            with open(RUTA, "r", encoding="utf-8") as arch:
                datos = json.load(arch)
            for k in POR_DEFECTO:
                if k in datos:
                    cfg[k] = datos[k]
        except (ValueError, OSError):
            pass
    return cfg


def guardar(cfg):
    with open(RUTA, "w", encoding="utf-8") as arch:
        json.dump(cfg, arch, indent=2)