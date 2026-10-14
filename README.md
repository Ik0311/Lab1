Videojuego en Pygame con bitácora de eventos y estadísticas hechas desde cero. Laboratorio 1 de Estructura de Datos I, Universidad del Norte. Autor: Iván Eduardo Rivas Guzmán.

Instalar: pip install pygame-ce

Jugar: python main.py (A y D mover, espacio saltar, mouse apuntar, clic disparar, Shift dash, Esc menú)

Pruebas: python prueba_estadistica.py, python prueba_estadistica2.py y python prueba_estadistica3.py

Analizar una bitácora: python analisis.py datos_web (la bitácora real de 25 sesiones está en datos_web)

Versión web: python -m pygbag . y abrir http://localhost:8000

telemetria.py es el módulo telemetry del enunciado y estadistica.py es el statistics_engine.

Ejecutar versión web
python -m pybag .

para hacer pruebas
cd ..
git clone https://github.com/Ik0311/Lab1.git Lab1_prueba
cd Lab1_prueba
python main.py
python prueba_estadistica.py
python prueba_estadistica2.py
python prueba_estadistica3.py

para ver eventos en vivo en la terminal
Get-Content logs\events_001.log -Wait -Tail 5
Get-Content config.json


Problemas conocidos 
-en la web: abrir Statistics justo después de abandonar una partida con Esc puede congelar la página.
