AfterGlow-Cloud
===============

About
-----

AfterGlow Cloud is a security visualization tool which lets users upload data 
and visualize the data as graphs on-the-fly. This project is a part of 
[Google's Summer of Code](http://www.google-melange.com/gsoc/homepage/google/gsoc2012) 
2012 under [The Honeynet Project](https://honeynet.org/gsoc/slot6). 

The core of this tool is derived from its command-line predecessor [AfterGlow](http://afterglow.sourceforge.net/). 
AfterGlow Cloud runs primarily on Django. A live demo can be found [here](http://andromeda.ayrus.net:8080).

Installation
------------

Following provides installation requirements and procedure for AfterGlow Cloud.
At a production level, since AfterGlow runs on Django; it can be deployed in a
number of ways. This document however will only deal with deploying the
application on Apache with <code>mod_wsgi</code>. If you choose to deploy it with another
choice, please refer the to guidelines in the [official Django documentation](https://docs.djangoproject.com/en/dev/howto/deployment/).

AfterGlow also requires a database system on its backend to handle its 
operations. Instructions below refer to using MySQL. You can again, however use
any of the [compatible systems](https://docs.djangoproject.com/en/dev/ref/databases/) that Django supports.

Instructions below are also specific to a machine running Ubuntu. If your
targetted environment doesn't run Ubuntu you will have to satisfy the 
requirements below (specific to the distribution you are using) and then attempt
to run the application.

###Requirements:

 * Apache 2 (or an alternate, see above)
 * mod_wsgi
 * MySQL (or an alternate, see above)
 * Python MySQL bindings (or an alternate, see above)
 * Python Imaging Library (PIL)
 * Django 1.4.0
 * GraphViz Library
 * Perl Text::CSV package
 * Django libraries:
  * ReCaptcha client
  * Easy thumbnails
  * OAuth2
  <br/>
  
You will also have to sign up for specific API keys and mention settings at
settings.py (Step #6 below)
  
###Instructions:

1)  Most of the above packages can be installed on a Ubuntu machine with the
following; even if you have a fresh install of Ubuntu. Missing packages (or all)
are installed. It's also assumed that you'd want to install the application
in your home folder, merely as an example (throughout the document):

<code>~$ sudo apt-get install git apache2 libapache2-mod-wsgi mysql-server libmysqlclient-dev </code><br/>
<code>~$ sudo apt-get install python-pip python-mysqldb libtext-csv-perl graphviz python-imaging</code>

2) Install Django 1.4.0 and the libraries AfterGlow requires:

<code>~$ sudo pip install Django==1.4.0 recaptcha-client easy_thumbnails oauth2</code>

3)  Clone this repository to obtain the application files:

<code>~$ git clone https://github.com/ayrus/afterglow-cloud.git</code>

4) Change permissions of certain folders to rwxrwxrwx (these folders are written
to by Apache while performing various operations):

<code>~$ cd afterglow-cloud/afterglow\_cloud/</code> <br/>
<code>~/afterglow-cloud/afterglow\_cloud$ chmod 777 user\_config/ user\_data/ user\_logs/ user\_logs\_parsed/<br/>
afterglow\_cloud/app/static/gallery/ afterglow\_cloud/app/static/gallery\_thumbs/ afterglow\_cloud/app/static/rendered/</code>

5) Create a database for AfterGlow to use (this example will use the database
name as "af").

<code>$ mysql -u user -p</code>

> Enter password: <br/>
        Welcome to the MySQL monitor.  Commands end with ; or \g.
        
Once logged in to the MySQL prompt, create the database:

<code>mysql> create database af;</code>

>Query OK, 1 row affected (0.00 sec)

6) Edit <code>settings.py</code> at afterglow\_cloud/settings.py (if you're currently in 
~/afterglow-cloud/afterglow\_cloud). This file contains important configuration
for the application to run. You'll have to edit Lines #10-88 with the 
instructions inside. The file has been commented in detail to help you out.

7) Create tables in the database with Django's <code>syncdb</code> command.

<code>~/afterglow-cloud/afterglow_cloud$ python ../manage.py syncdb</code>

If everything went well, you should see something like this:

>Creating tables ...<br/>
>Creating table auth_permission<br/>
>.<br/>
>.<br/>
>.<br/>
>Installing custom SQL ...<br/>
>Installing indexes ...<br/>
>Installed 0 object(s) from 0 fixture(s)<br/>

8) At this point, the application should be ready to run in a development
environment (with django's <code>runserver</code>). To deploy it on Apache with
<code>mod_wsgi</code>:

Open <code>/etc/apache2/httpd.conf</code> in an editor and add the following: <br/>
(your username is assumed to be foo, and as indicated earlier it's assumed
that you've cloned the application files to your home folder).


    WSGIPythonPath /home/foo/afterglow-cloud/afterglow_cloud

    Alias /static/ /home/foo/afterglow-cloud/afterglow_cloud/afterglow_cloud/app/static/

    <Directory /home/foo/afterglow-cloud/afterglow_cloud/afterglow_cloud/app/static>
    Order deny,allow
    Allow from all
    </Directory>

    WSGIScriptAlias / /home/foo/afterglow-cloud/afterglow_cloud/afterglow_cloud/wsgi.py

    <Directory /home/foo/afterglow-cloud/afterglow_cloud/afterglow_cloud>
    <Files wsgi.py>
    Order deny,allow
    Allow from all
    </Files>
    </Directory>

__Note__: Several assumptions have been made above. <br/>

 * You do __not__ have any sites enabled on Apache. If you do, ideally the
 <code>WSGIPythonPath</code> declaration goes in <code>/etc/apache2/httpd.conf</code>
 and the rest of the above should go in your <code>VirtualHost</code> declaration for the
 site you want to enable/serve the application with.
 
 * It is also assumed that you'd want to use Apache to serve the static files
 as well. You can however serve it with another dedicated server as mentioned
 in the [documentation](https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/#serving-files).
 
9) Reload and restart apache:

<code>~$ sudo service apache2 reload</code> <br/>
<code>~$ sudo service apache2 restart</code>

You should now have the application running in complete from your Apache server. <br/>
(if you followed these instructions as-is, this would ideally be at 
http://localhost ).


Links
-----

A first version of this application (development version) can be found in a
seperate tree <code>first-version</code> 

Commit: ayrus/afterglow-cloud@86e55a923edcd0461137a81a2a6ea13f6d58b9fb

Blog post detailing the features available in the first version can be viewed
[here](http://honeynet.org/node/890).

Contacts / Bugs
---------------

You can reach or report a bug using the contact form available on the [demo](http://andromeda.ayrus.net:8080).
