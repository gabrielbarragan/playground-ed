#!/bin/bash
# Obtener certificado SSL por primera vez.
# Ejecutar desde la raíz del proyecto después de setup-server.sh.
# Uso:
#   export DOMAIN=tuapp.duckdns.org
#   export EMAIL=tu@email.com
#   bash scripts/init-ssl.sh

set -e

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "ERROR: Define DOMAIN y EMAIL antes de ejecutar."
    echo "  export DOMAIN=tuapp.duckdns.org"
    echo "  export EMAIL=tu@email.com"
    exit 1
fi

echo "==> Dominio: $DOMAIN"
echo "==> Email:   $EMAIL"

# Reemplazar ${DOMAIN} en nginx.prod.conf
sed -i "s/\${DOMAIN}/$DOMAIN/g" frontend/nginx.prod.conf

# Paso 1: levantar nginx mínimo (sin SSL, sin backend) para responder el challenge
echo "==> Levantando nginx bootstrap en HTTP..."
docker compose -f docker-compose.bootstrap.yml up -d nginx-bootstrap
sleep 3

# Paso 2: obtener el certificado
echo "==> Solicitando certificado a Let's Encrypt..."
docker compose -f docker-compose.bootstrap.yml run --rm certbot \
    certonly --webroot -w /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

# Paso 3: bajar el nginx bootstrap
echo "==> Bajando nginx bootstrap..."
docker compose -f docker-compose.bootstrap.yml down

# Paso 4: levantar todo con SSL
echo "==> Levantando todos los servicios con HTTPS..."
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "Listo! El proyecto esta disponible en https://$DOMAIN"