#!/bin/bash

# ======================
# FRONTEND (React + TS)
# ======================
mkdir -p aurora-dev/src/{components,pages,hooks,services}
touch aurora-dev/package.json

# ====================
# BACKEND (FastAPI)
# ====================
mkdir -p aurora-db/app/{models,schemas,routes,services}
touch aurora-db/app/{main.py,db.py}
touch aurora-db/requirements.txt

# ====================
# Archivos raíz
# ====================
touch docker-compose.yml
touch README.md

# ====================
# Mensaje final
# ====================
echo "✅ Estructura de proyecto creada dentro de $(pwd)"#!/bin/bash

# Crear directorio raíz
mkdir -p aurora
cd aurora || exit

# ======================
# FRONTEND (React + TS)
# ======================
mkdir -p frontend/src/{components,pages,hooks,services}
touch frontend/package.json

# ====================
# BACKEND (FastAPI)
# ====================
mkdir -p backend/app/{models,schemas,routes,services}
touch backend/app/{main.py,db.py}
touch backend/requirements.txt

# ====================
# Archivos raíz
# ====================
touch docker-compose.yml
touch README.md

# ====================
# Mensaje final
# ====================
echo "✅ Estructura de proyecto 'aurora' creada con éxito"
