#
# gunicorn configuration file
#

# Address and port to bind to. 0.0.0.0 translates to your external
# IP address
bind = "0.0.0.0:7214"

# Number of instances to run.
workers = 2

# Name of app
wsgi_app = "app:app"
