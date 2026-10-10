import asyncio
import math
import random
import time
import pygame

ANCHO = 800
ALTO = 450
SUELO = 400
DANO = {"robot": 20, "dron": 15, "disparo_dron": 10}
AJUSTE = {"easy": (130, 0.7), "normal": (100, 1.0), "hard": (70, 1.4)}


def nueva_id():
    return "S" + str(int(time.time()))


def total_nivel(n, mult):
    return max(2, int((3 + 2 * n) * mult))


def intervalo_nivel(n):
    return max(30, 100 - 8 * n)


async def jugar(pant, cfg, esc):
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 28)
    fuente_g = pygame.font.Font(None, 64)
    dificultad = cfg["difficulty"] if cfg["difficulty"] in AJUSTE else "normal"
    jugador = cfg["player"] or "jugador"
    vida_max, mult = AJUSTE[dificultad]

    jug = pygame.Rect(100, SUELO - 50, 36, 50)
    vel = 5
    vel_y = 0.0
    grav = 0.8
    fuerza_salto = -15
    en_suelo = True

    DASH_VEL = 16
    DASH_DUR = 10
    DASH_ESPERA = 60
    dash_t = 0
    dash_cd = 0
    dash_dir = 1

    vida = vida_max
    inmune = 0
    dano_total = 0

    balas = []
    vel_bala = 12
    espera = 0

    enemigos = []
    disp_en = []
    t_spawn = 0
    puntaje = 0

    nivel = 1
    por_salir = total_nivel(1, mult)
    t_aviso = 120

    estado = "jugando"
    causa = ""
    dur = 0.0
    t_ini = pygame.time.get_ticks()

    id_ses = nueva_id()
    esc.registrar(id_ses, "SESSION_START", player=jugador, difficulty=dificultad)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if estado == "jugando":
                    seg = (pygame.time.get_ticks() - t_ini) / 1000
                    esc.registrar(id_ses, "SESSION_END", score=puntaje,
                                  level=nivel, duration=round(seg, 1),
                                  result="quit")
                return "salir"
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if estado == "jugando":
                        seg = (pygame.time.get_ticks() - t_ini) / 1000
                        esc.registrar(id_ses, "SESSION_END", score=puntaje,
                                      level=nivel, duration=round(seg, 1),
                                      result="quit")
                    return "menu"
                if ev.key == pygame.K_m and estado == "muerto":
                    return "menu"
                if ev.key == pygame.K_SPACE and en_suelo and estado == "jugando":
                    vel_y = fuerza_salto
                    en_suelo = False
                if (ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT)
                        and estado == "jugando" and dash_cd == 0):
                    tec = pygame.key.get_pressed()
                    if tec[pygame.K_a]:
                        dash_dir = -1
                    elif tec[pygame.K_d]:
                        dash_dir = 1
                    elif pygame.mouse.get_pos()[0] < jug.centerx:
                        dash_dir = -1
                    else:
                        dash_dir = 1
                    dash_t = DASH_DUR
                    dash_cd = DASH_ESPERA
                    vel_y = 0.0
                if ev.key == pygame.K_r and estado == "muerto":
                    jug.x = 100
                    jug.bottom = SUELO
                    vel_y = 0.0
                    balas = []
                    enemigos = []
                    disp_en = []
                    puntaje = 0
                    vida = vida_max
                    inmune = 0
                    dano_total = 0
                    dash_t = 0
                    dash_cd = 0
                    t_spawn = 0
                    nivel = 1
                    por_salir = total_nivel(1, mult)
                    t_aviso = 120
                    estado = "jugando"
                    t_ini = pygame.time.get_ticks()
                    id_ses = nueva_id()
                    esc.registrar(id_ses, "SESSION_START", player=jugador,
                                  difficulty=dificultad)

        if estado == "muerto":
            pant.fill((20, 20, 40))
            lineas = [("GAME OVER", fuente_g), (f"Puntaje: {puntaje}", fuente),
                      (f"Nivel alcanzado: {nivel}", fuente),
                      (f"Causa de muerte: {causa}", fuente),
                      (f"Tiempo: {dur:.1f} s", fuente),
                      ("R: reiniciar     M: menu", fuente)]
            y = 90
            for txt, fte in lineas:
                img = fte.render(txt, True, (255, 255, 255))
                pant.blit(img, (ANCHO // 2 - img.get_width() // 2, y))
                y += 50
            pygame.display.flip()
            reloj.tick(60)
            await asyncio.sleep(0)
            continue

        teclas = pygame.key.get_pressed()
        if dash_cd > 0:
            dash_cd -= 1
        if dash_t > 0:
            jug.x += dash_dir * DASH_VEL
            dash_t -= 1
        else:
            if teclas[pygame.K_a]:
                jug.x -= vel
            if teclas[pygame.K_d]:
                jug.x += vel
        jug.x = max(0, min(ANCHO - jug.width, jug.x))

        if dash_t == 0:
            vel_y += grav
            jug.y += round(vel_y)
        if jug.bottom >= SUELO:
            jug.bottom = SUELO
            vel_y = 0
            en_suelo = True

        mx, my = pygame.mouse.get_pos()
        cx = jug.centerx
        cy = jug.centery - 5
        ang = math.atan2(my - cy, mx - cx)
        punta = (cx + math.cos(ang) * 35, cy + math.sin(ang) * 35)

        if espera > 0:
            espera -= 1
        if pygame.mouse.get_pressed()[0] and espera == 0:
            balas.append({"x": punta[0], "y": punta[1],
                          "vx": math.cos(ang) * vel_bala,
                          "vy": math.sin(ang) * vel_bala})
            espera = 10

        vivas = []
        for b in balas:
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            if 0 <= b["x"] <= ANCHO and 0 <= b["y"] <= ALTO:
                vivas.append(b)
        balas = vivas

        if t_aviso > 0:
            t_aviso -= 1
        else:
            t_spawn += 1
            if por_salir > 0 and t_spawn >= intervalo_nivel(nivel):
                t_spawn = 0
                por_salir -= 1
                lado = random.choice([0, ANCHO - 30])
                prob_dron = min(0.7, 0.3 + 0.05 * nivel)
                if random.random() < prob_dron:
                    enemigos.append({"tipo": "dron", "vel": 3 + nivel // 4,
                                     "muerto": False, "cd": random.randint(30, 60),
                                     "r": pygame.Rect(lado, random.randint(120, 300), 30, 24)})
                else:
                    enemigos.append({"tipo": "robot", "vel": 2 + nivel // 3,
                                     "muerto": False,
                                     "r": pygame.Rect(lado, SUELO - 30, 30, 30)})

        for e in enemigos:
            dx = jug.centerx - e["r"].centerx
            if abs(dx) > e["vel"]:
                if dx > 0:
                    e["r"].x += e["vel"]
                else:
                    e["r"].x -= e["vel"]
            if e["tipo"] == "dron":
                if e["cd"] > 0:
                    e["cd"] -= 1
                if e["cd"] == 0 and abs(dx) < 40:
                    disp_en.append({"r": pygame.Rect(e["r"].centerx - 4, e["r"].bottom, 8, 14),
                                    "hit": False})
                    e["cd"] = 90

        vivos = []
        for s in disp_en:
            s["r"].y += 6
            if not s["hit"] and s["r"].y < SUELO:
                vivos.append(s)
        disp_en = vivos

        for b in balas:
            r_bala = pygame.Rect(b["x"] - 5, b["y"] - 5, 10, 10)
            for e in enemigos:
                if not e["muerto"] and r_bala.colliderect(e["r"]):
                    e["muerto"] = True
                    b["x"] = -100
                    puntaje += 100
                    esc.registrar(id_ses, "ENEMY_KILL", type=e["tipo"], wave=nivel)
                    break

        if inmune > 0:
            inmune -= 1
        golpe = ""
        if inmune == 0 and dash_t == 0:
            for e in enemigos:
                if not e["muerto"] and jug.colliderect(e["r"]):
                    e["muerto"] = True
                    golpe = e["tipo"]
                    break
            if golpe == "":
                for s in disp_en:
                    if not s["hit"] and jug.colliderect(s["r"]):
                        s["hit"] = True
                        golpe = "disparo_dron"
                        break
        if golpe != "":
            dano = DANO[golpe]
            vida -= dano
            dano_total += dano
            inmune = 60
            esc.registrar(id_ses, "DAMAGE_TAKEN", amount=dano, source=golpe)
            if vida <= 0:
                causa = golpe
                dur = (pygame.time.get_ticks() - t_ini) / 1000
                estado = "muerto"
                esc.registrar(id_ses, "PLAYER_DEATH", cause=causa, level=nivel)
                esc.registrar(id_ses, "SESSION_END", score=puntaje, level=nivel,
                              duration=round(dur, 1), result="death")

        restantes = []
        for e in enemigos:
            if not e["muerto"]:
                restantes.append(e)
        enemigos = restantes

        if (estado == "jugando" and por_salir == 0 and len(enemigos) == 0
                and t_aviso == 0):
            nivel += 1
            puntaje += 200
            por_salir = total_nivel(nivel, mult)
            t_spawn = 0
            t_aviso = 120
            seg = (pygame.time.get_ticks() - t_ini) / 1000
            esc.registrar(id_ses, "LEVEL_UP", level=nivel, time=round(seg, 1))

        pant.fill((20, 20, 40))
        pygame.draw.rect(pant, (60, 60, 80), (0, SUELO, ANCHO, ALTO - SUELO))
        if dash_t > 0:
            pygame.draw.rect(pant, (140, 230, 255), jug)
        elif inmune == 0 or (inmune // 4) % 2 == 0:
            pygame.draw.rect(pant, (60, 140, 255), jug)
        pygame.draw.line(pant, (255, 220, 80), (cx, cy), punta, 8)
        for b in balas:
            pygame.draw.circle(pant, (255, 240, 120), (int(b["x"]), int(b["y"])), 5)
        for e in enemigos:
            if e["tipo"] == "robot":
                pygame.draw.rect(pant, (220, 60, 60), e["r"])
            else:
                pygame.draw.rect(pant, (240, 150, 50), e["r"])
        for s in disp_en:
            pygame.draw.rect(pant, (255, 100, 220), s["r"])
        pygame.draw.rect(pant, (70, 70, 70), (10, 40, 140, 12))
        ancho_vida = int(140 * max(0, vida) / vida_max)
        pygame.draw.rect(pant, (80, 220, 120), (10, 40, ancho_vida, 12))
        pygame.draw.rect(pant, (70, 70, 70), (10, 58, 140, 8))
        carga = int(140 * (1 - dash_cd / DASH_ESPERA))
        pygame.draw.rect(pant, (100, 200, 255), (10, 58, carga, 8))
        texto = fuente.render(f"Nivel: {nivel}   Puntaje: {puntaje}", True, (255, 255, 255))
        pant.blit(texto, (10, 10))
        if t_aviso > 0:
            img = fuente_g.render(f"NIVEL {nivel}", True, (255, 255, 255))
            pant.blit(img, (ANCHO // 2 - img.get_width() // 2, 150))
        pygame.display.flip()
        reloj.tick(60)
        await asyncio.sleep(0)