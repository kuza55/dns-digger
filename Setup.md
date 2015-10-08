# Setup #

Digger is written in Python and requires a number of libraries. Below we detail the recommended installation process which uses `pip` and `virtualenv` to create an isolated environment.

If you'd prefer to install the dependencies system-wide, manually, please see `doc/requirements` to see the list of libraries.

## Virtualenv ##

Install dependencies and Python libraries:

```
virtualenv --no-site-packages venv
source venv/bin/activate

pip install -r doc/requirements
pip install -r web/dashboard/requirements
```

## WDNS ##

Digger uses the [wdns](https://github.com/farsightsec/wdns) C library and [pywdns](https://github.com/farsightsec/pywdns) Cython wrapper for parsing DNS messages.

Digger was written and tested using version 0.4, which is included in the `lib` directory.

```
cd lib
tar xvzf pywdns-0.4.tar.gz
pip install -e pywdns-0.4
cd -
```

## RabbitMQ ##

RabbitMQ is the backbone of Digger, please the documentation for installation procedures for your system:

http://www.rabbitmq.com/download.html

```
# delete_user {username}
$ rabbitmqctl delete_user guest

# add_user {username} {password}
$ rabbitmqctl add_user digger $PASSWORD
```

## PostgreSQL ##

Digger core uses a database to store domain names and their respective source. Any database backend supported by SQLAlchemy will work, but we provide the PostgreSQL schema.

```
sudo -u postgres psql <<SQL
  CREATE USER digger WITH PASSWORD 'password';
  CREATE DATABASE digger WITH owner digger;
SQL
psql < doc/pg-schema.sql
```

## Supervisor ##

We recommend using [supervisord](http://supervisord.org/) to logically daemonize and control the separate Scheduler, Dispatcher, and Archiver processes.

```
cp doc/supervisor.conf.example conf/supervisor.conf
supervisord -c conf/supervisor.conf -d .
supervisorctl -c conf/supervisor.conf
```