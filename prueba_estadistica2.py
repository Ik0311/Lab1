from estadistica import Frecuencias, Correlacion

# 8.3 tabla de frecuencias
fr = Frecuencias()
for _ in range(412):
    fr.agregar("slime")
for _ in range(298):
    fr.agregar("arrow_trap")
for _ in range(190):
    fr.agregar("boss")
for _ in range(100):
    fr.agregar("fall")

filas = fr.tabla()
assert fr.total == 1000
assert filas[0][0] == "slime" and filas[0][1] == 412
assert round(filas[0][2], 1) == 41.2 and round(filas[0][3], 1) == 41.2
assert round(filas[1][2], 1) == 29.8 and round(filas[1][3], 1) == 71.0
assert round(filas[2][3], 1) == 90.0
assert round(filas[3][3], 1) == 100.0
assert fr.moda() == "slime"

# 8.5 correlacion
tiempos = [2, 4, 6, 8, 10, 12]
puntajes = [800, 1400, 1900, 2600, 3000, 3700]
c = Correlacion()
for i in range(len(tiempos)):
    c.agregar(tiempos[i], puntajes[i])

assert c.n == 6
assert c.sx == 42 and c.sy == 13400
assert c.sxy == 113800
assert round(c.r(), 5) == 0.99834

print("Todo bien: frecuencias y correlacion reproducen la referencia")