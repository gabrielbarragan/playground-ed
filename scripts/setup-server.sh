#!/bin/bash
# Ejecutar en el servidor Hetzner (Ubuntu 24.04) como root
# Uso: bash setup-server.sh

set -e

echo "==> Actualizando sistema..."
apt update && apt upgrade -y

echo "==> Instalando Docker..."
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

echo "==> Instalando Docker Compose plugin..."
apt install -y docker-compose-plugin

echo "==> Instalando utilidades..."
apt install -y git ufw

echo "==> Configurando firewall..."
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "==> Servidor listo. Ahora:"
echo "    1. Clona el repositorio"
echo "    2. Crea el archivo .env con JWT_SECRET y DOMAIN"
echo "    3. Ejecuta scripts/init-ssl.sh"