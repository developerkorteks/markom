module.exports = {
  apps: [
    {
      name: 'markom-merchandise',
      script: '/root/markom/venv/bin/python',
      args: 'manage.py runserver 0.0.0.0:50456 --noreload',
      cwd: '/root/markom',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        DJANGO_SETTINGS_MODULE: 'mysite.settings',
        PYTHONUNBUFFERED: '1',
      },
      error_file: '/root/markom/logs/pm2-error.log',
      out_file: '/root/markom/logs/pm2-out.log',
      log_file: '/root/markom/logs/pm2-combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    }
  ]
};
