import asyncio
import pygame

from analisis import analizar
from estadistica import mediana_de, percentil

ANCHO = 800
ALTO = 450
PESTANAS = ["Resumen", "Distribucion", "Relacion"]
VARIABLES = ["Puntaje", "Duracion", "Dano recibido"]


def lineas_resumen(res, i):
    descs = [res["punt"], res["dur"], res["dano"]]
    listas = [res["puntajes"], res["dur_l"], res["dano_l"]]
    d = descs[i]
    lista = listas[i]
    if d.n == 0:
        return ["Sin datos para esta variable"]
    return [f"n = {d.n}",
            f"Media = {d.media():.2f}",
            f"Mediana = {mediana_de(sorted(lista)):.2f}",
            f"Desviacion estandar = {d.desv():.2f}",
            f"Coef. de variacion = {d.cv():.1f} %",
            f"Minimo = {d.minimo}",
            f"Maximo = {d.maximo}",
            f"Percentil 90 = {percentil(lista, 90)}"]


def lineas_calidad(rep):
    leidas = rep.get("leidas", 0)
    validas = rep.get("validas", 0)
    corruptas = rep.get("corruptas", 0)
    pv = validas * 100 / leidas if leidas else 0.0
    pc = corruptas * 100 / leidas if leidas else 0.0
    return ["REPORTE DE CALIDAD DE DATOS",
            f"Archivos procesados: {rep.get('archivos', 0)}",
            f"Lineas leidas: {leidas}",
            f"Eventos validos: {validas} ({pv:.2f}%)",
            f"Lineas corruptas: {corruptas} ({pc:.2f}%)",
            f"Sesiones incompletas: {rep.get('incompletas', 0)}"]


async def pantalla_stats(pant, carpeta):
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 32)
    fuente_p = pygame.font.Font(None, 22)
    fuente_t = pygame.font.Font(None, 28)
    res = analizar(carpeta)
    pestana = 0
    var = 0
    ver_calidad = False
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if ver_calidad:
                        ver_calidad = False
                    else:
                        return
                elif ev.key == pygame.K_RIGHT:
                    pestana = (pestana + 1) % 3
                elif ev.key == pygame.K_LEFT:
                    pestana = (pestana - 1) % 3
                elif ev.key == pygame.K_v:
                    var = (var + 1) % 3
                elif ev.key == pygame.K_c:
                    ver_calidad = not ver_calidad

        pant.fill((20, 20, 40))
        for i, nombre in enumerate(PESTANAS):
            r = pygame.Rect(20 + i * 170, 15, 160, 34)
            color = (60, 140, 255) if i == pestana else (60, 60, 90)
            pygame.draw.rect(pant, color, r)
            img = fuente_t.render(nombre, True, (255, 255, 255))
            pant.blit(img, (r.centerx - img.get_width() // 2, r.y + 8))

        if pestana == 0:
            t = fuente.render(f"Variable: {VARIABLES[var]}", True, (255, 220, 80))
            pant.blit(t, (30, 75))
            y = 120
            for txt in lineas_resumen(res, var):
                img = fuente.render(txt, True, (255, 255, 255))
                pant.blit(img, (50, y))
                y += 36
        else:
            img = fuente.render("(en construccion)", True, (200, 200, 200))
            pant.blit(img, (50, 120))

        ayuda = fuente_p.render(
            "Izq/der: pestana   V: variable   C: calidad de datos   Esc: volver",
            True, (150, 150, 170))
        pant.blit(ayuda, (20, ALTO - 28))

        if ver_calidad:
            panel = pygame.Rect(120, 90, 560, 250)
            pygame.draw.rect(pant, (35, 35, 70), panel)
            pygame.draw.rect(pant, (255, 220, 80), panel, 2)
            y = panel.y + 20
            for txt in lineas_calidad(res["rep"]):
                img = fuente.render(txt, True, (255, 255, 255))
                pant.blit(img, (panel.x + 25, y))
                y += 36

        pygame.display.flip()
        reloj.tick(30)
        await asyncio.sleep(0)