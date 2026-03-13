#!/bin/bash
# Obtener certificado SSL por primera vez.
# Ejecutar desde la raíz del proyecto después de setup-server.sh.
# Uso: bash scripts/init-ssl.sh

set -e

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "ERROR: Define DOMAIN y EMAIL antes de ejecutar."
    echo "  export DOMAIN=tuapp.duckdns.org"
    echo "  export EMAIL=tu@email.com"
    exit 1
fi

echo "==> Dominio: $DOMAIN"
echo "==> Email:   $EMAIL"

# Reemplazar la variable ${DOMAIN} en nginx.prod.conf
sed -i "s/\${DOMAIN}/$DOMAIN/g" frontend/nginx.prod.conf

# Levantar solo el frontend en HTTP para responder el challenge
echo "==> Levantando nginx en HTTP para validación ACME..."
docker compose -f docker-compose.prod.yml up -d frontend

# Esperar a que nginx esté listo
sleep 3

# Obtener el certificado
echo "==> Solicitando certificado a Let's Encrypt..."
docker compose -f docker-compose.prod.yml run --rm certbot \
    certonly --webroot -w /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

echo "==> Certificado obtenido. Levantando todos los servicios..."
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "Listo! El proyecto esta disponible en https://$DOMAIN"