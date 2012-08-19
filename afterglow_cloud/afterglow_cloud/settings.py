import os.path

DEBUG = False
TEMPLATE_DEBUG = DEBUG
    
#    
# Following settings (until mentioned; are all required and necessary.
#

# Define administrators of the website. Contact points defined here will be
# as a source for sending debug information through demail when a user encounters
# a 500 server error.
# Add values as a tuple of (Name, Email) pair.
ADMINS = (
    #('Bob', 'bob@foo.bar'),
)

# Define a Django compatible RDBMS module; with authentication details.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '', # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

# Define your SMTP settings below for AfterGlow to use for the contact form and
# sending error reports to administrators.
#
# -If you don't have a SMTP server, as such, you can use (for example) a GMail
# -account to relay your emails. Define HOST as 'smtp.gmail.com'; PORT as 587 and
# -'USE_TLS' as True. Define your username (someuser@gmail.com) and password 
# -as well.
#
EMAIL_USE_TLS = True
EMAIL_HOST = ''
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

# Define the 'From email' used while sending an email. This can be any email.
AF_FROM_EMAIL = ""

# Define a list of emails to send copies of each contact form request.
AF_TO_EMAILS = ['']

# Define API keys for RECAPTCHA used in generating CAPTCHA images in the
# application. Keys can be obtained here:
#	https://www.google.com/recaptcha/admin/create
#
AF_RECAPTCHA_PUBLIC_KEY = ''
AF_RECAPTCHA_PRIVATE_KEY = ''

# AfterGlow intergrates with Loggly.com's accounts as a data source. For this
# purpose OAuth 1.0 authentication is used. Obtain and define keys from 
# Loggly.com as a developer account. More information can be found here:
#	http://wiki.loggly.com/oauth
#
LOGGLY_OAUTH_CONSUMER_KEY = ""
LOGGLY_OAUTH_CONSUMER_SECRET = ""

# A callback URL for loggly. Enter the root location of the application
# suffixed by "/callback". You *cannot* change the callback URL and the suffix
# should *not* have a terminating backslash.
# For example: If your app is running at http://localhost/afterglow then this
#		setting should be defined as:
#		"http://localhost/afterglow/callback
#
LOGGLY_OAUTH_CALLBACK = ""

# Enter the absolute path to the static directory. Static directory is at
# 'afterglow_cloud/app/static'. For example:
#	If the app is running from your home folder and your username is foo,
#	then this setting should be:
#	"/home/foo/afterglow-cloud/afterglow_cloud/afterglow_cloud/app/static"
#
STATICFILES_DIRS = (
    "",
)

# Generate a unique secret key for this instance of AfterGlow.
# NB: This setting is essential for ensuring Django's internal security measures
# are in place.
SECRET_KEY = ''


#
#
# *Settings below can be left as-is.*
# Please change only if you know what you're up to.
#
#

SERVER_EMAIL = AF_FROM_EMAIL
MANAGERS = ADMINS
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'afterglow_cloud.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'afterglow_cloud.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), '../templates').replace('\\','/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'afterglow_cloud.app',
    'easy_thumbnails',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
