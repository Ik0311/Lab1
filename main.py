import math
import pygame

pygame.init()
ANCHO = 800
ALTO = 450
SUELO = 400
pant = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Megaman")
reloj = pygame.time.Clock()

jug = pygame.Rect(100, SUELO - 50, 36, 50)
vel = 5
vel_y = 0.0
grav = 0.8
fuerza_salto = -15
en_suelo = True

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

    pant.fill((20, 20, 40))
    pygame.draw.rect(pant, (60, 60, 80), (0, SUELO, ANCHO, ALTO - SUELO))
    pygame.draw.rect(pant, (60, 140, 255), jug)
    pygame.draw.line(pant, (255, 220, 80), (cx, cy), punta, 8)
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()