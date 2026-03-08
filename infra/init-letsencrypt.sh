#!/bin/bash
# Initialize Let's Encrypt certificates for metallschrank.pfadivoels.at
set -e

DOMAIN="metallschrank.pfadivoels.at"
EMAIL="${CERTBOT_EMAIL:-}"
STAGING="${CERTBOT_STAGING:-0}"

echo "=== Let's Encrypt Certificate Setup ==="
echo "Domain: $DOMAIN"

# Step 1: Create a temporary nginx config that only serves HTTP (for ACME challenge)
echo "Step 1: Creating temporary HTTP-only nginx config..."
cat > /tmp/nginx-bootstrap.conf <<'NGINX'
events {
    worker_connections 1024;
}
http {
    server {
        listen 80;
        server_name metallschrank.pfadivoels.at;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 200 'Setting up SSL...';
            add_header Content-Type text/plain;
        }
    }
}
NGINX

# Step 2: Start nginx with temporary config
echo "Step 2: Starting nginx with HTTP-only config..."
docker compose down nginx certbot 2>/dev/null || true

docker compose run -d --name nginx-bootstrap \
    -p 80:80 \
    -v /tmp/nginx-bootstrap.conf:/etc/nginx/nginx.conf:ro \
    -v "$(docker volume inspect metallschrank_certbot_www --format '{{ .Mountpoint }}' 2>/dev/null || echo certbot_www):/var/www/certbot" \
    --no-deps \
    nginx

# Wait for nginx to be ready
sleep 2

# Step 3: Request certificate
echo "Step 3: Requesting certificate from Let's Encrypt..."
STAGING_FLAG=""
if [ "$STAGING" = "1" ]; then
    STAGING_FLAG="--staging"
    echo "(Using staging environment for testing)"
fi

EMAIL_FLAG="--register-unsafely-without-email"
if [ -n "$EMAIL" ]; then
    EMAIL_FLAG="--email $EMAIL"
fi

docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    $STAGING_FLAG \
    $EMAIL_FLAG \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

# Step 4: Stop temporary nginx and start the real stack
echo "Step 4: Stopping temporary nginx..."
docker stop nginx-bootstrap 2>/dev/null || true
docker rm nginx-bootstrap 2>/dev/null || true

echo ""
echo "=== Certificate obtained successfully! ==="
echo "Run 'docker compose up -d' to start with the real config."
