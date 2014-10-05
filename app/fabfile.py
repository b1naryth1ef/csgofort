from fabric.contrib.files import upload_template, exists
from fabric.api import *

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

def deploy():
    update()
    install()
    restart()
