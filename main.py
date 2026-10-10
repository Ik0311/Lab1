import math
import random
import pygame

pygame.init()
ANCHO = 800
ALTO = 450
SUELO = 400
pant = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Megaman")
reloj = pygame.time.Clock()
fuente = pygame.font.Font(None, 28)
fuente_g = pygame.font.Font(None, 64)

jug = pygame.Rect(100, SUELO - 50, 36, 50)
vel = 5
vel_y = 0.0
grav = 0.8
fuerza_salto = -15
en_suelo = True

vida_max = 5
vida = vida_max
inmune = 0
dano_total = 0

balas = []
vel_bala = 12
espera = 0

enemigos = []
t_spawn = 0
puntaje = 0

estado = "jugando"
causa = ""
dur = 0.0
t_ini = pygame.time.get_ticks()

corriendo = True
while corriendo:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            corriendo = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE and en_suelo and estado == "jugando":
                vel_y = fuerza_salto
                en_suelo = False
            if ev.key == pygame.K_r and estado == "muerto":
                jug.x = 100
                jug.bottom = SUELO
                vel_y = 0.0
                balas = []
                enemigos = []
                puntaje = 0
                vida = vida_max
                inmune = 0
                dano_total = 0
                t_spawn = 0
                estado = "jugando"
                t_ini = pygame.time.get_ticks()

    if estado == "muerto":
        pant.fill((20, 20, 40))
        lineas = [("GAME OVER", fuente_g), (f"Puntaje: {puntaje}", fuente),
                  (f"Causa de muerte: {causa}", fuente),
                  (f"Tiempo: {dur:.1f} s", fuente),
                  ("Presiona R para reiniciar", fuente)]
        y = 110
        for txt, fte in lineas:
            img = fte.render(txt, True, (255, 255, 255))
            pant.blit(img, (ANCHO // 2 - img.get_width() // 2, y))
            y += 55
        pygame.display.flip()
        reloj.tick(60)
        continue

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_a]:
        jug.x -= vel
    if teclas[pygame.K_d]:
        jug.x += vel
    jug.x = max(0, min(ANCHO - jug.width, jug.x))

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

    t_spawn += 1
    if t_spawn >= 90:
        t_spawn = 0
        lado = random.choice([0, ANCHO - 30])
        if random.random() < 0.5:
            enemigos.append({"tipo": "robot", "vel": 2, "muerto": False,
                             "r": pygame.Rect(lado, SUELO - 30, 30, 30)})
        else:
            enemigos.append({"tipo": "dron", "vel": 3, "muerto": False,
                             "r": pygame.Rect(lado, random.randint(120, 300), 30, 24)})

    for e in enemigos:
        if e["r"].centerx < jug.centerx:
            e["r"].x += e["vel"]
        else:
            e["r"].x -= e["vel"]

    for b in balas:
        r_bala = pygame.Rect(b["x"] - 5, b["y"] - 5, 10, 10)
        for e in enemigos:
            if not e["muerto"] and r_bala.colliderect(e["r"]):
                e["muerto"] = True
                b["x"] = -100
                puntaje += 100
                break

    if inmune > 0:
        inmune -= 1
    for e in enemigos:
        if not e["muerto"] and inmune == 0 and jug.colliderect(e["r"]):
            e["muerto"] = True
            vida -= 1
            dano_total += 1
            inmune = 60
            if vida <= 0:
                causa = e["tipo"]
                dur = (pygame.time.get_ticks() - t_ini) / 1000
                estado = "muerto"
            break

    restantes = []
    for e in enemigos:
        if not e["muerto"]:
            restantes.append(e)
    enemigos = restantes

    pant.fill((20, 20, 40))
    pygame.draw.rect(pant, (60, 60, 80), (0, SUELO, ANCHO, ALTO - SUELO))
    if inmune == 0 or (inmune // 4) % 2 == 0:
        pygame.draw.rect(pant, (60, 140, 255), jug)
    pygame.draw.line(pant, (255, 220, 80), (cx, cy), punta, 8)
    for b in balas:
        pygame.draw.circle(pant, (255, 240, 120), (int(b["x"]), int(b["y"])), 5)
    for e in enemigos:
        if e["tipo"] == "robot":
            pygame.draw.rect(pant, (220, 60, 60), e["r"])
        else:
            pygame.draw.rect(pant, (240, 150, 50), e["r"])
    for i in range(vida_max):
        color = (80, 220, 120) if i < vida else (70, 70, 70)
        pygame.draw.rect(pant, color, (10 + i * 28, 40, 24, 12))
    texto = fuente.render(f"Puntaje: {puntaje}", True, (255, 255, 255))
    pant.blit(texto, (10, 10))
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()