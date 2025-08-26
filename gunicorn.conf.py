# Configuración de Gunicorn para WhatsApp Bot
import multiprocessing

# Servidor
bind = "0.0.0.0:5000"
backlog = 2048

# Workers
workers = min(4, (multiprocessing.cpu_count() * 2) + 1)
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2

# Reinicio
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "-"
errorlog = "-" 
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Proceso
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (si lo necesitas)
# certfile = None
# keyfile = None
