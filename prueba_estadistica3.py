from estadistica import Histograma, Embudo, PorDificultad

datos = [1200, 1500, 1500, 1800, 2100, 2400, 2400, 3000, 3600, 9000]

# 8.3 histograma con k = 8
h = Histograma(1200, 9000, 8)
for x in datos:
    h.agregar(x)
assert h.ancho == 975
assert h.cuentas == [5, 3, 1, 0, 0, 0, 0, 1]

# 8.4 embudo con el ejemplo del enunciado
e = Embudo()
for nivel, cuantas in [(1, 30), (2, 80), (3, 210), (4, 20), (5, 160)]:
    for _ in range(cuantas):
        e.agregar(nivel)
filas = e.tabla()
assert filas[0][1] == 500
assert filas[1][1] == 470 and round(filas[1][2], 1) == 94.0
assert round(filas[1][3], 1) == 6.0
assert filas[2][1] == 390 and round(filas[2][3], 1) == 17.0
assert filas[3][1] == 180 and round(filas[3][3], 1) == 53.8
assert filas[4][1] == 160 and round(filas[4][3], 1) == 11.1

# 8.6 por dificultad
pd = PorDificultad()
pd.agregar("easy", 3000)
pd.agregar("easy", 4000)
pd.agregar("hard", 1000)
pd.agregar("hard", 2000)
assert pd.grupos["easy"].n == 2
assert pd.grupos["easy"].media() == 3500
assert pd.grupos["hard"].media() == 1500
assert pd.diferencia() == 2000

print("Todo bien: histograma, embudo y dificultad")