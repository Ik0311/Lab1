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
        if self.media() == 0:
            return 0.0  
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


class Histograma:
    def __init__(self, minimo, maximo, k=8):
        self.minimo = minimo
        self.maximo = maximo
        self.k = k
        self.ancho = (maximo - minimo) / k
        self.cuentas = [0] * k

    def agregar(self, x):
        if self.ancho == 0:
            pos = 0
        else:
            pos = int((x - self.minimo) / self.ancho)
        if pos >= self.k:
            pos = self.k - 1
        if pos < 0:
            pos = 0
        self.cuentas[pos] += 1

    def intervalos(self):
        lista = []
        for i in range(self.k):
            ini = self.minimo + i * self.ancho
            fin = self.minimo + (i + 1) * self.ancho
            lista.append((ini, fin, self.cuentas[i]))
        return lista


class Embudo:
    def __init__(self):
        self.finales = {}
        self.total = 0

    def agregar(self, nivel_final):
        nivel = int(nivel_final)
        if nivel in self.finales:
            self.finales[nivel] += 1
        else:
            self.finales[nivel] = 1
        self.total += 1

    def tabla(self):
        if self.total == 0:
            return []
        nivel_max = max(self.finales)
        filas = []
        anterior = None
        for nivel in range(1, nivel_max + 1):
            alcanz = 0
            for n_fin, c in self.finales.items():
                if n_fin >= nivel:
                    alcanz += c
            superv = alcanz * 100 / self.total
            if anterior is None or anterior == 0:
                aband = None
            else:
                aband = (anterior - alcanz) * 100 / anterior
            filas.append((nivel, alcanz, superv, aband))
            anterior = alcanz
        return filas


class PorDificultad:
    def __init__(self):
        self.grupos = {"easy": Descriptivas(), "hard": Descriptivas()}

    def agregar(self, dificultad, puntaje):
        if dificultad in self.grupos:
            self.grupos[dificultad].agregar(puntaje)

    def diferencia(self):
        return self.grupos["easy"].media() - self.grupos["hard"].media()