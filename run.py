# run.py
import subprocess
import sys

try:
   from app import create_app
except ImportError:
   print("Flask not found, installing...")
   subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
   from app import create_app

app = create_app()

if __name__ == '__main__':
   app.run(debug=True)