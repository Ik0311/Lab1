from estadistica import Descriptivas

datos = [1200, 1500, 1500, 1800, 2100, 2400, 2400, 3000, 3600, 9000]
d = Descriptivas()
for x in datos:
    d.agregar(x)

assert d.n == 10
assert d.suma == 28500
assert round(d.media(), 2) == 2850.00
assert d.minimo == 1200 and d.maximo == 9000
assert d.maximo - d.minimo == 7800
assert round(d.varianza(), 2) == 5205000.00
assert round(d.desv(), 2) == 2281.45
assert round(d.cv(), 2) == 80.05

print("Todo bien: reproduce los valores de referencia")