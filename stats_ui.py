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


def boton(pant, fuente, rect, texto, activo=False):
    pos = pygame.mouse.get_pos()
    if activo:
        color = (60, 140, 255)
    elif rect.collidepoint(pos):
        color = (80, 80, 130)
    else:
        color = (50, 50, 85)
    pygame.draw.rect(pant, color, rect)
    img = fuente.render(texto, True, (255, 255, 255))
    pant.blit(img, (rect.centerx - img.get_width() // 2,
                    rect.centery - img.get_height() // 2))


async def pantalla_stats(pant, carpeta):
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 32)
    fuente_t = pygame.font.Font(None, 28)
    res = analizar(carpeta)
    pestana = 0
    var = 0
    ver_calidad = False

    r_tabs = []
    for i in range(3):
        r_tabs.append(pygame.Rect(20 + i * 170, 15, 160, 34))
    r_var = pygame.Rect(30, 65, 330, 36)
    r_cal = pygame.Rect(20, 400, 220, 36)
    r_volver = pygame.Rect(ANCHO - 180, 400, 160, 36)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if ver_calidad:
                    ver_calidad = False
                else:
                    for i, r in enumerate(r_tabs):
                        if r.collidepoint(ev.pos):
                            pestana = i
                    if pestana == 0 and r_var.collidepoint(ev.pos):
                        var = (var + 1) % 3
                    if r_cal.collidepoint(ev.pos):
                        ver_calidad = True
                    if r_volver.collidepoint(ev.pos):
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
            boton(pant, fuente_t, r_tabs[i], nombre, i == pestana)

        if pestana == 0:
            boton(pant, fuente_t, r_var, f"Variable: {VARIABLES[var]}   >")
            y = 115
            for txt in lineas_resumen(res, var):
                img = fuente.render(txt, True, (255, 255, 255))
                pant.blit(img, (50, y))
                y += 32
        else:
            img = fuente.render("(en construccion)", True, (200, 200, 200))
            pant.blit(img, (50, 120))

        boton(pant, fuente_t, r_cal, "Calidad de datos")
        boton(pant, fuente_t, r_volver, "Volver")

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