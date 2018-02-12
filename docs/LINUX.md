# Linux setup

Instructions below were tested on:

* Fedora 27

1. [Install postgress locally](#1-install-postgres)
2. [Configure postgress](#2-configure-postgres)
3. [Run elasticsearch](#3-run-elasticsearch)
4. [Start the service](#4-start-the-service)
5. [Create service host aliases](#5-create-service-host-aliases)
6. [Access the service](#6-access-services-by-their-service-names)


## 1. Install postgres
```shell
sudo dnf install \
    postgresql-9.6.5-1.fc27.x86_64 \
    postgresql-server-9.6.5-1.fc27.x86_64 \
    postgresql-devel-9.6.5-1.fc27.x86_64
```


## 2. Configure postgres
Edit `/var/lib/pgsql/data/postgresql.conf` and uncomment following settings:
```shell
listen_addresses = 'localhost'
port = 5432
```

Edit `/var/lib/pgsql/data/pg_hba.conf` and set the authentication methods to `trust`
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
# "local" is for Unix domain socket connections only
local   all             all                                trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
```

Then start the `postgres`:
```shell
sudo systemctl start postgresql
```


## 3. Run elasticsearch

Due to an elasticsearch [bug](https://github.com/elastic/elasticsearch/issues/23486) in handling `cgroups` version 5.1.2 won't work on Fedora.
You will need to use version `5.3.1`.

To do this change the image versions in `docker-compose.yml` & `docker-compose-test.yml`
```shell
    image: docker.elastic.co/elasticsearch/elasticsearch:5.3.1
```

Last thing to do before starting the service is to change the max virtual memory:
```shell
sudo sysctl -w vm.max_map_count=262144
```

Then start the `elasticsearch` with port `9200` exposed:
```shell
docker-compose run --rm -d -p 9200:9200 elasticsearch
```


## 4. Start the service

Start the webserver
```shell
make debug
make debug_webserver
```

Create new superuser:
```shell
cmd=createsuperuserwithpsswd make debug_manage
```


## 5. Create service host aliases

Create host aliases in [/etc/hosts](../#sso)


## 6. Access services by their service names

If everything is correctly configured, then you should be able to access:

* buyer api via [http://buyer.trade.great:8000/](http://buyer.trade.great:8000/)
* buyer admin via [http://buyer.trade.great:8000/admin/](http://buyer.trade.great:8000/admin/)
