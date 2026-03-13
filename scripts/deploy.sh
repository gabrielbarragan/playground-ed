#!/bin/bash
# Actualizar el proyecto en producción (después del primer despliegue).
# Uso: bash scripts/deploy.sh

set -e

echo "==> Descargando últimos cambios..."
git pull

echo "==> Reconstruyendo y reiniciando servicios..."
docker compose -f docker-compose.prod.yml up -d --build

echo "==> Limpiando imágenes antiguas..."
docker image prune -f

echo "==> Deploy completado."
docker compose -f docker-compose.prod.yml ps