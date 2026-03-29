#!/bin/bash
# Bootstrap script executed on EC2 first boot.
# Terraform replaces ${ecr_repo_url}, ${image_tag}, and ${aws_region} before upload.
set -euo pipefail
exec > /var/log/user_data.log 2>&1

echo "===> [$(date)] Starting bootstrap"

# ─── System update & Docker ────────────────────────────────────────────────
dnf update -y
dnf install -y docker awscli
systemctl enable --now docker
usermod -aG docker ec2-user

# ─── Docker Compose v2 plugin ──────────────────────────────────────────────
mkdir -p /usr/local/lib/docker/cli-plugins
curl -fsSL \
  "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# ─── App directory ─────────────────────────────────────────────────────────
mkdir -p /opt/emotion_detector/nginx
cd /opt/emotion_detector

# ─── nginx.conf ────────────────────────────────────────────────────────────
# Single-quoted heredoc prevents shell from expanding $host, $remote_addr, etc.
cat > nginx/nginx.conf << 'NGINX_EOF'
upstream flask_app {
    server app:5000;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 10M;

    location / {
        proxy_pass         http://flask_app;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }
}
NGINX_EOF

# ─── docker-compose.yml ────────────────────────────────────────────────────
# Terraform has already substituted ${ecr_repo_url} and ${image_tag} above;
# single-quoted heredoc just prevents any residual shell expansion.
cat > docker-compose.yml << 'COMPOSE_EOF'
services:
  app:
    image: ${ecr_repo_url}:${image_tag}
    container_name: emotion_app
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - emotion_net

  nginx:
    image: nginx:1.25-alpine
    container_name: emotion_nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - app
    networks:
      - emotion_net

networks:
  emotion_net:
    driver: bridge
COMPOSE_EOF

# ─── ECR authentication ────────────────────────────────────────────────────
aws ecr get-login-password --region ${aws_region} | \
  docker login --username AWS --password-stdin ${ecr_repo_url}

# ─── Start containers ──────────────────────────────────────────────────────
docker compose pull
docker compose up -d

echo "===> [$(date)] Bootstrap complete. App reachable on port 80."
