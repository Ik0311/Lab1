from lector import iter_events

rep = {}
n = 0
for ev in iter_events("logs_sint", rep):
    n += 1
print(rep)