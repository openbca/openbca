"""
Launcher script for OpenBCA Streamlit app.
Properly starts Streamlit server with correct paths in PyInstaller bundle.
"""
import sys
from pathlib import Path

# Ensure repo root is on path for imports
if getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(sys._MEIPASS)))
else:
    sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Import Streamlit's CLI after paths are set up
    from streamlit.web import cli as stcli
    
    # Get the path to the Streamlit app
    if getattr(sys, 'frozen', False):
        app_script = Path(sys._MEIPASS) / "streamlit_test" / "Entrypoint.py"
    else:
        app_script = Path(__file__).parent / "streamlit_test" / "Entrypoint.py"
    
    # Set up Streamlit CLI arguments with proper config
    sys.argv = [
        "streamlit",
        "run",
        str(app_script),
        "--server.port=8501",
        "--global.developmentMode=false",
        "--logger.level=info",
    ]
    
    # Launch Streamlit
    sys.exit(stcli.main())
