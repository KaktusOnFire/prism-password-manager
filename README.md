<img src="src/logo.png" width="500">

# PRISM Password Manager
[![Build](https://github.com/KaktusOnFire/prism-password-manager/actions/workflows/main.yaml/badge.svg?branch=master)](https://github.com/KaktusOnFire/prism-password-manager/actions/workflows/main.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PRISM is a [Django](https://www.djangoproject.com/)-based secured password manager.

Every secret is encrypted using [Fernet](https://cryptography.io/en/latest/fernet/) symmetric encryption

- [Requirements](#requirements)
- [Features](#features)
- [Website](#website)
- [Usage](#usage)
- [Deployment](#deployment)
   - [Environment Variables](#environment-variables)
   - [Static files](#staticfiles)
   - [Start containers](#start-containers)
   - [Setup superuser](#setup-superuser)
- [Security note](#security-note)
- [Bugs](#bugs)
- [Design](#design)

## Requirements
* Docker (with docker-compose)
* (optional) SSL-ready NGINX server

## Features

- Fernet-based symmetric encryption of each secret
- Encrypted cookies (for master key caching)
- SSL-ready
- Cross-platform
- Fast deployment

## Website

PRISM is now available at **https://prism.kaktusdev.ru/**

## Usage

* Register at `/auth/register`
* Generate your encryption key on `/auth/key` page. **Don't forget to save it.**
* Start saving you secrets

## Deployment

### Environment Variables
At first, you should create `.env` file with your ENV variables in project root directory.

This is an example `.env` file structure.
You can treat all values as **default** values.
```bash
DJANGO_SECRET_KEY='secret_key'
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 0.0.0.0
DJANGO_SSL_ENABLED=False
DJANGO_REGISTRATION_ENABLED=True

POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=prism_database
POSTGRES_USER=prism_user
POSTGRES_PASSWORD=prism_password
```

`DJANGO_SECRET_KEY` - Django secret key for hashing internal passwords. You can generate it on https://djecrety.ir/.

`DJANGO_ALLOWED_HOSTS` - List of available hosts for which the application will be available. Set your domain name separated by a space **only if you have it**.

`DJANGO_SSL_ENABLED` -  Set `True` **only** if you have an **SSL-ready** NGINX (or another) proxy server.

`DJANGO_REGISTRATION_ENABLED` -  Allows users to create their own accounts. Set `False` to manage user accounts by your own.

`POSTGRES_HOST` - Database host address.

`POSTGRES_PORT` - Database port.

`POSTGRES_DB` - Database name.

`POSTGRES_USER` - Database username.

`POSTGRES_PASSWORD` - Database password.

### Staticfiles
**If you a Windows user, you can skip this step.**

Main Django container have a non-root user for security reasons.  
Before starting our service, its important to create a user that have an access to folder with our static and media files.

Nothing complicated, just run the following code in project root directory:
```bash 
groupadd --gid 2000 prism 
useradd prism --uid 2000 --gid prism
mkdir cdn
chown -R prism:prism cdn
```

### Start containers

If you have a properly configured proxy server like NGINX, you can just run
```bash 
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

Otherwise, you can start application with included NGINX-server
```bash 
docker-compose -f docker-compose.nginx.yml build
docker-compose -f docker-compose.nginx.yml up -d
```

### Setup superuser

Create a django superuser to manage user accounts.
```bash 
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Security note

Built-in NGINX server is not configured for use SSL connection.  
If you want to use this application in production, it is recommended to configure your own proxy server with SSL support.

This is an example NGINX setup manual:
* Install NGINX
* Copy `gzip.conf`, `ssl_setup.conf`, `security_headers.conf` from `docker/nginx/conf` to `/etc/nginx/conf.d/`
* Create free SSL certificate [using this guide](https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/).
* Setup your `yourdomain` file in `/etc/nginx/sites-available/` like this [example](https://gist.github.com/KaktusOnFire/c5dc512f24612eee143e44a4bedef3df). Replace `your_domain` with your domain name and `<your_project_dir>` with your project directory.
* Create symlink with `ln -s /etc/nginx/sites-available/yourdomain /etc/nginx/sites-enabled/yourdomain`
* Restart NGINX

## Bugs

If you discover any bugs or vulnerabilities, please report them in [Github Issues](https://github.com/KaktusOnFire/prism-password-manager/issues) or my [Telegram](https://t.me/KaktusOnFire).

## Design

Design by [AppSeed](https://appseed.us/)