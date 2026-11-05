import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'development-only-folio-change-before-deploy')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')
INSTALLED_APPS = ['jazzmin', 'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'catalog', 'circulation']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:5173', 'http://localhost:5173']
JAZZMIN_SETTINGS = {'site_title': 'Fólio | Administração', 'site_header': 'Fólio', 'site_brand': 'Fólio · Biblioteca', 'welcome_sign': 'Seu acervo, bem cuidado.', 'copyright': 'Fólio', 'search_model': ['catalog.Book', 'circulation.Reader'], 'show_sidebar': True, 'navigation_expanded': True, 'icons': {'catalog.Book': 'fas fa-book', 'catalog.Copy': 'fas fa-barcode', 'catalog.Author': 'fas fa-pen-nib', 'circulation.Loan': 'fas fa-exchange-alt', 'circulation.Reader': 'fas fa-users', 'circulation.Reservation': 'fas fa-bookmark'}, 'topmenu_links': [{'name': 'Painel Preact', 'url': 'http://127.0.0.1:5173', 'new_window': True}], 'show_ui_builder': False}
JAZZMIN_UI_TWEAKS = {'theme': 'flatly', 'default_theme_mode': 'auto', 'navbar': 'navbar-dark', 'sidebar': 'sidebar-dark-success', 'brand_colour': 'navbar-success', 'accent': 'accent-success'}
