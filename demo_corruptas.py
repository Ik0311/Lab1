import os

from lector import iter_events

ORIGEN = "datos_web"
DEMO = "logs_demo"
VACIA = "carpeta_vacia_demo"

# (que es, la linea que se agrega a proposito)
MALAS = [
    ("linea vacia", "\n"),
    ("linea con solo espacios", "   \n"),
    ("menos de 4 campos", "1760000000.000|S9999|ENEMY_KILL\n"),
    ("mas de 4 campos", "1760000000.000|S9999|ENEMY_KILL|type=robot|extra\n"),
    ("parametro sin signo igual", "1760000001.000|S9999|ENEMY_KILL|type=robot;wave\n"),
    ("parametro con valor vacio", "1760000002.000|S9999|ENEMY_KILL|type=;wave=1\n"),
    ("numero que no se puede convertir",
     "1760000003.000|S9999|SESSION_END|score=abc;level=2;duration=5;result=death\n"),
    ("ultima linea truncada (sin salto de linea)",
     "1760000004.000|S9999|ENEMY_KILL|type=rob"),
]


def pausa():
    input("\nPresiona Enter para continuar...")


def leer(carpeta):
    rep = {}
    for ev in iter_events(carpeta, rep):
        pass
    return rep


def mostrar(titulo, rep):
    n = rep["leidas"]
    pv = rep["validas"] * 100 / n if n else 0.0
    pc = rep["corruptas"] * 100 / n if n else 0.0
    print(titulo)
    print("  Archivos procesados:", rep["archivos"])
    print("  Lineas leidas:", n)
    print(f"  Eventos validos: {rep['validas']} ({pv:.2f}%)")
    print(f"  Lineas corruptas: {rep['corruptas']} ({pc:.2f}%)")
    print("  Sesiones incompletas:", rep["incompletas"])


def preparar_demo():
    # copia la bitacora a logs_demo (linea por linea) y le agrega las lineas malas
    if os.path.isdir(DEMO):
        for nombre in os.listdir(DEMO):
            os.remove(os.path.join(DEMO, nombre))
    else:
        os.makedirs(DEMO)
    copiados = []
    for nombre in sorted(os.listdir(ORIGEN)):
        if nombre.startswith("events_") and nombre.endswith(".log"):
            ultima = "\n"
            with open(os.path.join(ORIGEN, nombre), "r", encoding="utf-8") as src:
                with open(os.path.join(DEMO, nombre), "w", encoding="utf-8") as dst:
                    for linea in src:
                        dst.write(linea)
                        ultima = linea
                    if not ultima.endswith("\n"):
                        dst.write("\n")
            copiados.append(nombre)
    ultimo = copiados[-1]
    with open(os.path.join(DEMO, ultimo), "a", encoding="utf-8") as dst:
        for nombre, linea in MALAS:
            dst.write(linea)


def main():
    if not os.path.isdir(ORIGEN):
        print("No encuentro la carpeta", ORIGEN)
        return

    print("PASO 1: la bitacora real, sin tocar\n")
    base = leer(ORIGEN)
    mostrar("Reporte de calidad:", base)
    pausa()

    print("\nPASO 2: copio la bitacora a", DEMO, "y le agrego", len(MALAS), "lineas danadas a proposito\n")
    preparar_demo()
    for i, (nombre, linea) in enumerate(MALAS, 1):
        print(f"  {i}. {nombre}: {linea!r}")
    pausa()

    print("\nPASO 3: leo la bitacora danada (el programa no se debe caer)\n")
    rep = leer(DEMO)
    mostrar("Reporte de calidad:", rep)
    ok_corruptas = rep["corruptas"] == len(MALAS)
    ok_validas = rep["validas"] == base["validas"]
    print()
    print("  Lineas corruptas detectadas:", rep["corruptas"], "de", len(MALAS),
          "agregadas ->", "OK" if ok_corruptas else "FALLO")
    print("  Eventos validos sin cambios:", rep["validas"], "de", base["validas"],
          "->", "OK" if ok_validas else "FALLO")
    pausa()

    print("\nPASO 4: carpeta que no existe y carpeta vacia\n")
    rep1 = leer("carpeta_que_no_existe")
    print("  Carpeta que no existe -> eventos validos:", rep1["validas"], "(sin errores)")
    os.makedirs(VACIA, exist_ok=True)
    rep2 = leer(VACIA)
    os.rmdir(VACIA)
    print("  Carpeta vacia -> eventos validos:", rep2["validas"], "(sin errores)")

    print("\nListo. La bitacora danada quedo en", DEMO)


if __name__ == "__main__":
    main()