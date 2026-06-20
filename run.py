import os
import subprocess
import sys
import time

def main():
    print("=== Iniciando SmartHelp (API + Site) ===")
    
    # 1. Porta interna para a API FastAPI
    api_port = "8000"
    
    # 2. Porta externa (Render usa a variavel , local usa 8501)
    streamlit_port = os.getenv("PORT", "8501")
    
    print(f"Iniciando a API FastAPI na porta interna {api_port}...")
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", api_port
    ])
    
    # Aguarda a API subir
    time.sleep(3)
    
    print(f"Iniciando a Interface Streamlit na porta {streamlit_port}...")
    streamlit_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app/views/app_view.py", 
        "--server.port", streamlit_port, 
        "--server.address", "0.0.0.0"
    ])
    
    try:
        while True:
            if api_process.poll() is not None:
                print("A API parou inesperadamente.")
                break
            if streamlit_process.poll() is not None:
                print("O Streamlit parou inesperadamente.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando todos os servicos...")
    finally:
        api_process.terminate()
        streamlit_process.terminate()
        print("Servicos parados.")

if __name__ == "__main__":
    main()