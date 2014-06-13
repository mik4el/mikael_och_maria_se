from fabric.api import *
from fabric.contrib.files import exists
from fabric.operations import *
import time
from contextlib import contextmanager

env.roledefs = {
    'development': ['vagrant@127.0.0.1:2222'],
    'production': ['ubuntu@ec2-54-228-209-211.eu-west-1.compute.amazonaws.com'],
}

PROJECT_NAME = "mikael_och_maria_se"
DOMAIN_NAME = "mikaelochmaria.se"

env.root_dir = '/home/webapp'
env.virtualenv = '%s/env' % env.root_dir
env.virtualenv_python = '%s/bin/python' % env.virtualenv
env.activate = 'source %s/bin/activate ' % env.virtualenv
env.active_code_dir = '%s/%s' % (env.root_dir, PROJECT_NAME)
env.deploy_dir = '%s/deploy' % env.active_code_dir
env.conf_dir = '%s/conf' % env.active_code_dir
env.cronjobs_dir = '%s/cronjobs' % env.conf_dir
env.active_gunicorn_conf = "%s/gunicorn.conf.py-" % env.conf_dir
env.active_runit = "%s/runit-" % env.conf_dir
env.active_crontab = "%s/crontab-" % env.conf_dir
env.active_rsyslogd = "%s/rsyslog.conf-" % env.conf_dir
env.active_nginx_conf = "%s/nginx.conf-" % env.conf_dir
env.maintenance_nginx_conf = "%s/nginx.conf-maintenance" % env.conf_dir
env.source_dir = '%s/source' % env.root_dir
env.previous_release_dir = '%s/previous_release' % env.source_dir
env.media_dir = '%s/media' % env.root_dir
env.static_dir = '%s/public_static/' % env.root_dir
env.log_dir = '%s/logs' % env.root_dir

#settings based on role development
if (env.roles[0]=="development"):
    env.settings_name = "%s.settings.development"%PROJECT_NAME
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1].strip('"')
    env.active_gunicorn_conf += "development"
    env.active_runit += "development"
    env.active_nginx_conf += "development"
    env.active_crontab += "development"
    env.active_rsyslogd += "development"

#settings based on role production
if (env.roles[0]=="production"):
    env.settings_name = "%s.settings.production"%PROJECT_NAME
    env.key_filename = '~/keys/%s_production.pem'%"mikaelochmaria_se"
    env.active_gunicorn_conf += "production"
    env.active_runit += "production"
    env.active_nginx_conf += "production"
    env.active_crontab += "production"
    env.active_rsyslogd += "production"

@contextmanager
def _virtualenv():
	with prefix(env.activate):
		yield
    
def create_webapp_user():
    if not exists(env.root_dir):
        admin_username="webapp"
        admin_password="6EvDtFnNvpAm4eLg"
        
        #create user
        sudo('adduser {username} --home /home/{username} --disabled-password --gecos ""'.format(username=admin_username))
        sudo('adduser {username} admin'.format(username=admin_username))
	    # Set the password for the new admin user
        sudo('echo "{username}:{password}" | chpasswd'.format(username=admin_username,password=admin_password))

def create_logs():
    #create logging for webapp
    if exists(env.log_dir):
        sudo('rm -rf %s'%(env.log_dir))
    sudo('mkdir %s'%(env.log_dir))
    with cd(env.log_dir):
        sudo('touch cron.log')
        #sudo('touch gunicorn-access.log')
        #sudo('touch gunicorn-error.log')
        sudo('touch %s.log'%PROJECT_NAME)
        sudo('touch %s_django_request.log'%PROJECT_NAME)
        #sudo('chmod 777 cron.log gunicorn-access.log gunicorn-error.log fft_5fonder.log fft_5fonder_django_request.log')
        sudo('chmod 777 cron.log %s.log %s_django_request.log'%(PROJECT_NAME,PROJECT_NAME))
    #copy new rsyslogd
    if exists("/etc/rsyslog.conf"):
        sudo("rm -f /etc/rsyslog.conf")
    sudo("cp %s /etc/rsyslog.conf"%(env.active_rsyslogd))
    #restart rsyslog
    sudo("service rsyslog restart")
    
def create_virtualenv():
	with cd(env.root_dir):
		sudo('virtualenv env --no-site-packages')

def restart():
	"""
	Reload nginx/gunicorn
	"""
	stop_servers()
	start_servers()
	
def stop_servers():
	sudo('/etc/init.d/nginx stop')
	if exists("/etc/service/webapp"):
		#trying to stop webapp since can't stop directly after installed it in runit, do a while loop.
		did_not_stop_webapp = True
		time_spent = 0
		while did_not_stop_webapp:
			did_not_stop_webapp = False
			try:
				sudo("sv stop webapp")
			except:
				did_not_stop_webapp = True	
				time.sleep(5)
				time_spent += 5
				if time_spent > 60:
					print("An error was encountered while stopping webapp.")

def start_servers():
    if exists("/etc/service/webapp/run"):
        sudo("sv start webapp", pty=True)
    #reload nginx conf
    if exists("/etc/nginx/sites-enabled/%s"%(DOMAIN_NAME)):
        sudo("rm -f /etc/nginx/sites-enabled/%s"%(DOMAIN_NAME))
    #copy nginx conf depending on role
    sudo("cp %s /etc/nginx/sites-enabled/%s"%(env.active_nginx_conf, DOMAIN_NAME))
    sudo('/etc/init.d/nginx restart')

def transfer_project():
    #make file structure for release
    if not exists(env.source_dir):
        sudo("mkdir %s"%(env.source_dir))
    package_dir = "%s/packages"%(env.source_dir)
    if not exists(package_dir):
        sudo("mkdir %s"%(package_dir))
    release_name = time.strftime("%Y%m%d%H%M%S")
    release_dir = env.source_dir+"/"+release_name
    if exists(release_dir):
        sudo("rm -rf %s"%(release_dir))
    sudo("mkdir %s"%(release_dir))
    with cd(release_dir):
        #makes an archive from git using git-archive-all https://github.com/Kentzo/git-archive-all
        local("git-archive-all release_%s.tar.gz"%(release_name))
        put("release_%s.tar.gz"%(release_name), package_dir, use_sudo=True)
        sudo("tar zxf %s/release_%s.tar.gz"%(package_dir, release_name))
        local("rm -f release_%s.tar.gz"%(release_name))
    make_new_code_active(release_dir)

def make_new_code_active(new_active_dir):
	#take code in new_active_dir, set as active, move old active code to previous_release.
	#move active release to env.previous_release_dir
	if exists(env.active_code_dir):
		if exists(env.previous_release_dir):
			sudo("rm -rf %s"%(env.previous_release_dir))
		sudo("mkdir %s"%(env.previous_release_dir))
		sudo("mv -f %s %s"%(env.active_code_dir, env.previous_release_dir))
		#remove any *.pyc files from env.previous_release_dir
		#copy current release to /home/webapp/<projectname>
	sudo("cp -r %s %s"%(new_active_dir, env.active_code_dir))

def rollback():
	'''
	DEPRECATED! Rollback to previous release or any prompted available release. Stops and starts servers.
	'''
	if exists(env.source_dir):
		print("Previous releases available:")
		sudo("ls %s"%(env.source_dir))
		rollback_release = prompt("Rollback to release (leave blank for previous release):")
		rollback_release_dir = None
		if rollback_release == "":
			print("You selected the previous release. Rolling back.")
			rollback_release_dir = env.previous_release_dir+"/"+PROJECT_NAME
		else:
			if exists(env.source_dir+"/"+rollback_release):
				print("You selected %s. Rolling back."%(rollback_release))
				rollback_release_dir = env.source_dir+"/"+rollback_release
			else:
				print("No release %s available!"%(rollback_release))
        if exists(rollback_release_dir):
            stop_servers()
            make_new_code_active(rollback_release_dir)
            start_servers()
            print("Finished rolling back from %s"%(rollback_release_dir))
	else:
		print("No releases available since no source_dir available.")

def provision():
    '''
    Should only run once, creates user webapp, transfers project from local, installs chef, provisions server with chef, installs project.
    '''
    create_webapp_user()
    transfer_project()
    #install chef-solo
    sudo('apt-get update', pty=True)
    #ruby and rubygems is installed on vagrant, otherwise install it.
    #if env.user != 'vagrant':
        #sudo('apt-get install -y ruby1.9.1 ruby1.9.1-dev build-essential', pty=True)
        #sudo('apt-get -y install ohai chef rubygems', pty=True)
    #sudo('gem install --no-rdoc --no-ri chef', pty=True)
    #run chef-solo on env.active_code_dir
    with cd(env.deploy_dir):
        sudo('chef-solo -c /home/webapp/mikael_och_maria_se/deploy/solo.rb -j /home/webapp/mikael_och_maria_se/deploy/chef.json', pty=True)
    #build deps for PIL
    sudo("apt-get build-dep python-imaging")
    if not exists("/usr/lib/libfreetype.so"):
        sudo("ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/")
        sudo("ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/")
        sudo("ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/")
    install_project()
    
def install_project():
    """
    Init django project the first time
    """
    create_logs() 
    if exists(env.static_dir):
        sudo('rm -rf %s'%(env.static_dir))       
    sudo('mkdir %s'%(env.static_dir))
    with cd(env.static_dir):
        sudo('mkdir static')
    if not exists(env.virtualenv):
        create_virtualenv()
    with cd(env.active_code_dir):
        #copy correct gunicorn.conf.py-<role> to gunicorn.conf.py
        sudo("cp %s %s/gunicorn.conf.py"%(env.active_gunicorn_conf, env.conf_dir))
        with _virtualenv():
            #Uncomment when online:
            sudo('pip install -r requirements.txt', pty=True)
            managepy("syncdb --noinput")
        if exists("/etc/nginx/sites-enabled/default"):
            sudo("rm -f /etc/nginx/sites-enabled/default")
        managepy("collectstatic --noinput")
    configure_runit()
    add_cron_jobs()
    restart()
	
def deploy():
    stop_servers()        
    transfer_project()
    install_project()
	
def hotswitch():
    stop_servers()        
    transfer_project()
    start_servers()
    
def configure_runit():
	'''
	Configure runit to run webapp on reboot
	'''
	#create /etc/service/webapp/run from /home/webapp/PROJECT_NAME/conf/runit
	if not exists("/etc/service/webapp"):
		sudo("mkdir /etc/service/webapp")
	sudo("cp %s /etc/service/webapp/run"%(env.active_runit)) 
	sudo("chmod a+x /etc/service/webapp/run")
	
def add_cron_jobs():
    '''
    Add cronjobs in conf/cronjobs specified in crontab
    '''
    #make scripts in conf/cronjobs executable
    with cd(env.cronjobs_dir):
        output = run('ls')
        files = output.split()
        for file in files:
            sudo("chmod a+x %s"%(file))
    #add <projectname>_crontab to /etc/cron.d
    sudo("cp %s /etc/cron.d/%s"%(env.active_crontab, PROJECT_NAME))
    print("Added cronjobs")
    
def managepy(operation):
    sudo('%s manage.py %s --settings=%s'%(env.virtualenv_python, operation, env.settings_name), pty=True)