"""
Launcher script for OverPilas Flask Application
This script starts the Flask server and opens the browser automatically
"""
import os
import sys
import webbrowser
import threading
from time import sleep

# Add the application directory to the path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(application_path)

# Import the Flask app
from app import app

def open_browser():
    """Open the browser after a short delay"""
    sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask app
    print("=" * 60)
    print("OverPilas - Sistema de Gestión de Baterías")
    print("=" * 60)
    print("\nServidor iniciado en: http://127.0.0.1:5000")
    print("\nEl navegador se abrirá automáticamente...")
    print("\nPara detener el servidor, presiona Ctrl+C")
    print("=" * 60)

    # Run Flask app without debug mode for production
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
