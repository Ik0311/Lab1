import math


class Descriptivas:
    def __init__(self):
        self.n = 0
        self.suma = 0.0
        self.suma_cuad = 0.0
        self.minimo = None
        self.maximo = None

    def agregar(self, x):
        self.n += 1
        self.suma += x
        self.suma_cuad += x * x
        if self.minimo is None or x < self.minimo:
            self.minimo = x
        if self.maximo is None or x > self.maximo:
            self.maximo = x

    def media(self):
        return self.suma / self.n

    def varianza(self):
        if self.n < 2:
            return 0.0
        return (self.suma_cuad - self.n * self.media() ** 2) / (self.n - 1)

    def desv(self):
        return math.sqrt(self.varianza())

    def cv(self):
        return self.desv() / self.media() * 100


def mediana_de(lista):
    n = len(lista)
    mitad = n // 2
    if n % 2 == 1:
        return lista[mitad]
    return (lista[mitad - 1] + lista[mitad]) / 2


def cuartiles(datos):
    orden = sorted(datos)
    n = len(orden)
    mitad = n // 2
    inf = orden[:mitad]
    if n % 2 == 1:
        sup = orden[mitad + 1:]
    else:
        sup = orden[mitad:]
    return mediana_de(inf), mediana_de(orden), mediana_de(sup)


def percentil(datos, p):
    orden = sorted(datos)
    pos = math.ceil(p * len(orden) / 100)
    if pos < 1:
        pos = 1
    return orden[pos - 1]


def atipicos_iqr(datos):
    q1, q2, q3 = cuartiles(datos)
    iqr = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    lista = []
    for x in datos:
        if x < lim_inf or x > lim_sup:
            lista.append(x)
    return lim_inf, lim_sup, lista


def puntaje_z(x, media, desv):
    return (x - media) / desv


def atipicos_z(datos, umbral=3):
    d = Descriptivas()
    for x in datos:
        d.agregar(x)
    lista = []
    for x in datos:
        if abs(puntaje_z(x, d.media(), d.desv())) > umbral:
            lista.append(x)
    return lista