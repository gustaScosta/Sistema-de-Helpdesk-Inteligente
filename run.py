import subprocess
import sys
import time

def main():
    print("=== Iniciando SmartHelp (API + Site) ===")
    
    # 1. Inicia a API FastAPI na porta 8000
    print("Iniciando a API FastAPI na porta 8000...")
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"
    ])
    
    # Aguarda 2 segundos para a API subir
    time.sleep(2)
    
    # 2. Inicia o Streamlit na porta 8501
    print("Iniciando a Interface Streamlit na porta 8501...")
    streamlit_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app/views/app_view.py", "--server.port", "8501", "--server.address", "0.0.0.0"
    ])
    
    try:
        while True:
            # Verifica se algum processo morreu
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
        print("Servicos parados com sucesso.")

if __name__ == "__main__":
    main()