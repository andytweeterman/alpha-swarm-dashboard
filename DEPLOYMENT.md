# Alpha Swarm - Deployment Guide

## Quick Start

### Local Development
```bash
# Windows
run.bat

# macOS/Linux
bash run.sh

# Or manual setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run src/app.py
```

## Production Deployment

### Option 1: Systemd Service (Linux)

Create `/etc/systemd/system/alpha-swarm.service`:

```ini
[Unit]
Description=Alpha Swarm Financial Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/alpha-swarm
Environment="PATH=/var/www/alpha-swarm/venv/bin"
ExecStart=/var/www/alpha-swarm/venv/bin/streamlit run src/app.py --server.port 8501 --server.headless true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable alpha-swarm
sudo systemctl start alpha-swarm
```

### Option 2: Docker

Build the Docker image using the included Dockerfile:

```bash
docker build -t alpha-swarm:latest .
docker run -p 8501:8501 -v $(pwd)/data:/app/data alpha-swarm:latest
```

### Option 3: Nginx Reverse Proxy

Configure Nginx to proxy to Streamlit:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Configuration

1. **Environment Variables** (.env or .streamlit/secrets.toml):
   See `.env.example` for a template.
   ```
   STRATEGIST_SHEET_URL=https://docs.google.com/spreadsheets/...
   LOG_LEVEL=info
   ```

2. **Streamlit Config** (.streamlit/config.toml):
   - Port and host settings
   - Theme customization
   - Browser settings
   - Logger configuration

## Monitoring & Logs

- Application logs: `logs/`
- Streamlit logs: Check application output or `logs/streamlit.log`
- Monitor resource usage with system tools (htop, Task Manager, etc.)

## Troubleshooting

### Import Errors
If you get import errors, ensure:
- Virtual environment is activated
- All dependencies are installed: `pip install -r requirements.txt`
- Python path includes src/: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

### File Not Found Errors
- Ensure `launch from the repository root` (where app.py is)
- All data files are in `data/` directory
- Check file permissions, especially for logs/ and data/ directories

### Port Already in Use
Change the port in .streamlit/config.toml or via CLI:
```bash
streamlit run src/app.py --server.port 8502
```

## Backup & Data

- Regular backup of `data/` directory
- Store configuration secrets in `.streamlit/secrets.toml` (not in git)
- Archive old logs periodically
- Version control code, not data

## Performance Tuning

For high-traffic deployments:

1. Use a production server (Gunicorn, uWSGI)
2. Enable caching in .streamlit/config.toml
3. Optimize data loading and queries
4. Use a CDN for static assets
5. Monitor and profile application performance

## Support & Updates

- Consult product roadmap: `docs/ALPHA SWARM PRODUCT ROADMAP (v2.0).txt`
- User guide: `docs/USER_GUIDE.md`
- Governance documentation: `docs/Governance_Report.txt`
