# Análisis de Accesos Anómalos en Base de Datos

Correlación de patrones de acceso mediante SQL para identificar actividad fuera 
de la línea base operativa: horario, geolocalización y tasa de intentos fallidos.

## Hallazgo principal

Se confirmó compromiso de cuenta mediante fuerza bruta: 40 intentos fallidos 
consecutivos desde una dirección perteneciente a un rango de salida Tor 
documentado, seguidos de acceso exitoso.

## Contenido

- `generate_dataset.py` — construcción del dataset base (SQLite)
- `documento_caso.md` — análisis completo: hipótesis, evidencia, criterio de 
tuning y mapeo NIST CSF
- `bitacora.md` — registro de ejecución
- `login_logs.db` — base de datos con los registros analizados

## Stack

SQLite, SQL, Python
