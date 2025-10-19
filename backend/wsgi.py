# WSGI configuration for PythonAnywhere
# Place this file in your PythonAnywhere web app configuration

import os
import sys

# Add your project directory to the Python path
path = '/home/seu_usuario/mysite'  # Substitua 'seu_usuario' pelo seu username
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['ENVIRONMENT'] = 'production'

# Import must be after path and environment setup for proper loading
from main import app  # noqa: E402

# WSGI application
application = app
