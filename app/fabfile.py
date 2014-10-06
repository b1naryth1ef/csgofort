from fabric.contrib.files import upload_template, exists
from fabric.api import *
import random

env.user = "root"
env.hosts = ["csgofort.com"]

def install():
    upload_template("configs/csgofort.nginx", "/etc/nginx/sites-enabled/csgofort", use_jinja=True)
    upload_template("configs/uwsgi.cmd", "/root/csgofort/app/run", use_jinja=True)
    run("chmod +x /root/csgofort/app/run")

def update():
    with cd("/root/csgofort/app/"):
        run("git stash")
        run("git pull origin develop")

def migrate():
    with cd("/root/csgofort/app/"):
        run("python database.py migrate develop")

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
    with cd("/root/csgofort/app"):
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

    with cd("/home/postgres/"):
        fname = "fort_dump_{}".format(id)
        run('su postgres -c "pg_dump fort > {}"'.format(fname))
        run("tar -jcvf {0}.tbz2 {0}".format(fname))

        get("/home/postgres/{}.tbz2".format(fname), "{}.tbz2".format(fname))
        run("rm {0} {0}.tbz2".format(fname))

def loaddb(name, username=None):
    local('tar -jxvf {}.tbz2'.format(name))
    local('dropdb fort')
    local('createdb fort')

    cmd = 'psql -d fort < {}'.format(name)
    if username:
        local('sudo su {} -c "{}"'.format(username, cmd))
    else:
        local(cmd)

    local('rm {}'.format(name))

def deploy():
    update()
    install()
    restart()
    clear_cache()
