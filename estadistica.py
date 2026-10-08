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


def por_frecuencia(par):
    return par[1]


class Frecuencias:
    def __init__(self):
        self.cuentas = {}
        self.total = 0

    def agregar(self, valor):
        if valor in self.cuentas:
            self.cuentas[valor] += 1
        else:
            self.cuentas[valor] = 1
        self.total += 1

    def tabla(self):
        filas = []
        acum = 0
        orden = sorted(self.cuentas.items(), key=por_frecuencia, reverse=True)
        for valor, f in orden:
            acum += f
            filas.append((valor, f, f * 100 / self.total, acum * 100 / self.total))
        return filas

    def moda(self):
        return self.tabla()[0][0]


class Correlacion:
    def __init__(self):
        self.n = 0
        self.sx = 0.0
        self.sy = 0.0
        self.sxy = 0.0
        self.sxx = 0.0
        self.syy = 0.0

    def agregar(self, x, y):
        self.n += 1
        self.sx += x
        self.sy += y
        self.sxy += x * y
        self.sxx += x * x
        self.syy += y * y

    def r(self):
        num = self.n * self.sxy - self.sx * self.sy
        den = math.sqrt((self.n * self.sxx - self.sx ** 2) *
                        (self.n * self.syy - self.sy ** 2))
        if den == 0:
            return 0.0
        return num / den