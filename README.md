# Online survey creation tool

### Prerequisites

Flask app with MySql/MariaDB 

Check requirements.txt

### Deployment

There are multiple deployment options, but one working solution is:
nginx + gunicorn (with gevent worker) 

Working directory: /srv/rating

#### Installing prequisites

Install python packages with pip and preferably in virtual environment:
yy```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
``` 

Create user 'rating' and grant access to database 'rating_db'.

Create necessary tables by running the initialization script:
```
 mysql -u rating -p -D rating_db < db/create_rating_db.sql
```

#### Setting startup script

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

#### Logs

Error logs are saved to application folder (/srv/rating/logs/) 

Optionally with journalctl:
journalctl -u gunicorn.service 

#### Restart server after updates

```
service gunicorn restart
```

### Deployment with docker

Install docker and docker-compose

Go to deploy folder. Build containers and run them with:
```
docker-compose -f docker-compose.yml up -d --build
```

This will create persistent database 'rating_db' to deploy/dbdata with user 'rating'.

Application should be up and running in 'localhost'.

### Project contact details
 - osmala@utu.fi
 - timo.t.heikkila@utu.fi

