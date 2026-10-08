import os
import time


class EscritorBitacora:
    def __init__(self, carpeta="logs", n_buf=100, max_bytes=512 * 1024):
        self.carpeta = carpeta
        self.n_buf = n_buf
        self.max_bytes = max_bytes
        self.buf = []
        os.makedirs(carpeta, exist_ok=True)
        self.num = self._ultimo_num()
        self.arch = open(self._ruta(self.num), "a", encoding="utf-8")

    def _ruta(self, i):
        return os.path.join(self.carpeta, f"events_{i:03d}.log")

    def _ultimo_num(self):
        i = 1
        while os.path.exists(self._ruta(i + 1)):
            i += 1
        return i

    def registrar(self, id_ses, tipo_ev, **params):
        pares = ";".join(f"{k}={v}" for k, v in params.items())
        linea = f"{time.time():.3f}|{id_ses}|{tipo_ev}|{pares}\n"
        self.buf.append(linea)
        if len(self.buf) >= self.n_buf:
            self.vaciar()

    def vaciar(self):
        if not self.buf:
            return
        self.arch.writelines(self.buf)
        self.arch.flush()
        self.buf = []
        if os.path.getsize(self._ruta(self.num)) > self.max_bytes:
            self._rotar()

    def _rotar(self):
        self.arch.close()
        self.num += 1
        self.arch = open(self._ruta(self.num), "a", encoding="utf-8")

    def cerrar(self):
        self.vaciar()
        self.arch.close()


if __name__ == "__main__":
    esc = EscritorBitacora(n_buf=3)
    esc.registrar("S0001", "SESSION_START", player="ana", difficulty="normal")
    esc.registrar("S0001", "ENEMY_KILL", type="slime", wave=1)
    esc.registrar("S0001", "DAMAGE_TAKEN", amount=12, source="slime")
    esc.registrar("S0001", "SESSION_END", score=3200, level=4, duration=77.6, result="death")
    esc.cerrar()