import os
import sys
import subprocess
import time
import webbrowser
import socket

def get_local_ip():
    try:
        # Crea un socket dummy para obtener la IP interna activa de la interfaz de red
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def setup_venv():
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(workspace_dir, '.venv')
    
    # 1. Create virtual environment if it doesn't exist
    if not os.path.isdir(venv_dir):
        print(">>> Creando entorno virtual (.venv)... Esto puede tardar unos momentos.")
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
            print(">>> Entorno virtual creado exitosamente.")
        except subprocess.CalledProcessError as e:
            print(f"Error al crear el entorno virtual: {e}")
            sys.exit(1)
            
    # 2. Determine paths for venv executables (Windows specific)
    pip_path = os.path.join(venv_dir, 'Scripts', 'pip.exe')
    python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
    
    # Fallback for non-Windows if needed (though user is on Windows)
    if not os.path.exists(pip_path):
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
        python_path = os.path.join(venv_dir, 'bin', 'python')
        
    # 3. Install requirements
    requirements_file = os.path.join(workspace_dir, 'requirements.txt')
    if os.path.exists(requirements_file):
        print(">>> Instalando dependencias desde requirements.txt...")
        try:
            subprocess.run([pip_path, 'install', '-r', requirements_file], check=True)
            print(">>> Dependencias instaladas con éxito.")
        except subprocess.CalledProcessError as e:
            print(f"Error al instalar las dependencias: {e}")
            sys.exit(1)
    else:
        print("Error: No se encontró el archivo requirements.txt.")
        sys.exit(1)
        
    return python_path

def main():
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    python_path = setup_venv()
    
    desktop_path = os.path.join(workspace_dir, 'desktop.py')
    if not os.path.exists(desktop_path):
        print(f"Error: No se encontró el archivo de escritorio '{desktop_path}'")
        sys.exit(1)
        
    print("\n" + "="*60)
    print("  >>> INICIANDO EL DEPÓSITO INTELIGENTE <<<")
    print("  Se abrirá una ventana de aplicación en unos segundos.")
    print("  Para cerrar el programa, simplemente cierra la ventana de la aplicación.")
    print("="*60 + "\n")
    
    # Run the desktop app as a subprocess
    process = None
    try:
        # Start desktop application
        process = subprocess.Popen([python_path, desktop_path], cwd=workspace_dir)
        
        # Wait for the subprocess to finish (runs indefinitely until closed)
        process.wait()
    except KeyboardInterrupt:
        print("\n>>> Cerrando la aplicación...")
        if process:
            process.terminate()
            process.wait()
        print(">>> Aplicación detenida. ¡Hasta luego!")
    except Exception as e:
        print(f"Ocurrió un error al ejecutar la aplicación: {e}")
        if process:
            process.kill()
        sys.exit(1)

if __name__ == '__main__':
    main()
