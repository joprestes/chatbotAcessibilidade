# 🚀 Guia de Deploy e Produção

**Data de Criação:** 2025-11-22  
**Versão do Projeto:** 3.1.0

---

## 📋 Índice

1. [Configuração HTTPS](#configuração-https)
2. [CDN para Assets Estáticos](#cdn-para-assets-estáticos)
3. [Configuração de Servidor Web](#configuração-de-servidor-web)
4. [Variáveis de Ambiente](#variáveis-de-ambiente)
5. [Monitoramento e Logs](#monitoramento-e-logs)

---

## 🔒 Configuração HTTPS

### Por que HTTPS é Importante?

- **Segurança:** Protege dados em trânsito
- **SEO:** Google prioriza sites HTTPS
- **Conformidade:** Necessário para muitos recursos modernos (Service Workers, etc.)
- **Headers de Segurança:** HSTS e outros headers requerem HTTPS

### Opções de Configuração

#### 1. Usando Nginx como Reverse Proxy

**Instalação do Nginx:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# macOS (Homebrew)
brew install nginx
```

**Configuração do Nginx (`/etc/nginx/sites-available/chatbot-acessibilidade`):**
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    # Redireciona HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com;

    # Certificados SSL (obtidos via Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    # Configurações SSL recomendadas
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Headers de segurança (adicionais aos do middleware)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Tamanho máximo de upload
    client_max_body_size 10M;

    # Proxy para aplicação FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (se necessário no futuro)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Cache para assets estáticos (se não usar CDN)
    location /static/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_cache_valid 200 1d;
        add_header Cache-Control "public, max-age=86400";
    }

    location /assets/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_cache_valid 200 7d;
        add_header Cache-Control "public, max-age=604800";
    }
}
```

**Habilitar configuração:**
```bash
sudo ln -s /etc/nginx/sites-available/chatbot-acessibilidade /etc/nginx/sites-enabled/
sudo nginx -t  # Verificar configuração
sudo systemctl reload nginx
```

#### 2. Usando Caddy (Automático)

**Instalação:**
```bash
# Ubuntu/Debian
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# macOS (Homebrew)
brew install caddy
```

**Configuração (`Caddyfile`):**
```
seu-dominio.com {
    reverse_proxy localhost:8000
    
    # Headers de segurança
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
    }
}
```

**Iniciar Caddy:**
```bash
sudo caddy start
```

#### 3. Usando Certbot (Let's Encrypt)

**Instalação:**
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# macOS (Homebrew)
brew install certbot
```

**Obter certificado:**
```bash
# Com Nginx
sudo certbot --nginx -d seu-dominio.com

# Standalone (sem Nginx)
sudo certbot certonly --standalone -d seu-dominio.com
```

**Renovação automática:**
```bash
# Certbot cria cron job automaticamente
# Verificar com:
sudo certbot renew --dry-run
```

---

## 🌐 CDN para Assets Estáticos

### Por que usar CDN?

- **Performance:** Reduz latência ao servir assets de servidores próximos ao usuário
- **Escalabilidade:** Reduz carga no servidor principal
- **Custo:** Muitos CDNs oferecem planos gratuitos generosos
- **Cache:** Cache distribuído globalmente

### Opções de CDN

#### 1. Cloudflare (Recomendado - Gratuito)

**Configuração:**

1. **Criar conta no Cloudflare:**
   - Acesse [cloudflare.com](https://www.cloudflare.com)
   - Adicione seu domínio
   - Siga as instruções para atualizar nameservers

2. **Configurar Cache Rules:**
   - No painel do Cloudflare, vá em **Caching** → **Configuration**
   - Configure cache para `/static/` e `/assets/`:
     - **Cache Level:** Standard
     - **Browser Cache TTL:** 1 day (para `/static/`) ou 7 days (para `/assets/`)
     - **Edge Cache TTL:** 1 month

3. **Otimizações Automáticas:**
   - **Auto Minify:** Ative para CSS, JavaScript e HTML
   - **Brotli Compression:** Ative para compressão adicional
   - **Rocket Loader:** Opcional (pode quebrar alguns scripts)

**Configuração no código:**
O código já está preparado para CDN. Os headers `Cache-Control` são configurados automaticamente pelo middleware.

#### 2. AWS CloudFront

**Configuração:**

1. **Criar Distribution:**
   ```bash
   # Via AWS CLI
   aws cloudfront create-distribution \
     --origin-domain-name seu-dominio.com \
     --default-root-object index.html
   ```

2. **Configurar Cache Behaviors:**
   - **Path Pattern:** `/static/*`
   - **Cache Policy:** CachingOptimized
   - **TTL:** 86400 segundos (1 dia)

3. **Configurar Headers:**
   - Adicione `Cache-Control` nos headers de resposta
   - CloudFront respeitará os headers do servidor

#### 3. Vercel / Netlify (Para Frontend)

**Se hospedar frontend separadamente:**

1. **Vercel:**
   ```bash
   npm i -g vercel
   vercel --prod
   ```

2. **Netlify:**
   ```bash
   npm i -g netlify-cli
   netlify deploy --prod
   ```

**Configuração de Cache:**
Crie arquivo `netlify.toml` ou `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=86400"
        }
      ]
    }
  ]
}
```

---

## 🖥️ Configuração de Servidor Web

### Executando com Uvicorn

**Produção com múltiplos workers:**
```bash
uvicorn src.backend.api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --access-log
```

**Com SSL/TLS direto (não recomendado, use reverse proxy):**
```bash
uvicorn src.backend.api:app \
  --host 0.0.0.0 \
  --port 8443 \
  --ssl-keyfile /path/to/key.pem \
  --ssl-certfile /path/to/cert.pem \
  --workers 4
```

### Usando Gunicorn + Uvicorn Workers

**Instalação:**
```bash
pip install gunicorn
```

**Execução:**
```bash
gunicorn src.backend.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Systemd Service (Linux)

**Criar arquivo `/etc/systemd/system/chatbot-acessibilidade.service`:**
```ini
[Unit]
Description=Chatbot de Acessibilidade Digital API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/chatbotAcessibilidade
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn src.backend.api:app \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Habilitar e iniciar:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable chatbot-acessibilidade
sudo systemctl start chatbot-acessibilidade
```

---

## 🔐 Variáveis de Ambiente

### Arquivo `.env` de Produção

```env
# API Keys (OBRIGATÓRIAS)
GOOGLE_API_KEY=sua_chave_google_api
OPENROUTER_API_KEY=sua_chave_openrouter_api

# Configurações de Fallback
FALLBACK_ENABLED=true
OPENROUTER_MODELS=meta-llama/llama-3.3-70b-instruct:free,google/gemini-flash-1.5:free

# CORS
CORS_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10

# Cache
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600
CACHE_MAX_SIZE=1000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Segurança
SECURITY_HEADERS_ENABLED=true
CSP_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'

# Compressão
COMPRESSION_ENABLED=true

# Timeouts
API_TIMEOUT_SECONDS=30
```

### Segurança

**⚠️ IMPORTANTE:**
- **NUNCA** commite o arquivo `.env` no Git
- Use variáveis de ambiente do sistema ou secrets manager
- Rotacione chaves API regularmente
- Use diferentes chaves para desenvolvimento e produção

**Exemplo com secrets manager (AWS Secrets Manager):**
```python
import boto3
import json

def load_secrets():
    client = boto3.client('secretsmanager')
    secret = client.get_secret_value(SecretId='chatbot-acessibilidade/prod')
    return json.loads(secret['SecretString'])
```

---

## 📊 Monitoramento e Logs

### Logs Estruturados

O projeto já inclui logging estruturado. Configure rotação de logs:

**Logrotate (`/etc/logrotate.d/chatbot-acessibilidade`):**
```
/path/to/chatbotAcessibilidade/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload chatbot-acessibilidade > /dev/null 2>&1 || true
    endscript
}
```

### Monitoramento com Prometheus (Opcional)

**Adicionar métricas:**
```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Health Checks

O endpoint `/api/health` já está disponível. Configure monitoramento:

**Exemplo com Uptime Robot:**
- URL: `https://seu-dominio.com/api/health`
- Intervalo: 5 minutos
- Alerta: Se status != 200

---

## 🚀 Checklist de Deploy

### Antes do Deploy

- [ ] Todas as variáveis de ambiente configuradas
- [ ] Certificados SSL obtidos e configurados
- [ ] CDN configurado (se aplicável)
- [ ] Testes passando localmente
- [ ] Linters passando
- [ ] Documentação atualizada

### Durante o Deploy

- [ ] Servidor web configurado (Nginx/Caddy)
- [ ] Aplicação rodando com múltiplos workers
- [ ] Service/systemd configurado (se aplicável)
- [ ] Logs sendo gerados corretamente
- [ ] Health check respondendo

### Após o Deploy

- [ ] Testar endpoints principais
- [ ] Verificar headers de segurança
- [ ] Testar compressão de respostas
- [ ] Verificar cache de assets
- [ ] Monitorar logs por erros
- [ ] Configurar alertas

---

## 📚 Recursos Adicionais

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [Cloudflare CDN](https://www.cloudflare.com/cdn/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Última atualização:** 2025-11-22  
**Versão do Documento:** 1.0.0

