import asyncio
import pygame

import config
from telemetria import EscritorBitacora
from juego import jugar, ANCHO, ALTO
from stats_ui import pantalla_stats
from web import copiar_bitacora_web

TITULO = "MEGAMAN"
N_BUF = 100
DIFICULTADES = ["easy", "normal", "hard"]


def cambiar(cfg, fila, d):
    if fila == 1:
        cfg["volume"] = max(0, min(100, cfg["volume"] + 10 * d))
    elif fila == 2:
        i = 1
        if cfg["difficulty"] in DIFICULTADES:
            i = DIFICULTADES.index(cfg["difficulty"])
        i = max(0, min(2, i + d))
        cfg["difficulty"] = DIFICULTADES[i]


async def menu(pant):
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 40)
    fuente_g = pygame.font.Font(None, 72)
    opciones = ["Start Game", "Statistics", "Settings", "Quit"]
    rects = []
    for i in range(len(opciones)):
        rects.append(pygame.Rect(ANCHO // 2 - 130, 185 + i * 50, 260, 42))
    sel = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "Quit"
            if ev.type == pygame.MOUSEMOTION:
                for i, r in enumerate(rects):
                    if r.collidepoint(ev.pos):
                        sel = i
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, r in enumerate(rects):
                    if r.collidepoint(ev.pos):
                        return opciones[i]
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    sel = (sel - 1) % len(opciones)
                elif ev.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(opciones)
                elif ev.key == pygame.K_RETURN:
                    return opciones[sel]
        pant.fill((20, 20, 40))
        t = fuente_g.render(TITULO, True, (60, 140, 255))
        pant.blit(t, (ANCHO // 2 - t.get_width() // 2, 70))
        for i, op in enumerate(opciones):
            r = rects[i]
            if i == sel:
                pygame.draw.rect(pant, (45, 45, 90), r)
                pygame.draw.rect(pant, (255, 220, 80), r, 2)
                color = (255, 220, 80)
            else:
                color = (200, 200, 200)
            img = fuente.render(op, True, color)
            pant.blit(img, (r.centerx - img.get_width() // 2,
                            r.centery - img.get_height() // 2))
        pygame.display.flip()
        reloj.tick(60)
        await asyncio.sleep(0)


async def pantalla_config(pant, cfg):
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 36)
    fuente_g = pygame.font.Font(None, 56)
    filas = []
    for i in range(3):
        filas.append(pygame.Rect(200, 150 + i * 55, 400, 44))
    r_volver = pygame.Rect(ANCHO // 2 - 80, 335, 160, 42)
    sel = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                config.guardar(cfg)
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if r_volver.collidepoint(ev.pos):
                    config.guardar(cfg)
                    return
                for i, r in enumerate(filas):
                    if r.collidepoint(ev.pos):
                        sel = i
                        if i > 0:
                            if ev.pos[0] < r.centerx:
                                cambiar(cfg, i, -1)
                            else:
                                cambiar(cfg, i, 1)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    config.guardar(cfg)
                    return
                elif ev.key == pygame.K_UP:
                    sel = (sel - 1) % 3
                elif ev.key == pygame.K_DOWN:
                    sel = (sel + 1) % 3
                elif sel == 0:
                    if ev.key == pygame.K_BACKSPACE:
                        cfg["player"] = cfg["player"][:-1]
                    elif ev.unicode.isalnum() and len(cfg["player"]) < 12:
                        cfg["player"] += ev.unicode
                elif ev.key == pygame.K_LEFT:
                    cambiar(cfg, sel, -1)
                elif ev.key == pygame.K_RIGHT:
                    cambiar(cfg, sel, 1)
        pant.fill((20, 20, 40))
        t = fuente_g.render("SETTINGS", True, (255, 255, 255))
        pant.blit(t, (ANCHO // 2 - t.get_width() // 2, 60))
        textos = [f"Player: {cfg['player']}",
                  f"<   Volume: {cfg['volume']}   >",
                  f"<   Difficulty: {cfg['difficulty']}   >"]
        for i, txt in enumerate(textos):
            r = filas[i]
            if i == sel:
                pygame.draw.rect(pant, (45, 45, 90), r)
                pygame.draw.rect(pant, (255, 220, 80), r, 2)
                color = (255, 220, 80)
            else:
                color = (200, 200, 200)
            img = fuente.render(txt, True, color)
            pant.blit(img, (r.centerx - img.get_width() // 2,
                            r.centery - img.get_height() // 2))
        pygame.draw.rect(pant, (60, 140, 255), r_volver)
        img = fuente.render("Volver", True, (255, 255, 255))
        pant.blit(img, (r_volver.centerx - img.get_width() // 2,
                        r_volver.centery - img.get_height() // 2))
        pygame.display.flip()
        reloj.tick(60)
        await asyncio.sleep(0)


async def main():
    pygame.init()
    pant = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption(TITULO)
    copiar_bitacora_web()
    cfg = config.cargar()
    esc = EscritorBitacora("logs", n_buf=N_BUF)
    while True:
        op = await menu(pant)
        if op == "Start Game":
            res = await jugar(pant, cfg, esc)
            if res == "salir":
                break
        elif op == "Statistics":
            esc.vaciar()
            await pantalla_stats(pant, "logs")
        elif op == "Settings":
            await pantalla_config(pant, cfg)
        else:
            break
    esc.cerrar()
    pygame.quit()


asyncio.run(main())