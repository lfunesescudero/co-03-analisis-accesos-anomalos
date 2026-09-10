# CO-03: Análisis de Accesos Anómalos en Base de Datos

**Stack:** SQLite, SQL, Python

## Hipótesis y Decisión

Se identificó la necesidad de auditar el histórico de accesos al sistema para 
determinar si existían patrones de comportamiento fuera de la línea base 
operativa establecida. La hipótesis de trabajo fue que un análisis correlacional 
sobre horario, geolocalización y frecuencia de intentos permitiría distinguir 
actividad legítima de actividad comprometida sin depender de una única señal 
aislada.

Se decidió estructurar el análisis en tres ejes independientes: horario de 
acceso, consistencia geográfica y tasa de intentos fallidos. Un ataque real rara 
vez se manifiesta en una sola dimensión, y correlacionar múltiples señales reduce 
la tasa de falsos positivos frente a reglas de detección simples.

## Evidencia Cruda & Interpretación

### Eje 1: Horario de acceso

```sql
SELECT username, COUNT(*) AS accesos_fuera_horario
FROM login_attempts
WHERE CAST(strftime('%H', timestamp) AS INTEGER) < 8
   OR CAST(strftime('%H', timestamp) AS INTEGER) > 19
GROUP BY username
ORDER BY accesos_fuera_horario DESC;
```

Resultado:

| username | accesos_fuera_horario |
|---|---|
| user07 | 41 |
| user15 | 2 |
| user11 | 2 |
| user14 | 1 |
| user12 | 1 |

Una primera versión de la consulta sin agrupamiento devolvió 47 registros 
individuales, mezclando dos patrones de naturaleza distinta bajo la misma 
condición horaria. El agrupamiento por usuario permitió separar severidad: la 
concentración de 41 accesos en `user07` corresponde a actividad automatizada, 
mientras que los valores de 1 a 2 en el resto corresponden a accesos aislados 
que requieren revisión puntual, no respuesta inmediata.

### Eje 2: Consistencia geográfica

```sql
SELECT username, country, COUNT(*) AS accesos
FROM login_attempts
WHERE country NOT IN ('AR', 'CL', 'UY')
GROUP BY username, country
ORDER BY accesos DESC;
```

Resultado:

| username | country | accesos |
|---|---|---|
| user07 | NL | 41 |
| user02 | CN | 2 |
| user11 | RU | 2 |
| user15 | RU | 2 |
| user01 | CN | 1 |
| user12 | RU | 1 |
| user13 | CN | 1 |
| user14 | RU | 1 |
| user15 | CN | 1 |

El agrupamiento por usuario y país aisló un tercer patrón, independiente del 
horario: cinco accesos desde origen CN ocurridos dentro del rango horario 
operativo normal (9-18hs). Este eje confirma que la anomalía de geolocalización 
no depende del horario para manifestarse, y valida la necesidad de mantener los 
tres ejes de análisis como criterios separados.

### Eje 3: Tasa de intentos fallidos

```sql
SELECT username, ip_address, COUNT(*) AS intentos_fallidos
FROM login_attempts
WHERE status = 'fail'
GROUP BY username, ip_address
HAVING COUNT(*) > 5
ORDER BY intentos_fallidos DESC;
```

Resultado:

| username | ip_address | intentos_fallidos |
|---|---|---|
| user07 | 185.220.101.45 | 40 |

Esta consulta aisló de forma directa el incidente de mayor severidad: 40 
intentos fallidos consecutivos contra la cuenta `user07`, originados desde 
185.220.101.45, dirección perteneciente a un rango de salida Tor documentado 
públicame
