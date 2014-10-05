from fabric.contrib.files import upload_template
from fabric.api import *

env.user = "root"
env.hosts = ["csgofort.com"]

def install():
    upload_template("configs/csgofort.nginx", "/etc/nginx/sites-enabled/csgofort", use_jinja=True)
    upload_template("configs/uwsgi.cmd", "/root/csgofort/app/run", use_jinja=True)
    run("chmod +x /root/csgofort/app/run")
    run()

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
    run('kill -HUP $(cat /var/run/uwsgifort.pid)')

    # TODO: restart scheduler

def deploy():
    update()
    install()
    restart()
