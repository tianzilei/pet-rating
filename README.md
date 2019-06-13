# Online survey creation tool

### Prerequisites

Flask app with MariaDB 

Check requirements.txt

### Installing

Install python packages with pip and preferably in virtual environment:
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
``` 

### Deployment

There are multiple deployment options, but one working solution is:
nginx + gunicorn (with gevent worker) 

Create systemd startup script in '/etc/systemd/system/gunicorn.service'

```
[Unit]
Description=Gunicorn instance to serve flask application
After=network.target

[Service]
User=nginx
WorkingDirectory=/srv/rating
Environment="PATH=/srv/rating/venv/bin"
ExecStart=/srv/rating/venv/bin/gunicorn run:app -b localhost:8000 -k gevent -w 1

[Install]
WantedBy=multi-user.target
```

Run 'systemctl daemon-reload' to reload units.

Enable and start gunicorn service:
```
service gunicorn enable
service gunicorn start
```

### Logs

Error logs are saved to application folder (/srv/rating/logs/) 

Optionally with journalctl:
journalctl -u gunicorn.service 

### Restart server after updates

```
service gunicorn restart
```

