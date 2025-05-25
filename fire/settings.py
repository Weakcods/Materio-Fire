# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'joshuaaaaa2.pythonanywhere.com',
    '.pythonanywhere.com'  
]

SECRET_KEY = 'django-insecure-your-secret-key-here' 

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/joshuaaaaa2/fire/db.sqlite3',
    }
} 