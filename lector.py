import os

CLAVES_NUM = ["score", "level", "duration", "amount", "wave", "time"]


def parse_linea(linea):
    if not linea.endswith("\n"):
        return None
    partes = linea.strip().split("|")
    if len(partes) != 4:
        return None
    if partes[1] == "" or partes[2] == "":
        return None
    try:
        ts = float(partes[0])
        params = {}
        if partes[3] != "":
            for par in partes[3].split(";"):
                clave, valor = par.split("=")
                if clave == "" or valor == "":
                    return None
                if clave in CLAVES_NUM:
                    valor = float(valor)
                params[clave] = valor
    except ValueError:
        return None
    return {"ts": ts, "ses": partes[1], "tipo": partes[2], "params": params}


def archivos_de(carpeta):
    if not os.path.isdir(carpeta):
        return []
    lista = []
    for nombre in os.listdir(carpeta):
        if nombre.startswith("events_") and nombre.endswith(".log"):
            lista.append(os.path.join(carpeta, nombre))
    return lista


def iter_events(carpeta, rep):
    rep["archivos"] = 0
    rep["leidas"] = 0
    rep["validas"] = 0
    rep["corruptas"] = 0
    rep["incompletas"] = 0
    abiertas = set()
    for ruta in sorted(archivos_de(carpeta)):
        rep["archivos"] += 1
        with open(ruta, "r", encoding="utf-8", errors="replace") as arch:
            for linea in arch:
                rep["leidas"] += 1
                ev = parse_linea(linea)
                if ev is None:
                    rep["corruptas"] += 1
                else:
                    rep["validas"] += 1
                    if ev["tipo"] == "SESSION_START":
                        abiertas.add(ev["ses"])
                    elif ev["tipo"] == "SESSION_END":
                        abiertas.discard(ev["ses"])
                    yield ev
    rep["incompletas"] = len(abiertas)


if __name__ == "__main__":
    rep = {}
    for ev in iter_events("logs", rep):
        pass
    print(rep)