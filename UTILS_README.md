
## Sources
[Marius Page ](https://blog.mariusschulz.com/2014/12/16/how-to-set-up-sublime-text-for-a-vastly-better-markdown-writing-experience) 
[OOPSMONK Page ](http://oopsmonk.github.io/blog/2015/08/12/markdown-preview-use-sublime-text-3) 


# ARCHIVE

TAR a folder

tar zcvf <name>.tar.gz <folder_to_archive>


UNTAR the archive

tar zxvf <archive>

---


```python
	print ( 'x=1')
```

[link to archive]


*italic*
**Bold**
~~strikethrough~~

Image
![GitHub Logo](/images/Logo.png)


Link
[GitHub](https://github.com)

Link with tootip
[Upstage](https://github.com/upstage/ "Visit Upstage!")

>Quotes
>suite Quotes


Code Block

```python
print( ' something ')
def func(x):
	try:
		print ( x)
	except Exception as e:
		print ( 'Exception in ' % ( __name__))

```


//--- Escapes string special chars

```js
String.prototype.escape=function(){
    return this.replace(/[-[\]{}()*+?.,\\^$|#\s]/g,"\\$&");
}
```


# MYSQL
## Install MySQL
https://devops.profitbricks.com/tutorials/install-mysql-on-centos-7/

execute script
mysql> source myscript.sql;

mysql> create database appdb;
mysql> grant all on appdb.* to 'appuser'@'localhost' identified by 'password';
mysql> quit

## ANOTHER

```
wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
sudo rpm -ivh mysql-community-release-el7-5.noarch.rpm
sudo yum update

sudo yum install mysql-server
sudo systemctl start mysqld
```

---

# POSTGRESQL WITH YUM

```
yum install postgresql94-server
```


*Then, either:*

```
sudo service postgresql initdb
```

*or*

```
postgresql-setup initdb
```

*Then, do either this*

```
sudo chkconfig postgresql on  
```

*or* 

```
systemctl enable postgresql
```

## ON REDHAT

```
systemctl enable postgresql-9.4.service
systemctl start postgresql-9.4.service
```


## Database location

### UBUNTU

```
/var/lib/postgresql/<version>/data
```

### REDHAT or CENTOS

```
/var/lib/pgsql/data
```

[Source](https://wiki.postgresql.org/wiki/PostgreSQL_on_RedHat_Linux)

```
sudo service postgresql restart
```

```
/var/lib/pgsql-9.6
service postgresql-9.6 initdb
chkconfig postgresql-9.6 on
```
---

# CELERY and REDIS

rabbitmqctl stop
rabbitmqctl status

[download rabbitmq](http://www.rabbitmq.com/download.html)


[celery install](https://www.digitalocean.com/community/tutorials/how-to-use-celery-with-rabbitmq-to-queue-tasks-on-an-ubuntu-vps)


[about celery](http://flask.pocoo.org/docs/0.10/patterns/celery/)

*create an app like this:**

```
celery -A application.celery worker
```

```
sudo /sbin/service redis start
```

[Reference doc](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis "how to install redis")

---


# MONGODB on CENTOS 7

Edit /etc/yum.repos.d/mongodb.repo
[mongodb]
name=MongoDB Repository
baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/i686/
gpgcheck=0
enabled=1

Yum –y update

Yum install –y mongodb-org mongodb-org-server
systemctl start mongod

---

# NETWORKING ON VB FOR CENTOS 7

EDIT /etc/sysconfig/network-scripts/ifcfg-enp0s3

```
onboot=yes
```

Then:

```
sudo systemctl restart NetworkManager
```




# STORED


Install MySQL:
https://devops.profitbricks.com/tutorials/install-mysql-on-centos-7/

execute script
mysql> source cabamte.sql;

mysql> create database appdb;
mysql> grant all on appdb.* to 'appuser'@'localhost' identified by 'password';
mysql> quit

---

# CLEAN UP
Clean up:
find /var/cache -type f -size +2048 -mount -exec rm -r {} \;
yum clean all


---

# CENTOS with VB
CENTOS 7 (Feb 9)
Virtual BOX:
Centos 7.0 networking:
http://lintut.com/how-to-setup-network-after-rhelcentos-7-minimal-installation/

Important commands for networking:
nmcli d
nmtui


sudo yum install docker
sudo service docker start

Example 1:
sudo docker pull centos
sudo docker images centos
Run to test it:
sudo docker run -i -t centos /bin/bash

EXECUTE a MYSQL BATCH:
mysql -u taxi -p  < create_proc_driverlog.sql


# AUTHENTICATION
Authentication link:
http://rc3.org/2011/12/02/using-hmac-to-authenticate-web-service-requests/


# PLANTUML

*Usage*

```
plantuml.py [-h] [-o OUT] [-s SERVER] filename [filename ...]
```


Such as:

```
python /c/Apps/python-plantuml/plantuml.py Payment\ Complete_SF.txt -o PaymenT.png
```


---


# NETWORKING 
Internet access

```
vim /etc/resolv.conf
```

and add:

```
nameserver 8.8.8.8
nameserver 8.8.4.4
```

Add the following to /etc/sysconfig/network-scripts/ifcfg-enp0s3

```
DNS1=8.8.8.8
DNS2=8.8.4.4
```

Note this was set to no

```
ONBOOT=yes  
```


---

# CELERY


[Check this link](http://michal.karzynski.pl/blog/2014/05/18/setting-up-an-asynchronous-task-queue-for-django-using-celery-redis/)




---

# NGINX
[LINK](https://www.nginx.com/resources/wiki/start/topics/examples/fullexample2/)

```
sudo chmod 755 /etc/init.d/nginx
```

```
sudo /etc/init.d/nginx start
```


---




# ARCUS INSTALL
ARCUS INSTALL
tar -xvf mkc_5.6.1_cabmate_centos_6_5_64bit.tar
vim mkc.ini
edit
timezone=US/Eastern
mode = cwebs
[cabmate-service]
host
port
agent
secret
validation_secret




ARCHIVE_NAME=mkc_5.6.1_cabmate sh centos.sh >& 5.6.1_cabmate_install.log

tar -xvf api.mkc_5.6.1_centos_6_5_64bit.tar
vim customer_cabmate.ini
[cabmate-db]
[CabmateRepo-db]
[cabmaterates-db]
[drivershift-db]
[shareride-db]




ARCHIVE_NAME=api.mkc_5.6.1 sh deploy.sh >& mkc.api.5.6.1_install.log

cd /home/vtrack/
tail -f 5.6.1_cabmate_install.log
tail -f mkc.api.5.6.1_install.log

---

# ARCUS FROM SOURCES
ARCUS UI from source Files:
production_cabmate.ini
production.ini
Check settings.ini

ARCUS API from source files:
Check:
/etc/httpd/conf.d/api.mkc.conf 
/etc/httpd/conf.d/mkc.conf

cp -r  /var/lib/mkc/src/content/static/ /home/samira/arcus.ui/src/content/static/

For some reason, also:
sudo chmod -R 777  /home/samira/arcus.api/logs/




cp –r /var/lib/mkc/env    /home/samira/arcus.ui/env
cp –r /var/lib/api.mkc/env    /home/samira/arcus.api/env


chmod –R 777 /home/samira/arcus.api
chmod –R 777 /home/samira/arcus.ui


---

# CONNEXION

Reference

[Source as an example](https://github.com/hjacobs/connexion-example "Example Open API implementation")
First Update you dev environment
If using Python 3 such as python 3.4

sudo yum install -y python34-devel


pip install uwsgi


# GITHUB PAGES
[Check out this link](http://davidensinger.com/2013/03/setting-the-dns-for-github-pages-on-namecheap/ "Setting your DNS on Github pages")
Set up the DNS
You’ll need to set up three different records:

Click the Add New Record button and then select A Record from the list. You’ll then want to enter @ for Host and 192.30.252.153 for IP Address. Leave the TTL as Automatic (use this setting for all three records).
Add another new A Record with the same @ for the Host, but use 192.30.252.154 for the IP Address.
Finally, add another new record, but select CNAME Record. For Host set www and for the IP Address use your username.github.io. (with trailing period).

[Julia Lovett link] (https://medium.com/@LovettLovett/github-pages-godaddy-f0318c2f25a#.hsgsff6iw)
[Stackoerverflow link] (http://stackoverflow.com/questions/9082499/custom-domain-for-github-project-pages)


## MAIL
[MAIL](http://naelshiab.com/tutorial-send-email-python/)
 https://docs.python.org/2/library/smtplib.html 
– http://www.tutorialspoint.com/python/python_sending_email.htm
– http://en.wikibooks.org/wiki/Python_Programming/Email
– http://www.pythonforbeginners.com/code-snippets-source-code/using-python-to-send-email
– https://docs.python.org/2/library/email.mime.html
– https://docs.python.org/2/library/email-examples.html
– https://docs.python.org/2/library/email.html
– http://www.blog.pythonlibrary.org/2013/06/26/python-102-how-to-send-an-email-using-smtplib-email/
– http://www.smipple.net/snippet/Jimmyromanticde/gmail.py

