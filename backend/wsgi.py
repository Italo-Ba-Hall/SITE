# WSGI configuration for PythonAnywhere
# Place this file in your PythonAnywhere web app configuration

import sys
import os

# Add your project directory to the Python path
path = '/home/seu_usuario/mysite'  # Substitua 'seu_usuario' pelo seu username
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['ENVIRONMENT'] = 'production'

# Import your FastAPI app
from main import app

# WSGI application
application = app
