module.exports = {
  apps: [{
    name: 'whatsapp-bot',
    script: 'gunicorn',
    args: '-w 4 -b 0.0.0.0:5000 app:app --timeout 120',
    interpreter: 'none',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: 5000
    },
    error_file: './logs/whatsapp-bot-error.log',
    out_file: './logs/whatsapp-bot-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    min_uptime: '10s',
    max_restarts: 10,
    restart_delay: 4000
  }]
};
