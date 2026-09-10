import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("login_logs.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    ip_address TEXT,
    country TEXT,
    timestamp TEXT,
    status TEXT
)
""")

usuarios = [f"user{i:02d}" for i in range(1, 16)]
paises_normales = ["AR", "AR", "AR", "AR", "CL", "UY"]
ips_normales = {u: f"181.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}" for u in usuarios}
base = datetime(2026, 8, 1)
registros = []

for dia in range(30):
    for _ in range(random.randint(15, 25)):
        user = random.choice(usuarios)
        hora = random.randint(8, 19)
        ts = base + timedelta(days=dia, hours=hora, minutes=random.randint(0,59))
        registros.append((user, ips_normales[user], random.choice(paises_normales), ts.isoformat(), "success"))
for _ in range(6):
    user = random.choice(usuarios)
    dia = random.randint(0, 29)
    ts = base + timedelta(days=dia, hours=random.choice([1,2,3,4]), minutes=random.randint(0,59))
    ip_rara = f"45.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    registros.append((user, ip_rara, "RU", ts.isoformat(), "success"))

for _ in range(5):
    user = random.choice(usuarios)
    dia = random.randint(0, 29)
    ts = base + timedelta(days=dia, hours=random.randint(9,18), minutes=random.randint(0,59))
    ip_rara = f"103.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    registros.append((user, ip_rara, "CN", ts.isoformat(), "success"))
victima = "user07"
ip_atacante = "185.220.101.45"
dia = 15
for m in range(40):
    ts = base + timedelta(days=dia, hours=3, minutes=m)
    registros.append((victima, ip_atacante, "NL", ts.isoformat(), "fail"))
registros.append((victima, ip_atacante, "NL", (base + timedelta(days=dia, hours=3, minutes=41)).isoformat(), "success"))

cur.executemany("INSERT INTO login_attempts (username, ip_address, country, timestamp, status) VALUES (?,?,?,?,?)", registros)
conn.commit()
conn.close()
print(f"Insertados {len(registros)} registros en login_logs.db")
