"""
Configurazioni e Tema dell'Applicazione
Contiene tutte le configurazioni centralizzate, temi colori e utility globali.

Componenti:
- AppTheme: Configurazione colori e stili
- AppConfig: Configurazioni applicazione
- Utility functions: Funzioni di supporto globali
"""

import sys
import traceback
import datetime
import os
from typing import Dict, Any


class AppTheme:
    """
    Configurazione centralizzata per tema e colori dell'applicazione.
    
    Definisce tutti i colori, font e stili utilizzati nell'interfaccia
    per garantire consistenza visiva in tutta l'applicazione.
    """
    
    # === COLORI PRINCIPALI ===
    BACKGROUND = "#242424"              # Sfondo principale applicazione
    CHAT_BACKGROUND = "#1E1E1E"         # Sfondo area chat
    TEXT_COLOR = "#FFFFFF"              # Colore testo principale
    
    # === COLORI MESSAGGI ===
    USER_BUBBLE = "#00519E"             # Colore messaggi utente
    ASSISTANT_BUBBLE = "#3D3D3D"        # Colore messaggi assistente
    
    # === COLORI ACCENTO ===
    PRIMARY_ACCENT = "#1F6AA5"          # Colore primario (bottoni, link)
    SECONDARY_ACCENT = "#2196F3"        # Colore secondario
    
    # === COLORI CITAZIONI E FONTI ===
    SOURCE_BUTTON_COLOR = "#1E88E5"     # Colore bottoni citazioni
    SOURCE_BUTTON_HOVER = "#1565C0"     # Colore hover citazioni
    
    # === COLORI STATO ===
    ERROR_COLOR = "#FF5722"             # Colore errori
    SUCCESS_COLOR = "#4CAF50"           # Colore successo
    WARNING_COLOR = "#FF9800"           # Colore avvisi
    INFO_COLOR = "#2196F3"              # Colore informazioni
    
    # === FONT E TIPOGRAFIA ===
    FONT_FAMILY = ("Arial", 14)         # Font principale
    FONT_SMALL = ("Arial", 10)          # Font piccolo
    FONT_LARGE = ("Arial", 16)          # Font grande
    FONT_TITLE = ("Arial", 16, "bold")  # Font titoli
    FONT_MONO = ("Courier New", 12)     # Font monospaziato
    
    # === DIMENSIONI E SPAZIATURA ===
    BORDER_RADIUS = 10                  # Raggio angoli arrotondati
    PADDING_SMALL = 5                   # Padding piccolo
    PADDING_MEDIUM = 10                 # Padding medio
    PADDING_LARGE = 15                  # Padding grande
    
    # === COLORI HOVER E FOCUS ===
    HOVER_COLOR = "#2A2A2A"             # Colore hover generico
    FOCUS_COLOR = "#3A3A3A"             # Colore focus
    DISABLED_COLOR = "#666666"          # Colore elementi disabilitati
    
    @classmethod
    def get_theme_dict(cls) -> Dict[str, str]:
        """
        Restituisce tutti i colori del tema in un dizionario.
        
        Returns:
            Dict[str, str]: Dizionario con tutti i colori definiti
        """
        return {
            attr: getattr(cls, attr) 
            for attr in dir(cls) 
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        }


class AppConfig:
    """
    Configurazioni generali dell'applicazione.
    
    Contiene tutte le impostazioni configurabili dell'app
    come percorsi file, limiti, timeout, ecc.
    """
    
    # === INFORMAZIONI APPLICAZIONE ===
    APP_NAME = "AI-Regulatory-Consultant-RAG"
    APP_VERSION = "2.0.0"
    APP_AUTHOR = "Zampier Zago"
    APP_COPYRIGHT = "© Tutti i diritti riservati • Powered By Zampier Zago"
    APP_DESCRIPTION = "Consulente AI per Normative Alimentari"
    
    # === PERCORSI FILE ===
    DATASET_PATH = "DATASET"                    # Cartella documenti PDF
    STORAGE_PATH = "storage"                    # Database vettoriale
    KNOWLEDGE_SCOPE_FILE = "knowledge_scope.json"  # File ambito conoscenza
    CRASH_LOG_FILE = "crash_log.txt"            # Log errori fatali
    BACKEND_LOG_FILE = "backend_errors.log"     # Log errori backend
    
    # === CONFIGURAZIONI RAG ===
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    LLM_MAIN_MODEL = "google/gemini-flash-1.5"
    LLM_ROUTER_MODEL = "google/gemini-flash-1.5"
    
    # === API CONFIGURAZIONI ===
    OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
    API_TIMEOUT = 60                            # Timeout richieste API (secondi)
    ROUTER_TIMEOUT = 20                         # Timeout router (secondi)
    MAX_RETRIES = 2                             # Massimi tentativi richiesta
    
    # === CONFIGURAZIONI RETRIEVER ===
    RETRIEVER_K = 20                            # Documenti recuperati inizialmente
    RERANK_TOP_N = 5                           # Documenti dopo re-ranking
    RERANK_MODEL = "ms-marco-MiniLM-L-12-v2"   # Modello re-ranking
    
    # === CONFIGURAZIONI UI ===
    WINDOW_WIDTH = 1200                         # Larghezza finestra
    WINDOW_HEIGHT = 800                         # Altezza finestra
    WINDOW_MIN_WIDTH = 800                      # Larghezza minima
    WINDOW_MIN_HEIGHT = 600                     # Altezza minima
    
    # === CONFIGURAZIONI CHAT ===
    MAX_MESSAGE_LENGTH = 5000                   # Lunghezza massima messaggio
    MESSAGE_WRAP_LENGTH = 600                   # Lunghezza wrapping testo
    TOOLTIP_DELAY = 1000                        # Ritardo tooltip (ms)
    
    # === CONFIGURAZIONI LOGGING ===
    LOG_FORMAT = "[{timestamp}] {level}: {message}"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """
        Restituisce tutte le configurazioni in un dizionario.
        
        Returns:
            Dict[str, Any]: Dizionario con tutte le configurazioni
        """
        return {
            attr: getattr(cls, attr) 
            for attr in dir(cls) 
            if not attr.startswith('_') and not callable(getattr(cls, attr))
        }

    @classmethod
    def validate_paths(cls) -> Dict[str, bool]:
        """
        Valida l'esistenza dei percorsi critici.
        
        Returns:
            Dict[str, bool]: Stato di validazione per ogni percorso
        """
        return {
            "dataset_exists": os.path.exists(cls.DATASET_PATH),
            "storage_exists": os.path.exists(cls.STORAGE_PATH),
            "knowledge_scope_exists": os.path.exists(cls.KNOWLEDGE_SCOPE_FILE)
        }


# === UTILITY FUNCTIONS GLOBALI ===

def setup_global_exception_handler():
    """
    Configura il gestore globale degli errori non gestiti.
    Salva automaticamente tutti gli errori fatali in un log.
    """
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        """Handler globale per catturare e loggare tutti gli errori non gestiti."""
        # Mostra errore anche in console
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
        # Prepara dettagli errore
        error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        timestamp = datetime.datetime.now().strftime(AppConfig.LOG_DATE_FORMAT)
        
        log_content = f"""{'='*60}
CRASH LOG: {timestamp}
{'='*60}
{error_details}
{'='*60}

"""
        
        print(f"\n🚨 ERRORE FATALE RILEVATO 🚨")
        print(f"Timestamp: {timestamp}")
        print(f"Dettagli salvati in: {AppConfig.CRASH_LOG_FILE}")
        print("="*50)
        
        # Salva nel file di log
        try:
            with open(AppConfig.CRASH_LOG_FILE, "a", encoding='utf-8') as log_file:
                log_file.write(log_content)
        except Exception as log_error:
            print(f"❌ Errore nel salvare il crash log: {log_error}")

    sys.excepthook = global_exception_handler


def log_info(message: str, category: str = "INFO"):
    """
    Registra un messaggio informativo.
    
    Args:
        message (str): Messaggio da registrare
        category (str): Categoria del log
    """
    timestamp = datetime.datetime.now().strftime(AppConfig.LOG_DATE_FORMAT)
    print(f"[{timestamp}] {category}: {message}")


def log_error(error_details: str, error_type: str = "ERROR"):
    """
    Registra un errore nel file di log del backend.
    
    Args:
        error_details (str): Dettagli dell'errore
        error_type (str): Tipo di errore
    """
    timestamp = datetime.datetime.now().strftime(AppConfig.LOG_DATE_FORMAT)
    log_entry = AppConfig.LOG_FORMAT.format(
        timestamp=timestamp,
        level=error_type,
        message=error_details
    ) + "\n"
    
    try:
        with open(AppConfig.BACKEND_LOG_FILE, "a", encoding='utf-8') as log_file:
            log_file.write(log_entry)
        print(f"🔍 [{error_type}] {error_details}")
    except Exception as e:
        print(f"❌ Errore nel logging: {e}")


def ensure_directories():
    """
    Assicura che tutte le directory necessarie esistano.
    Crea le directory mancanti automaticamente.
    """
    directories = [
        AppConfig.DATASET_PATH,
        AppConfig.STORAGE_PATH,
        "config",
        "ui", 
        "backend",
        "assets"  # Per eventuali icone/risorse
    ]
    
    created_dirs = []
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                created_dirs.append(directory)
        except Exception as e:
            log_error(f"Impossibile creare directory {directory}: {e}")
    
    if created_dirs:
        log_info(f"Directory create: {', '.join(created_dirs)}")


def validate_environment() -> Dict[str, Any]:
    """
    Valida l'ambiente di esecuzione dell'applicazione.
    
    Returns:
        Dict[str, Any]: Stato di validazione dell'ambiente
    """
    validation_result = {
        "python_version": sys.version,
        "platform": sys.platform,
        "paths": AppConfig.validate_paths(),
        "environment_valid": True,
        "warnings": [],
        "errors": []
    }
    
    # Controlla versione Python
    if sys.version_info < (3, 8):
        validation_result["errors"].append("Python 3.8+ richiesto")
        validation_result["environment_valid"] = False
    
    # Controlla percorsi critici
    if not validation_result["paths"]["dataset_exists"]:
        validation_result["warnings"].append(f"Directory {AppConfig.DATASET_PATH} non trovata")
    
    if not validation_result["paths"]["storage_exists"]:
        validation_result["warnings"].append(f"Directory {AppConfig.STORAGE_PATH} non trovata")
    
    return validation_result


def format_file_size(size_bytes: int) -> str:
    """
    Formatta la dimensione di un file in formato leggibile.
    
    Args:
        size_bytes (int): Dimensione in bytes
        
    Returns:
        str: Dimensione formattata (es. "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and unit_index < len(size_units) - 1:
        size /= 1024.0
        unit_index += 1
    
    return f"{size:.1f} {size_units[unit_index]}"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Tronca un testo se supera la lunghezza massima.
    
    Args:
        text (str): Testo da troncare
        max_length (int): Lunghezza massima
        suffix (str): Suffisso da aggiungere
        
    Returns:
        str: Testo troncato se necessario
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def create_knowledge_scope_template():
    """
    Crea un file template per il knowledge scope se non esiste.
    Definisce gli argomenti di competenza dell'AI.
    """
    if os.path.exists(AppConfig.KNOWLEDGE_SCOPE_FILE):
        return  # File già esistente
    
    default_scope = {
        "scope": [
            "Normative alimentari europee (Regolamenti UE)",
            "Regolamenti ministeriali italiani",
            "Etichettatura prodotti alimentari",
            "Sicurezza alimentare e sistema HACCP",
            "Additivi e conservanti autorizzati",
            "Controlli sanitari e ispezioni ASL",
            "Certificazioni di qualità alimentare",
            "Allergeni e dichiarazioni obbligatorie",
            "Limiti microbiologici negli alimenti",
            "Tracciabilità e rintracciabilità",
            "Novel food e alimenti innovativi",
            "Sostanze contaminanti e residui",
            "Materiali a contatto con alimenti (MOCA)",
            "Etichettatura nutrizionale obbligatoria",
            "Claims nutrizionali e salutistici",
            "Agricoltura biologica e certificazione",
            "Denominazioni di origine (DOP, IGP)",
            "Controllo ufficiale degli alimenti",
            "Frodi alimentari e adulterazioni",
            "Imballaggio e confezionamento alimenti"
        ],
        "description": "Ambito di competenza dell'AI per normative alimentari",
        "version": "2.0",
        "last_updated": datetime.datetime.now().isoformat()
    }
    
    try:
        import json
        with open(AppConfig.KNOWLEDGE_SCOPE_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_scope, f, ensure_ascii=False, indent=2)
        log_info(f"File {AppConfig.KNOWLEDGE_SCOPE_FILE} creato con successo")
    except Exception as e:
        log_error(f"Errore nella creazione del knowledge scope: {e}")


def print_startup_banner():
    """Stampa il banner di avvio dell'applicazione."""
    banner = f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                🤖 AI-Regulatory-Consultant-RAG                ║
║                                                          ║
║              Consulente AI Normative Alimentari         ║
║                                                          ║
║                     Versione {AppConfig.APP_VERSION}                    ║
║                                                          ║
║              {AppConfig.APP_COPYRIGHT}           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_system_info():
    """Stampa informazioni sul sistema all'avvio."""
    print("🔧 INFORMAZIONI SISTEMA:")
    print(f"   • Python: {sys.version.split()[0]}")
    print(f"   • Piattaforma: {sys.platform}")
    print(f"   • Directory di lavoro: {os.getcwd()}")
    
    # Valida ambiente
    validation = validate_environment()
    if validation["environment_valid"]:
        print("   • Ambiente: ✅ Validato")
    else:
        print("   • Ambiente: ❌ Problemi rilevati")
        for error in validation["errors"]:
            print(f"     - ERRORE: {error}")
    
    for warning in validation["warnings"]:
        print(f"     - ATTENZIONE: {warning}")
    
    print()


# === INIZIALIZZAZIONE AUTOMATICA ===
def initialize_app_environment():
    """
    Inizializza completamente l'ambiente dell'applicazione.
    Chiamata automatica all'import del modulo.
    """
    # Configura handler errori globali
    setup_global_exception_handler()
    
    # Assicura esistenza directory
    ensure_directories()
    
    # Crea template knowledge scope se necessario
    create_knowledge_scope_template()
    
    log_info("Ambiente applicazione inizializzato", "SETUP")


# Esegui inizializzazione quando il modulo viene importato
initialize_app_environment()