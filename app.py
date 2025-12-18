#!/usr/bin/env python3
"""
App.py - File Principale della Macchina delle Risposte
=====================================================

Punto di ingresso principale per l'applicazione RAG con interfaccia grafica.
Orchestra l'inizializzazione del backend e dell'interfaccia utente.

Autore: Zampier Zago
Versione: 2.0.0
"""

import customtkinter as ctk
import sys
import os

# Aggiungi le directory al path per gli import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import componenti applicazione
try:
    from config.settings import AppConfig, AppTheme, print_startup_banner, print_system_info, log_info, log_error
    from backend.rag_engine import RAGBackend
    from ui.chat_interface import ChatApp
except ImportError as e:
    print(f"❌ ERRORE IMPORT: {e}")
    print("Assicurati che tutte le directory (config/, backend/, ui/) esistano e contengano i file necessari.")
    sys.exit(1)


def check_dependencies():
    """
    Verifica che tutte le dipendenze critiche siano installate.
    
    Returns:
        bool: True se tutte le dipendenze sono disponibili
    """
    missing_deps = []
    
    # Verifica dipendenze LangChain
    try:
        import langchain_chroma
        import langchain_huggingface
        import langchain_openai
        import langchain_core
    except ImportError as e:
        missing_deps.append(f"LangChain: {e}")
    
    # Verifica CustomTkinter
    try:
        import customtkinter
    except ImportError:
        missing_deps.append("CustomTkinter non installato")
    
    # Verifica dotenv
    try:
        import dotenv
    except ImportError:
        missing_deps.append("python-dotenv non installato")
    
    if missing_deps:
        print("❌ DIPENDENZE MANCANTI:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n💡 Installa le dipendenze con:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def configure_ui_theme():
    """Configura il tema dell'interfaccia CustomTkinter."""
    try:
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        log_info("Tema UI configurato: Dark Mode")
    except Exception as e:
        log_error(f"Errore configurazione tema: {e}")


def initialize_backend():
    """
    Inizializza il backend RAG.
    
    Returns:
        RAGBackend: Istanza del backend inizializzato
    """
    try:
        log_info("Inizializzazione backend RAG in corso...")
        backend = RAGBackend()
        
        # Verifica stato del sistema
        status = backend.get_system_status()
        if status["status"] == "operational":
            log_info("✅ Backend RAG operativo")
        elif status["status"] == "degraded":
            log_info("⚠️ Backend in modalità degradata - alcune funzionalità potrebbero essere limitate")
        else:
            log_error("❌ Backend non funzionante")
        
        return backend
        
    except Exception as e:
        log_error(f"Errore fatale nell'inizializzazione backend: {e}")
        raise


def handle_startup_warnings(backend):
    """
    Gestisce avvisi e problemi all'avvio.
    
    Args:
        backend (RAGBackend): Istanza del backend
    """
    # Controlla se il database è vuoto
    if not backend.compression_retriever:
        print("\n⚠️  ATTENZIONE: Sistema di recupero documenti non disponibile")
        print("   Possibili cause:")
        print("   • Database vettoriale vuoto o non esistente")
        print("   • Cartella 'storage' mancante")
        print("   • Errori durante l'inizializzazione")
        print("\n💡 Soluzioni:")
        print("   1. Esegui 'python ingest.py' per creare/aggiornare il database")
        print("   2. Assicurati che la cartella 'DATASET' contenga file PDF")
        print("   3. Verifica le configurazioni nel file .env")
        
        response = input("\n❓ Vuoi continuare comunque? (y/N): ").lower().strip()
        if response not in ['y', 'yes', 'si', 'sì']:
            print("⏹️ Avvio annullato dall'utente")
            sys.exit(0)
    
    # Controlla configurazioni
    paths_status = AppConfig.validate_paths()
    if not paths_status["dataset_exists"]:
        print(f"\n⚠️  Cartella '{AppConfig.DATASET_PATH}' non trovata")
        print("   Creare la cartella e inserire i file PDF da processare")


def launch_application(backend):
    """
    Avvia l'interfaccia grafica dell'applicazione.
    
    Args:
        backend (RAGBackend): Backend RAG inizializzato
    """
    try:
        log_info("Avvio interfaccia grafica...")
        
        # Crea e configura l'applicazione
        app = ChatApp(backend=backend)
        
        # Configurazioni finestra
        app.minsize(AppConfig.WINDOW_MIN_WIDTH, AppConfig.WINDOW_MIN_HEIGHT)
        app.protocol("WM_DELETE_WINDOW", lambda: on_closing(app))
        
        log_info("🚀 Applicazione pronta!")
        print_usage_tips()
        
        # Avvia loop principale
        app.mainloop()
        
    except Exception as e:
        log_error(f"Errore fatale nell'interfaccia grafica: {e}")
        raise


def print_usage_tips():
    """Stampa suggerimenti per l'uso dell'applicazione."""
    print("\n" + "="*60)
    print("💡 SUGGERIMENTI PER L'USO:")
    print("   • Fai domande specifiche su normative alimentari")
    print("   • Le risposte includeranno citazioni cliccabili alle fonti")
    print("   • Usa il pannello laterale per vedere i documenti disponibili")
    print("   • Clicca sui bottoni [N] nelle risposte per vedere le fonti")
    print("   • L'AI rifiuterà educatamente domande fuori ambito")
    print("="*60)


def on_closing(app):
    """
    Gestisce la chiusura dell'applicazione.
    
    Args:
        app: Istanza dell'applicazione
    """
    try:
        log_info("Chiusura applicazione in corso...")
        
        # Cleanup eventuali risorse
        if hasattr(app, 'backend'):
            # Qui si potrebbero aggiungere operazioni di cleanup del backend
            pass
        
        app.destroy()
        log_info("👋 Applicazione chiusa correttamente")
        
    except Exception as e:
        log_error(f"Errore durante la chiusura: {e}")
    finally:
        sys.exit(0)


def main():
    """
    Funzione principale - punto di ingresso dell'applicazione.
    Orchestra l'intero processo di avvio.
    """
    try:
        # Banner di avvio
        print_startup_banner()
        print_system_info()
        
        # Verifica dipendenze
        log_info("Verifica dipendenze in corso...")
        if not check_dependencies():
            sys.exit(1)
        
        # Configura tema UI
        configure_ui_theme()
        
        # Inizializza backend
        backend = initialize_backend()
        
        # Gestisci eventuali avvisi
        handle_startup_warnings(backend)
        
        # Avvia applicazione
        launch_application(backend)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruzione richiesta dall'utente (Ctrl+C)")
        log_info("Arresto forzato tramite Ctrl+C")
        
    except Exception as e:
        log_error(f"ERRORE CRITICO all'avvio: {e}")
        print(f"\n❌ ERRORE FATALE: {e}")
        print("\n🔧 POSSIBILI SOLUZIONI:")
        print("   1. Verifica installazione dipendenze: pip install -r requirements.txt")
        print("   2. Controlla configurazione file .env")
        print("   3. Esegui 'python ingest.py' per inizializzare il database")
        print("   4. Verifica presenza cartelle 'DATASET' e 'storage'")
        print(f"   5. Controlla il file '{AppConfig.CRASH_LOG_FILE}' per dettagli")
        
        # Pausa per permettere la lettura dell'errore
        input("\n⏸️  Premi ENTER per chiudere...")
        sys.exit(1)
        
    finally:
        log_info("=== SESSIONE TERMINATA ===")


# === ENTRY POINT ===
if __name__ == "__main__":
    main()