from estadistica import (Descriptivas, cuartiles, percentil,
                         atipicos_iqr, atipicos_z, puntaje_z)

datos = [1200, 1500, 1500, 1800, 2100, 2400, 2400, 3000, 3600, 9000]
d = Descriptivas()
for x in datos:
    d.agregar(x)

# 8.1 descriptivas
assert d.n == 10
assert d.suma == 28500
assert round(d.media(), 2) == 2850.00
assert d.minimo == 1200 and d.maximo == 9000
assert d.maximo - d.minimo == 7800
assert round(d.varianza(), 2) == 5205000.00
assert round(d.desv(), 2) == 2281.45
assert round(d.cv(), 2) == 80.05

# 8.2 mediana, cuartiles y atipicos
q1, q2, q3 = cuartiles(datos)
assert q2 == 2250
assert q1 == 1500
assert q3 == 3000
assert q3 - q1 == 1500
assert percentil(datos, 90) == 3600
lim_inf, lim_sup, atip = atipicos_iqr(datos)
assert lim_inf == -750
assert lim_sup == 5250
assert atip == [9000]
assert round(puntaje_z(9000, d.media(), d.desv()), 2) == 2.70
assert atipicos_z(datos) == []

print("Todo bien: reproduce los valores de referencia")