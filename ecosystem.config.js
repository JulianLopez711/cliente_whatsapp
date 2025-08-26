module.exports = {
  apps: [{
    name: 'whatsapp-bot',
    script: 'gunicorn',
    args: 'app:app --config gunicorn.conf.py',
    cwd: '/home/devxcargo/cliente_whatsapp',
    instances: 1,              // Gunicorn ya maneja workers internamente
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      PYTHONPATH: '/home/devxcargo/cliente_whatsapp',
      PORT: 5000
    },
    env_production: {
      NODE_ENV: 'production',
      PYTHONPATH: '/home/devxcargo/cliente_whatsapp'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    
    // Configuración específica para aplicaciones Python
    interpreter: 'python3',
    
    // Reinicio condicional
    min_uptime: '10s',
    max_restarts: 10
  }]
};
