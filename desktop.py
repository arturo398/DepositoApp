import sys
import os
import webview
from app import app

def main():
    # Permitir descargas de archivos en la ventana de escritorio
    webview.settings['ALLOW_DOWNLOADS'] = True

    # Crear la ventana de escritorio y cargar la aplicación Flask
    webview.create_window(
        title="Depósito Inteligente",
        url=app,
        width=1200,
        height=800,
        min_size=(1000, 600),
        resizable=True
    )
    # Iniciar la interfaz nativa
    webview.start()

if __name__ == '__main__':
    main()
