from fabric.contrib.files import upload_template, exists
from fabric.api import *
import random

env.user = "root"
env.hosts = ["csgofort.com:50000"]

def config():
    upload_template("configs/csgofort.nginx", "/etc/nginx/sites-enabled/csgofort", use_jinja=True,
        backup=False)
    upload_template("configs/uwsgi.cmd", "/var/www/csgofort/app/run", use_jinja=True, backup=False)
    run("chmod +x /var/www/csgofort/app/run")

def update():
    with cd("/var/www/csgofort/app/"):
        run("git reset --hard origin/develop")
        run("git pull origin develop")
        run("chown -R www-data:www-data static/")

def migrate():
    with cd("/var/www/csgofort/app/"):
        run("python database.py migrate develop")

def builddb():
    with cd("/var/www/csgofort/app/"):
        run("python database.py build")

def restart():
    # Restart nginx
    run("kill -HUP $(cat /var/run/nginx.pid)")

    # Flush log
    if exists("/var/log/fort.log"):
        run("rm /var/log/fort.log")

    # Restart uwsgi (if its running)
    if exists("/var/run/uwsgifort.pid"):
        run('kill -HUP $(cat /var/run/uwsgifort.pid)')

    # TODO: restart scheduler

def versions():
    with cd("/var/www/csgofort/app"):
        remote_hash = run("git rev-parse HEAD").strip()

    local_hash = local("git rev-parse HEAD").strip()

    if remote_hash == local_hash:
        print "Remote and local are up-to-date!"
    else:
        print "%s vs %s" % (remote_hash, local_hash)

def logs():
    run("tail -F /var/log/fort.log")

def clear_cache():
    run("redis-cli -n 3 flushall")

def dumpdb():
    id = random.randint(10000, 99999)
    fname = "fort_dump_{}".format(id)

    with cd("/home/postgres/"):
        run('su postgres -c "pg_dump fort > {}"'.format(fname))
        run("tar -jcvf {0}.tbz2 {0}".format(fname))

        get("/home/postgres/{}.tbz2".format(fname), "{}.tbz2".format(fname))
        run("rm {0} {0}.tbz2".format(fname))

    return fname

def loaddb(name, username=None):
    local('tar -jxvf {}.tbz2'.format(name))
    local('dropdb --if-exists --port 5433 fort')
    local('createdb --port 5433 fort')

    cmd = 'psql --port 5433 -d fort < {}'.format(name)
    if username:
        local('sudo su {} -c "{}"'.format(username, cmd))
    else:
        local(cmd)

    local('rm {}'.format(name))

def syncdb():
    fname = dumpdb()
    loaddb(fname)
    local("rm -rf {}.tbz2".format(fname))

def deploy():
    update()
    restart()
    clear_cache()
