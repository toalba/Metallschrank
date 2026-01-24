# SSL Certificates

This directory should contain your SSL certificates for HTTPS.

## For Development (Self-Signed)

Generate a self-signed certificate:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx-selfsigned.key \
  -out nginx-selfsigned.crt \
  -subj "/C=DE/ST=State/L=City/O=Organization/CN=localhost"
```

## For Production

### Option 1: Let's Encrypt (Recommended)

Use certbot for free, automated SSL certificates:

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Generate certificate
certbot certonly --standalone -d yourdomain.com

# Copy to this directory
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx-selfsigned.crt
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx-selfsigned.key
```

### Option 2: Custom SSL Provider

If you have certificates from a commercial provider:

```bash
# Copy your certificate files
cp /path/to/your/certificate.crt nginx-selfsigned.crt
cp /path/to/your/private.key nginx-selfsigned.key
```

## File Requirements

The nginx configuration expects these exact filenames:
- `nginx-selfsigned.crt` - Certificate file
- `nginx-selfsigned.key` - Private key file

## Security Notes

⚠️ **Important**: 
- Never commit `.key` files to version control!
- Keep private keys secure and with restricted permissions:
  ```bash
  chmod 600 nginx-selfsigned.key
  ```
- Self-signed certificates will show browser warnings (only use for dev/testing)
- For production, always use certificates from a trusted CA

## Certificate Renewal

Let's Encrypt certificates expire after 90 days. Set up automatic renewal:

```bash
# Test renewal
certbot renew --dry-run

# Set up cron job for automatic renewal
echo "0 0 * * 0 certbot renew --quiet && docker compose restart nginx" | crontab -
```
