import random
from telemetria import EscritorBitacora

CAUSAS = ["slime", "arrow_trap", "boss", "fall"]
PESOS = [41, 30, 19, 10]
DIFICULTADES = ["easy", "normal", "hard"]
PROB_PASAR = {"easy": 0.85, "normal": 0.75, "hard": 0.6}


def una_sesion(esc, id_ses):
    dif = random.choice(DIFICULTADES)
    esc.registrar(id_ses, "SESSION_START", player="ana", difficulty=dif)
    nivel = 1
    dur = 0.0
    kills = 0
    while True:
        dur += random.uniform(20, 40)
        for _ in range(random.randint(3, 8)):
            esc.registrar(id_ses, "ENEMY_KILL", type="slime", wave=nivel)
            kills += 1
        for _ in range(random.randint(0, 3)):
            esc.registrar(id_ses, "DAMAGE_TAKEN",
                          amount=random.randint(5, 25),
                          source=random.choice(CAUSAS))
        if nivel < 8 and random.random() < PROB_PASAR[dif]:
            nivel += 1
            esc.registrar(id_ses, "LEVEL_UP", level=nivel, time=round(dur, 1))
        else:
            break
    causa = random.choices(CAUSAS, weights=PESOS)[0]
    esc.registrar(id_ses, "PLAYER_DEATH", cause=causa, level=nivel)
    puntaje = kills * 100 + nivel * 300 + random.randint(0, 200)
    if random.random() < 0.02:
        puntaje = puntaje * 5
    if random.random() >= 0.03:
        esc.registrar(id_ses, "SESSION_END", score=puntaje, level=nivel,
                      duration=round(dur, 1), result="death")


def generar(carpeta, n_sesiones, n_buf=100):
    esc = EscritorBitacora(carpeta, n_buf=n_buf)
    for i in range(1, n_sesiones + 1):
        una_sesion(esc, f"S{i:04d}")
    esc.cerrar()


if __name__ == "__main__":
    random.seed(42)
    generar("logs_sint", 40)
    print("Listo: revisa la carpeta logs_sint")