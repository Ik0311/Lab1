import asyncio
import pygame

import config
from telemetria import EscritorBitacora
from juego import jugar, ANCHO, ALTO

N_BUF = 10


async def menu(pant):
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 40)
    fuente_g = pygame.font.Font(None, 72)
    opciones = ["Start Game", "Statistics", "Settings", "Quit"]
    sel = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "Quit"
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    sel = (sel - 1) % len(opciones)
                elif ev.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(opciones)
                elif ev.key == pygame.K_RETURN:
                    return opciones[sel]
        pant.fill((20, 20, 40))
        t = fuente_g.render("MEGAMAN", True, (60, 140, 255))
        pant.blit(t, (ANCHO // 2 - t.get_width() // 2, 70))
        for i, op in enumerate(opciones):
            color = (255, 220, 80) if i == sel else (200, 200, 200)
            img = fuente.render(op, True, color)
            pant.blit(img, (ANCHO // 2 - img.get_width() // 2, 190 + i * 50))
        pygame.display.flip()
        reloj.tick(60)
        await asyncio.sleep(0)


async def pantalla_config(pant, cfg):
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 36)
    fuente_g = pygame.font.Font(None, 56)
    dificultades = ["easy", "normal", "hard"]
    sel = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                config.guardar(cfg)
                return
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
                elif sel == 1:
                    if ev.key == pygame.K_LEFT:
                        cfg["volume"] = max(0, cfg["volume"] - 10)
                    elif ev.key == pygame.K_RIGHT:
                        cfg["volume"] = min(100, cfg["volume"] + 10)
                elif sel == 2:
                    i = 1
                    if cfg["difficulty"] in dificultades:
                        i = dificultades.index(cfg["difficulty"])
                    if ev.key == pygame.K_LEFT:
                        i = max(0, i - 1)
                    elif ev.key == pygame.K_RIGHT:
                        i = min(2, i + 1)
                    cfg["difficulty"] = dificultades[i]
        pant.fill((20, 20, 40))
        t = fuente_g.render("SETTINGS", True, (255, 255, 255))
        pant.blit(t, (ANCHO // 2 - t.get_width() // 2, 60))
        filas = [f"Player: {cfg['player']}", f"Volume: {cfg['volume']}",
                 f"Difficulty: {cfg['difficulty']}"]
        for i, txt in enumerate(filas):
            color = (255, 220, 80) if i == sel else (200, 200, 200)
            img = fuente.render(txt, True, color)
            pant.blit(img, (250, 160 + i * 50))
        ayuda = pygame.font.Font(None, 24).render(
            "Arriba/abajo: elegir   Izq/der: cambiar   Esc: guardar y volver",
            True, (150, 150, 170))
        pant.blit(ayuda, (ANCHO // 2 - ayuda.get_width() // 2, 380))
        pygame.display.flip()
        reloj.tick(60)
        await asyncio.sleep(0)


async def pantalla_stats(pant):
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 40)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return
        pant.fill((20, 20, 40))
        img = fuente.render("Statistics (proximamente)   Esc: volver", True, (255, 255, 255))
        pant.blit(img, (ANCHO // 2 - img.get_width() // 2, 200))
        pygame.display.flip()
        reloj.tick(60)
        await asyncio.sleep(0)


async def main():
    pygame.init()
    pant = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Megaman")
    cfg = config.cargar()
    esc = EscritorBitacora("logs", n_buf=N_BUF)
    while True:
        op = await menu(pant)
        if op == "Start Game":
            res = await jugar(pant, cfg, esc)
            if res == "salir":
                break
        elif op == "Statistics":
            await pantalla_stats(pant)
        elif op == "Settings":
            await pantalla_config(pant, cfg)
        else:
            break
    esc.cerrar()
    pygame.quit()


asyncio.run(main())