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