import asyncio
import pygame

from analisis import analizar
from estadistica import mediana_de, percentil

def analizar_seguro(carpeta):
    try:
        return analizar(carpeta)
    except Exception as e:
        print("Error al calcular las estadisticas:", repr(e))
        return analizar("carpeta_que_no_existe")


ANCHO = 800
ALTO = 450
PESTANAS = ["Resumen", "Distribucion", "Relacion"]
VARIABLES = ["Puntaje", "Duracion", "Dano recibido"]
PARES = [("Duracion (s)", "Puntaje"), ("Dano recibido", "Nivel alcanzado")]
X0 = 80
W = 680


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


def fmt(v):
    if abs(v) >= 1000:
        return f"{v / 1000:.1f}k"
    return f"{v:.0f}"


def px(v, minimo, rango):
    return X0 + (v - minimo) / rango * W


def interpretar(r):
    a = abs(r)
    if a < 0.2:
        return "Correlacion muy debil o nula: casi no hay relacion lineal"
    if a < 0.4:
        fuerza = "debil"
    elif a < 0.6:
        fuerza = "moderada"
    elif a < 0.8:
        fuerza = "fuerte"
    else:
        fuerza = "muy fuerte"
    if r > 0:
        return f"Correlacion {fuerza} positiva: si una sube, la otra tiende a subir"
    return f"Correlacion {fuerza} negativa: si una sube, la otra tiende a bajar"


def dibujar_distribucion(pant, fuente, fuente_p, res):
    if res["hist"] is None or "cuart" not in res:
        img = fuente.render("Se necesitan al menos 4 sesiones terminadas",
                            True, (200, 200, 200))
        pant.blit(img, (50, 120))
        return
    ints = res["hist"].intervalos()
    minimo = ints[0][0]
    maximo = ints[-1][1]
    rango = maximo - minimo
    if rango == 0:
        rango = 1

    c_max = 1
    for ini, fin, c in ints:
        if c > c_max:
            c_max = c
    y_base = 235
    alto = 135

    for ini, fin, c in ints:
        x1 = px(ini, minimo, rango)
        x2 = px(fin, minimo, rango)
        h = int(alto * c / c_max)
        r = pygame.Rect(int(x1) + 1, y_base - h, int(x2 - x1) - 2, h)
        pygame.draw.rect(pant, (60, 140, 255), r)
        t = fuente_p.render(str(c), True, (255, 255, 255))
        pant.blit(t, (r.centerx - t.get_width() // 2, y_base - h - 16))
        e = fuente_p.render(fmt(ini), True, (180, 180, 200))
        pant.blit(e, (int(x1) - e.get_width() // 2, y_base + 6))
    e = fuente_p.render(fmt(maximo), True, (180, 180, 200))
    pant.blit(e, (int(px(maximo, minimo, rango)) - e.get_width() // 2, y_base + 6))

    pygame.draw.line(pant, (200, 200, 200), (X0, y_base), (X0 + W, y_base), 2)
    pygame.draw.line(pant, (200, 200, 200), (X0, y_base - alto - 10), (X0, y_base), 2)
    t = fuente_p.render("Sesiones", True, (180, 180, 200))
    pant.blit(t, (10, y_base - alto - 10))
    t = fuente_p.render(str(c_max), True, (180, 180, 200))
    pant.blit(t, (X0 - t.get_width() - 6, y_base - alto - 4))
    t = fuente_p.render("0", True, (180, 180, 200))
    pant.blit(t, (X0 - t.get_width() - 6, y_base - 14))
    t = fuente_p.render("Puntaje", True, (180, 180, 200))
    pant.blit(t, (X0 + W // 2 - t.get_width() // 2, y_base + 22))

    q1, q2, q3 = res["cuart"]
    lim_inf, lim_sup, atip = res["iqr"]
    dentro = []
    for x in res["puntajes"]:
        if lim_inf <= x <= lim_sup:
            dentro.append(x)
    if len(dentro) > 0:
        bajo = min(dentro)
        alto_b = max(dentro)
    else:
        bajo = q1
        alto_b = q3
    yc = 305
    xb = px(bajo, minimo, rango)
    x1 = px(q1, minimo, rango)
    xm = px(q2, minimo, rango)
    x3 = px(q3, minimo, rango)
    xa = px(alto_b, minimo, rango)
    pygame.draw.line(pant, (200, 200, 200), (xb, yc), (x1, yc), 2)
    pygame.draw.line(pant, (200, 200, 200), (x3, yc), (xa, yc), 2)
    pygame.draw.line(pant, (200, 200, 200), (xb, yc - 8), (xb, yc + 8), 2)
    pygame.draw.line(pant, (200, 200, 200), (xa, yc - 8), (xa, yc + 8), 2)
    caja = pygame.Rect(int(x1), yc - 14, int(x3 - x1), 28)
    pygame.draw.rect(pant, (45, 45, 90), caja)
    pygame.draw.rect(pant, (255, 220, 80), caja, 2)
    pygame.draw.line(pant, (255, 100, 100), (xm, yc - 14), (xm, yc + 14), 3)
    for o in atip:
        pygame.draw.circle(pant, (255, 100, 220), (int(px(o, minimo, rango)), yc), 5)

    txt = (f"Q1={q1:.0f}   Mediana={q2:.0f}   Q3={q3:.0f}   "
           f"IQR={q3 - q1:.0f}   Atipicos (IQR): {len(atip)}")
    t = fuente_p.render(txt, True, (255, 255, 255))
    pant.blit(t, (X0, 340))
    t = fuente_p.render("Linea roja = mediana.  Puntos rosados = valores atipicos.",
                        True, (150, 150, 170))
    pant.blit(t, (X0, 362))


def dibujar_relacion(pant, fuente_t, fuente_p, res, par):
    if par == 0:
        pares = res["pares1"]
        corr = res["r1"]
    else:
        pares = res["pares2"]
        corr = res["r2"]
    nom_x, nom_y = PARES[par]
    if corr.n < 2 or len(pares) < 2:
        img = fuente_t.render("Se necesitan al menos 2 sesiones terminadas",
                              True, (200, 200, 200))
        pant.blit(img, (50, 130))
        return

    xmin = pares[0][0]
    xmax = pares[0][0]
    ymin = pares[0][1]
    ymax = pares[0][1]
    for x, y in pares:
        xmin = min(xmin, x)
        xmax = max(xmax, x)
        ymin = min(ymin, y)
        ymax = max(ymax, y)
    rx = xmax - xmin
    ry = ymax - ymin
    if rx == 0:
        rx = 1
    if ry == 0:
        ry = 1

    gx = 90
    gy = 120
    gw = 650
    gh = 200
    pygame.draw.line(pant, (200, 200, 200), (gx, gy + gh), (gx + gw, gy + gh), 2)
    pygame.draw.line(pant, (200, 200, 200), (gx, gy), (gx, gy + gh), 2)
    for x, y in pares:
        cx = gx + (x - xmin) / rx * gw
        cy = gy + gh - (y - ymin) / ry * gh
        pygame.draw.circle(pant, (60, 140, 255), (int(cx), int(cy)), 4)

    t = fuente_p.render(fmt(xmin), True, (180, 180, 200))
    pant.blit(t, (gx - t.get_width() // 2, gy + gh + 6))
    t = fuente_p.render(fmt(xmax), True, (180, 180, 200))
    pant.blit(t, (gx + gw - t.get_width() // 2, gy + gh + 6))
    t = fuente_p.render(nom_x, True, (180, 180, 200))
    pant.blit(t, (gx + gw // 2 - t.get_width() // 2, gy + gh + 6))
    t = fuente_p.render(fmt(ymax), True, (180, 180, 200))
    pant.blit(t, (gx - t.get_width() - 6, gy - 4))
    t = fuente_p.render(fmt(ymin), True, (180, 180, 200))
    pant.blit(t, (gx - t.get_width() - 6, gy + gh - 12))
    t = fuente_p.render(nom_y, True, (180, 180, 200))
    pant.blit(t, (10, gy - 22))

    r = corr.r()
    t = fuente_t.render(f"r = {r:.4f}      n = {corr.n} sesiones", True, (255, 220, 80))
    pant.blit(t, (gx, 350))
    t = fuente_p.render(interpretar(r), True, (255, 255, 255))
    pant.blit(t, (gx, 376))


async def pantalla_stats(pant, carpeta):
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 32)
    fuente_t = pygame.font.Font(None, 28)
    fuente_p = pygame.font.Font(None, 20)
    res = analizar_seguro(carpeta)
    pestana = 0
    var = 0
    par = 0
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
                    if r_var.collidepoint(ev.pos):
                        if pestana == 0:
                            var = (var + 1) % 3
                        elif pestana == 2:
                            par = (par + 1) % 2
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
                    if pestana == 2:
                        par = (par + 1) % 2
                    else:
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
        elif pestana == 1:
            t = fuente_t.render("Distribucion del puntaje (8 intervalos)",
                                True, (255, 220, 80))
            pant.blit(t, (30, 60))
            dibujar_distribucion(pant, fuente, fuente_p, res)
        else:
            boton(pant, fuente_t, r_var,
                  f"{PARES[par][0]} vs {PARES[par][1]}   >")
            dibujar_relacion(pant, fuente_t, fuente_p, res, par)

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