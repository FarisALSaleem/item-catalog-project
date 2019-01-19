import sys

sys.path.insert(0, "/var/www/item-catalog-project/")

from app import app as application

application.secret_key = 'super_secret_key'