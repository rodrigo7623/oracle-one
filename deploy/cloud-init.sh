#!/bin/bash
# Script de arranque automático para una instancia OCI Compute (Ubuntu 22.04+).
# Pegalo en el campo "Cloud-init script" al crear la instancia en la consola de OCI
# (Advanced options > Management > Initialization script), reemplazando los
# valores de GITHUB_REPO_URL y ANTHROPIC_API_KEY.
#
# Nota de seguridad: este método deja la API key visible en los metadatos de
# la instancia. Para un despliegue mas cuidado, preferi el método manual por
# SSH descrito en el README (crear el .env a mano dentro de la VM).

set -euxo pipefail

GITHUB_REPO_URL="https://github.com/TU_USUARIO/TU_REPO.git"
ANTHROPIC_API_KEY="sk-ant-REEMPLAZAR"

apt-get update -y
apt-get install -y docker.io git
systemctl enable --now docker

cd /opt
git clone "$GITHUB_REPO_URL" novashop-agent
cd novashop-agent

cat > .env <<EOF
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
EOF

docker build -t novashop-agent .
docker run -d --restart unless-stopped \
  --name novashop-agent \
  --env-file .env \
  -p 80:8000 \
  novashop-agent

# Abre el puerto 80 en el firewall del propio sistema operativo de la VM.
# El puerto también debe habilitarse en la Security List / NSG de la VCN
# desde la consola de OCI (ver README).
iptables -I INPUT -p tcp --dport 80 -j ACCEPT || true
netfilter-persistent save || true
