import sys

from lector import iter_events
from estadistica import (Descriptivas, Frecuencias, Correlacion, Embudo,
                         PorDificultad, Histograma, cuartiles, percentil,
                         atipicos_iqr, atipicos_z)


def analizar(carpeta):
    rep = {}
    d_punt = Descriptivas()
    d_dur = Descriptivas()
    d_dano = Descriptivas()
    causas = Frecuencias()
    embudo = Embudo()
    por_dif = PorDificultad()
    r_dur_punt = Correlacion()
    r_dano_niv = Correlacion()
    puntajes = []   # estas tres listas las piden la mediana y los cuartiles
    dur_l = []
    dano_l = []
    dif_de = {}     # dificultad de las sesiones abiertas
    dano_de = {}    # dano acumulado de las sesiones abiertas

    # Recorrido 1
    for ev in iter_events(carpeta, rep):
        tipo = ev["tipo"]
        p = ev["params"]
        ses = ev["ses"]
        if tipo == "SESSION_START":
            dif_de[ses] = p.get("difficulty", "normal")
            dano_de[ses] = 0.0
        elif tipo == "DAMAGE_TAKEN":
            if "amount" in p:
                d_dano.agregar(p["amount"])
                dano_l.append(p["amount"])
                if ses in dano_de:
                    dano_de[ses] += p["amount"]
        elif tipo == "PLAYER_DEATH":
            if "cause" in p:
                causas.agregar(p["cause"])
        elif tipo == "SESSION_END":
            if "score" in p and "duration" in p and "level" in p:
                d_punt.agregar(p["score"])
                d_dur.agregar(p["duration"])
                puntajes.append(p["score"])
                dur_l.append(p["duration"])
                embudo.agregar(p["level"])
                r_dur_punt.agregar(p["duration"], p["score"])
                if ses in dif_de:
                    por_dif.agregar(dif_de[ses], p["score"])
                if ses in dano_de:
                    r_dano_niv.agregar(dano_de[ses], p["level"])
            dif_de.pop(ses, None)
            dano_de.pop(ses, None)

    # Recorrido 2: el histograma necesita saber el minimo y el maximo antes
    hist = None
    if d_punt.n > 0:
        hist = Histograma(d_punt.minimo, d_punt.maximo, 8)
        for ev in iter_events(carpeta, {}):
            p = ev["params"]
            if (ev["tipo"] == "SESSION_END" and "score" in p
                    and "duration" in p and "level" in p):
                hist.agregar(p["score"])

    res = {"rep": rep, "punt": d_punt, "dur": d_dur, "dano": d_dano,
           "causas": causas, "embudo": embudo, "dif": por_dif,
           "r1": r_dur_punt, "r2": r_dano_niv, "hist": hist,
           "puntajes": puntajes, "dur_l": dur_l, "dano_l": dano_l}
    if len(puntajes) >= 4:
        res["cuart"] = cuartiles(puntajes)
        res["p90"] = percentil(puntajes, 90)
        res["iqr"] = atipicos_iqr(puntajes)
        res["z"] = atipicos_z(puntajes)
    return res


def linea_desc(nombre, d):
    if d.n == 0:
        print(nombre, ": sin datos")
        return
    print(f"{nombre}: n={d.n} suma={d.suma:.1f} min={d.minimo} max={d.maximo} "
          f"media={d.media():.2f} desv={d.desv():.2f} cv={d.cv():.1f}%")


def mostrar(res):
    print("CALIDAD DE DATOS", res["rep"])
    print()
    linea_desc("Puntaje", res["punt"])
    linea_desc("Duracion", res["dur"])
    linea_desc("Dano", res["dano"])
    if "cuart" in res:
        q1, q2, q3 = res["cuart"]
        print(f"Mediana={q2} Q1={q1} Q3={q3} IQR={q3 - q1} P90={res['p90']}")
        print("Atipicos IQR:", res["iqr"][2], " Atipicos z:", res["z"])
    print()
    print("CAUSAS DE MUERTE  f  f%  F%")
    for valor, f, pct, acum in res["causas"].tabla():
        print(f"{valor:12} {f:5} {pct:5.1f}% {acum:5.1f}%")
    print()
    if res["hist"] is not None:
        print("HISTOGRAMA DE PUNTAJE")
        for ini, fin, c in res["hist"].intervalos():
            print(f"{ini:8.0f} - {fin:8.0f} {c:4} {'#' * min(c, 50)}")
    print()
    print("NIVEL SESIONES SUPERVIVENCIA ABANDONO")
    for nivel, alcanz, sup, aband in res["embudo"].tabla():
        ab = "-" if aband is None else f"{aband:.1f}%"
        print(f"{nivel:5} {alcanz:8} {sup:11.1f}% {ab:>8}")
    print()
    print("r duracion vs puntaje:", round(res["r1"].r(), 4))
    print("r dano vs nivel:", round(res["r2"].r(), 4))
    print()
    for nombre in ["easy", "hard"]:
        g = res["dif"].grupos[nombre]
        if g.n > 0:
            print(f"{nombre}: n={g.n} media={g.media():.1f} desv={g.desv():.1f}")


if __name__ == "__main__":
    carpeta = "logs_sint"
    if len(sys.argv) > 1:
        carpeta = sys.argv[1]
    mostrar(analizar(carpeta))