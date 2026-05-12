import subprocess
import sys
from pathlib import Path

try:
    from app import create_app
except ImportError:
    requirements_path = Path(__file__).with_name("requirements.txt")
    print("Project dependencies not found, installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
    from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
