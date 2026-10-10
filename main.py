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

jug = pygame.Rect(100, SUELO - 50, 36, 50)
vel = 5
vel_y = 0.0
grav = 0.8
fuerza_salto = -15
en_suelo = True

balas = []
vel_bala = 12
espera = 0

enemigos = []
t_spawn = 0
puntaje = 0

corriendo = True
while corriendo:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            corriendo = False
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE and en_suelo:
            vel_y = fuerza_salto
            en_suelo = False

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

    # aparecen enemigos cada 90 vueltas (1.5 segundos)
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

    # los enemigos caminan hacia el jugador
    for e in enemigos:
        if e["r"].centerx < jug.centerx:
            e["r"].x += e["vel"]
        else:
            e["r"].x -= e["vel"]

    # choque de balas con enemigos
    for b in balas:
        r_bala = pygame.Rect(b["x"] - 5, b["y"] - 5, 10, 10)
        for e in enemigos:
            if not e["muerto"] and r_bala.colliderect(e["r"]):
                e["muerto"] = True
                b["x"] = -100
                puntaje += 100
                break

    restantes = []
    for e in enemigos:
        if not e["muerto"]:
            restantes.append(e)
    enemigos = restantes

    pant.fill((20, 20, 40))
    pygame.draw.rect(pant, (60, 60, 80), (0, SUELO, ANCHO, ALTO - SUELO))
    pygame.draw.rect(pant, (60, 140, 255), jug)
    pygame.draw.line(pant, (255, 220, 80), (cx, cy), punta, 8)
    for b in balas:
        pygame.draw.circle(pant, (255, 240, 120), (int(b["x"]), int(b["y"])), 5)
    for e in enemigos:
        if e["tipo"] == "robot":
            pygame.draw.rect(pant, (220, 60, 60), e["r"])
        else:
            pygame.draw.rect(pant, (240, 150, 50), e["r"])
    texto = fuente.render(f"Puntaje: {puntaje}", True, (255, 255, 255))
    pant.blit(texto, (10, 10))
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()