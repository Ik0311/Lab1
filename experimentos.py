import os
import random
import time
import tracemalloc

import pygame

from generador import una_sesion
from lector import iter_events
from telemetria import EscritorBitacora

CARPETA = "exp"
SALIDA = "resultados"
TEXTO = []


def decir(linea=""):
    print(linea)
    TEXTO.append(linea)


def limpiar(carpeta):
    if os.path.isdir(carpeta):
        for nombre in os.listdir(carpeta):
            os.remove(os.path.join(carpeta, nombre))
    else:
        os.makedirs(carpeta)


def tamano_total(carpeta):
    total = 0
    for nombre in os.listdir(carpeta):
        total += os.path.getsize(os.path.join(carpeta, nombre))
    return total


class Tope:
    # deja pasar eventos hasta llegar a n y descarta el resto
    def __init__(self, esc, n):
        self.esc = esc
        self.n = n
        self.cuenta = 0

    def registrar(self, id_ses, tipo_ev, **params):
        if self.cuenta < self.n:
            self.esc.registrar(id_ses, tipo_ev, **params)
            self.cuenta += 1


#  Experimento A 
def escribir_fijo(carpeta, n, n_buf):
    esc = EscritorBitacora(carpeta, n_buf=n_buf)
    t0 = time.perf_counter()
    for _ in range(n):
        esc.registrar("S0001", "ENEMY_KILL", type="slime", wave=1)
    esc.cerrar()
    return time.perf_counter() - t0


def experimento_a():
    carpeta = os.path.join(CARPETA, "a")
    resultados = []
    for n_buf in [1, 10, 100, 1000]:
        tiempos = []
        for _ in range(3):
            limpiar(carpeta)
            tiempos.append(escribir_fijo(carpeta, 100000, n_buf))
        resultados.append((n_buf, sum(tiempos) / len(tiempos)))
    limpiar(carpeta)
    return resultados


#  Experimentos B y C 
def generar_n(carpeta, n, n_buf=100):
    random.seed(42)
    limpiar(carpeta)
    esc = EscritorBitacora(carpeta, n_buf=n_buf)
    tope = Tope(esc, n)
    t0 = time.perf_counter()
    i = 0
    while tope.cuenta < n:
        i += 1
        una_sesion(tope, f"S{i:05d}")
    esc.cerrar()
    return time.perf_counter() - t0


def leer(carpeta):
    rep = {}
    t0 = time.perf_counter()
    for ev in iter_events(carpeta, rep):
        pass
    return time.perf_counter() - t0, rep


def tiempo_lista(carpeta):
    rep = {}
    t0 = time.perf_counter()
    lista = list(iter_events(carpeta, rep))
    return time.perf_counter() - t0


def mem_perezosa(carpeta):
    tracemalloc.start()
    rep = {}
    for ev in iter_events(carpeta, rep):
        pass
    pico = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return pico


def mem_lista(carpeta):
    tracemalloc.start()
    rep = {}
    lista = list(iter_events(carpeta, rep))
    pico = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return pico


def experimentos_b_c():
    filas = []
    for n in [5000, 50000, 100000]:
        carpeta = os.path.join(CARPETA, f"n{n}")
        t_esc = generar_n(carpeta, n)
        tam = tamano_total(carpeta)
        t_lec, rep = leer(carpeta)
        t_lis = tiempo_lista(carpeta)
        m_per = mem_perezosa(carpeta)
        m_lis = mem_lista(carpeta)
        filas.append({"n": n, "tam": tam / 1024, "t_esc": t_esc,
                      "t_lec": t_lec, "t_lis": t_lis,
                      "eps": rep["validas"] / t_lec,
                      "us": t_lec * 1000000 / rep["leidas"],
                      "m_per": m_per / 1024, "m_lis": m_lis / 1024})
        limpiar(carpeta)
    return filas


#  Figuras dibujadas con Pygame     
def figura_lineas(ruta, titulo, etiquetas, valores, eje_x, eje_y):
    f = pygame.font.Font(None, 24)
    ft = pygame.font.Font(None, 30)
    sup = pygame.Surface((640, 400))
    sup.fill((255, 255, 255))
    negro = (0, 0, 0)
    azul = (30, 90, 200)
    x0 = 80
    y0 = 60
    w = 520
    h = 270
    vmax = max(valores) * 1.15
    pygame.draw.line(sup, negro, (x0, y0 + h), (x0 + w, y0 + h), 2)
    pygame.draw.line(sup, negro, (x0, y0), (x0, y0 + h), 2)
    t = ft.render(titulo, True, negro)
    sup.blit(t, (320 - t.get_width() // 2, 10))
    t = f.render(eje_y, True, negro)
    sup.blit(t, (10, 36))
    t = f.render(eje_x, True, negro)
    sup.blit(t, (x0 + w // 2 - t.get_width() // 2, y0 + h + 36))
    puntos = []
    n = len(valores)
    for i in range(n):
        x = x0 + int((i + 0.5) * w / n)
        y = y0 + h - int(valores[i] / vmax * h)
        puntos.append((x, y))
        e = f.render(etiquetas[i], True, negro)
        sup.blit(e, (x - e.get_width() // 2, y0 + h + 8))
    pygame.draw.lines(sup, azul, False, puntos, 3)
    for i in range(n):
        x, y = puntos[i]
        pygame.draw.circle(sup, azul, (x, y), 6)
        v = f.render(f"{valores[i]:.2f}", True, negro)
        sup.blit(v, (x - v.get_width() // 2, y - 26))
    pygame.image.save(sup, ruta)


def figura_barras(ruta, titulo, grupos, series, eje_x, eje_y):
    f = pygame.font.Font(None, 24)
    ft = pygame.font.Font(None, 30)
    sup = pygame.Surface((640, 400))
    sup.fill((255, 255, 255))
    negro = (0, 0, 0)
    x0 = 80
    y0 = 60
    w = 520
    h = 270
    vmax = 0
    for nombre, vals, color in series:
        vmax = max(vmax, max(vals))
    vmax = vmax * 1.15
    pygame.draw.line(sup, negro, (x0, y0 + h), (x0 + w, y0 + h), 2)
    pygame.draw.line(sup, negro, (x0, y0), (x0, y0 + h), 2)
    t = ft.render(titulo, True, negro)
    sup.blit(t, (320 - t.get_width() // 2, 10))
    t = f.render(eje_y, True, negro)
    sup.blit(t, (10, 36))
    t = f.render(eje_x, True, negro)
    sup.blit(t, (x0 + w // 2 - t.get_width() // 2, y0 + h + 36))
    ng = len(grupos)
    ns = len(series)
    ancho_g = w / ng
    ancho_b = ancho_g * 0.7 / ns
    for gi in range(ng):
        e = f.render(grupos[gi], True, negro)
        sup.blit(e, (x0 + int((gi + 0.5) * ancho_g) - e.get_width() // 2, y0 + h + 8))
        for si in range(ns):
            nombre, vals, color = series[si]
            alto = int(vals[gi] / vmax * h)
            x = x0 + int(gi * ancho_g + ancho_g * 0.15 + si * ancho_b)
            r = pygame.Rect(x, y0 + h - alto, int(ancho_b) - 2, alto)
            pygame.draw.rect(sup, color, r)
            v = f.render(f"{vals[gi]:.0f}", True, negro)
            sup.blit(v, (r.centerx - v.get_width() // 2, r.y - 18))
    for si in range(ns):
        nombre, vals, color = series[si]
        pygame.draw.rect(sup, color, (420, 38 + si * 20, 14, 14))
        t = f.render(nombre, True, negro)
        sup.blit(t, (440, 36 + si * 20))
    pygame.image.save(sup, ruta)


def main():
    pygame.font.init()
    os.makedirs(SALIDA, exist_ok=True)

    decir("EXPERIMENTO A: escritura de 100000 eventos (promedio de 3 corridas)")
    decir(f"{'Buffer':>8} {'Tiempo (s)':>12}")
    res_a = experimento_a()
    etiquetas = []
    valores = []
    for n_buf, seg in res_a:
        decir(f"{n_buf:>8} {seg:>12.3f}")
        etiquetas.append(str(n_buf))
        valores.append(seg)
    figura_lineas(os.path.join(SALIDA, "figura_A.png"),
                  "Tiempo de escritura vs tamano de buffer",
                  etiquetas, valores, "Tamano del buffer (lineas)", "Tiempo (s)")
    decir()

    filas = experimentos_b_c()

    decir("EXPERIMENTO B: rendimiento de lectura")
    decir(f"{'Eventos':>8} {'T. lectura (s)':>15} {'Eventos/s':>12} {'us por linea':>13}")
    for fila in filas:
        decir(f"{fila['n']:>8} {fila['t_lec']:>15.3f} {fila['eps']:>12.0f} {fila['us']:>13.2f}")
    decir()

    decir("EXPERIMENTO C: lectura perezosa contra carga completa")
    decir(f"{'Eventos':>8} {'T. perezosa (s)':>16} {'T. lista (s)':>13} "
          f"{'Mem. perezosa (KiB)':>20} {'Mem. lista (KiB)':>17}")
    for fila in filas:
        decir(f"{fila['n']:>8} {fila['t_lec']:>16.3f} {fila['t_lis']:>13.3f} "
              f"{fila['m_per']:>20.1f} {fila['m_lis']:>17.1f}")
    decir()

    decir("TABLA RESUMEN")
    decir(f"{'Eventos':>8} {'Archivo (KiB)':>14} {'T. escritura (s)':>17} {'T. lectura (s)':>15} "
          f"{'Eventos/s':>10} {'Mem. perezosa (KiB)':>20} {'Mem. lista (KiB)':>17}")
    grupos = []
    perezosa = []
    lista = []
    for fila in filas:
        decir(f"{fila['n']:>8} {fila['tam']:>14.1f} {fila['t_esc']:>17.3f} {fila['t_lec']:>15.3f} "
              f"{fila['eps']:>10.0f} {fila['m_per']:>20.1f} {fila['m_lis']:>17.1f}")
        grupos.append(str(fila["n"]))
        perezosa.append(fila["m_per"])
        lista.append(fila["m_lis"])
    figura_barras(os.path.join(SALIDA, "figura_C.png"),
                  "Memoria: lectura perezosa vs lista completa", grupos,
                  [("Perezosa", perezosa, (30, 90, 200)),
                   ("Lista", lista, (220, 80, 60))],
                  "Eventos en la bitacora", "Memoria pico (KiB)")

    with open(os.path.join(SALIDA, "resultados.txt"), "w", encoding="utf-8") as arch:
        arch.write("\n".join(TEXTO))
    decir()
    decir("Listo: revisa la carpeta resultados")


if __name__ == "__main__":
    main()