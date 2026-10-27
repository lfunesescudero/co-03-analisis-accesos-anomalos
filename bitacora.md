## CO-03 - Análisis de Accesos Anómalos en Base de Datos

### Fase 1: Construcción del dataset
- Script: generate_dataset.py
- Comando de ejecución: python3 generate_dataset.py
- Resultado: 641 registros insertados en login_logs.db

- Composición del dataset:
  - Línea base: 30 días de actividad, 15 usuarios, horario 8-19hs, IP fija asignada por usuario
  - Patrón 1 - Acceso fuera de horario: 6 registros, madrugada (1-4hs), IP fuera del rango habitual del usuario, origen RU
  - Patrón 2 - Geolocalización no correspondiente: 5 registros, horario laboral normal, IP fuera del rango habitual, origen CN
  - Patrón 3 - Fuerza bruta con compromiso: 41 registros contra una única cuenta (user07), origen 185.220.101.45, 40 intentos fallidos consecutivos seguidos de acceso exitoso

- Criterio de diseño: proporción de ~98% tráfico legítimo frente a ~2% anómalo, para replicar relación señal-ruido real y evitar que las queries posteriores detecten patrones por volumen en lugar de por lógica de correlación

### Fase 2: Detección - Patrón de horario

Query inicial (sin agrupar): devolvió 47 filas, mezclando dos patrones distintos 
(fuerza bruta y acceso genuino fuera de horario) porque ambos comparten el mismo 
rango horario.

Query corregida (agrupada por usuario):
SELECT username, COUNT(*) AS accesos_fuera_horario
FROM login_attempts
WHERE CAST(strftime('%H', timestamp) AS INTEGER) < 8
   OR CAST(strftime('%H', timestamp) AS INTEGER) > 19
GROUP BY username
ORDER BY accesos_fuera_horario DESC;

Resultado:
user07 | 41  -> fuerza bruta, requiere respuesta inmediata
user15 | 2
user11 | 2
user14 | 1
user12 | 1   -> accesos aislados fuera de horario, requieren revisión

Criterio: el conteo por usuario permite distinguir severidad. Un valor alto 
concentrado en una sola cuenta indica automatización/ataque; valores bajos 
dispersos entre usuarios distintos indican casos puntuales a revisar individualmente.

### Fase 3: Detección - Patrón de geolocalización

Query inicial (sin agrupar por país): devolvió 52 filas, mezclando tres orígenes 
distintos (RU, CN, NL) bajo una sola condición de exclusión geográfica.

Query corregida:
SELECT username, country, COUNT(*) AS accesos
FROM login_attempts
WHERE country NOT IN ('AR', 'CL', 'UY')
GROUP BY username, country
ORDER BY accesos DESC;

Resultado:
user07 | NL | 41  -> ya identificado como fuerza bruta
user02 | CN | 2
user11 | RU | 2
user15 | RU | 2
user01 | CN | 1
user12 | RU | 1
user13 | CN | 1
user14 | RU | 1
user15 | CN | 1

Criterio: agrupar por usuario y país aísla el patrón de geolocalización pura 
(CN, 5 accesos en horario laboral normal) del patrón de horario (RU) y del de 
fuerza bruta (NL), que de otro modo aparecen mezclados bajo el mismo filtro.

### Fase 4: Detección - Fuerza bruta (aislamiento formal)

Query:
SELECT username, ip_address, COUNT(*) AS intentos_fallidos
FROM login_attempts
WHERE status = 'fail'
GROUP BY username, ip_address
HAVING COUNT(*) > 5
ORDER BY intentos_fallidos DESC;

Resultado:
user07 | 185.220.101.45 | 40

Criterio: WHERE filtra los fallos individuales antes de agrupar; HAVING descarta 
los grupos usuario+IP con 5 fallos o menos (rango explicable por error humano), 
dejando visible únicamente el patrón de automatización. A diferencia de las 
queries anteriores, esta aísla el caso sin mezclar los otros dos patrones.

