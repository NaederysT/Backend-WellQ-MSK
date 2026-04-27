# Backend-WellQ-MSK

IA para gestion de pacientes MSK.

## MongoDB

El modelo del PDF se replica en MongoDB con validadores e indices en
`app/db/mongo_schema.py`. La conexion se configura desde `.env`:

```env
MONGODB_URI=...
MONGODB_DB_NAME=dev_wq
MONGODB_APPLY_SCHEMA_ON_STARTUP=false
```

Para crear/actualizar colecciones, validadores e indices en Atlas:

```bash
python -m app.scripts.setup_mongodb
```

Para poblar datos demo y probar consultas reales:

```bash
python -m app.scripts.seed_demo_data
```

Si quieres que el backend aplique el esquema cada vez que arranca, cambia
`MONGODB_APPLY_SCHEMA_ON_STARTUP=true`.
