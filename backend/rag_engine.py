"""
Backend RAG Engine - Sistema avanzato di Retrieval-Augmented Generation
con architettura multi-stadio, routing intelligente e re-ranking.

Questo modulo contiene tutta la logica per:
- Inizializzazione dei modelli LLM
- Configurazione del sistema di recupero documenti
- Routing intelligente delle query
- Catene RAG, conversazionali e di rifiuto
- Gestione delle risposte con citazioni
"""

import os
import json
import traceback
import datetime
from typing import Literal, Dict, Any, List
from operator import itemgetter

# Importazioni LangChain
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank


class RAGBackend:
    """
    Backend avanzato per RAG con architettura multi-stadio.
    """
    
    def __init__(self):
        """Inizializza il backend RAG con tutti i componenti necessari."""
        print("🚀 Inizializzazione del backend RAG con architettura multi-stadio...")
        
        # Inizializza attributi principali
        self.llm_main = None
        self.llm_router = None
        self.compression_retriever = None
        self.knowledge_scope = []
        self.full_chain = None
        
        # Carica componenti in ordine sequenziale
        self._initialize_llms()
        self._initialize_retriever()
        self._load_knowledge_scope()
        self._build_chain_architecture()
        
        print("✅ Backend RAG completamente inizializzato e operativo.")

    def _initialize_llms(self):
        """
        Inizializza i modelli LLM per generazione e routing.
        """
        try:
            # Configurazione API keys e base URL
            api_key = ".........................................................."
            api_base = "...................................................."
            
            # Modello principale per generazione risposte
            self.llm_main = ChatOpenAI(
                model="google/gemini-flash-1.5",  # Un modello potente per risposte di qualità
                temperature=0.1,
                max_retries=2,
                timeout=60,
                request_timeout=60,
                max_tokens=4096,  # CORREZIONE: Aggiunto limite token
                openai_api_key=api_key,
                openai_api_base=api_base
            )
            
            # Modello veloce ed economico per classificazione/routing
            self.llm_router = ChatOpenAI(
                model="google/gemini-flash-1.5", # CORREZIONE: Modello più adatto, veloce e stabile per il routing
                temperature=0,
                max_retries=2,
                timeout=20,
                request_timeout=20,
                max_tokens=50, # CORREZIONE: Aggiunto limite token
                openai_api_key=api_key,
                openai_api_base=api_base
            )
            
            print("✅ Modelli LLM (Main e Router) caricati con successo.")
            
        except Exception as e:
            print(f"❌ ERRORE nel caricamento dei modelli LLM: {e}")
            raise

    def _initialize_retriever(self):
        """
        Inizializza il sistema di recupero documenti con re-ranking.
        """
        try:
            embeddings_model = HuggingFaceEmbeddings(
                model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            vector_store = Chroma(
                persist_directory="storage", 
                embedding_function=embeddings_model
            )
            
            doc_count = vector_store._collection.count()
            if doc_count == 0:
                print("⚠️ ATTENZIONE: Il database vettoriale è vuoto. Eseguire prima 'python ingest.py'")
                self.compression_retriever = None
                return
            else:
                print(f"✅ Database caricato con {doc_count} documenti.")
            
            base_retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 20}
            )
            
            compressor = FlashrankRerank(top_n=8, model="ms-marco-MiniLM-L-12-v2")
            
            self.compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor, 
                base_retriever=base_retriever
            )
            
            print("✅ Sistema di recupero documenti con re-ranking configurato.")
            
        except Exception as e:
            print(f"❌ ERRORE CRITICO nel caricamento del database: {e}")
            print("Assicurati che la cartella 'storage' esista e contenga il database.")
            self.compression_retriever = None

    def _load_knowledge_scope(self):
        """
        Carica l'ambito di conoscenza per il rifiuto intelligente.
        """
        try:
            with open("knowledge_scope.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.knowledge_scope = data.get("scope", [])
                
                if self.knowledge_scope:
                    print(f"✅ Ambito di conoscenza caricato: {len(self.knowledge_scope)} argomenti.")
                else:
                    print("⚠️ File knowledge_scope.json vuoto, creando ambito di default.")
                    self._create_default_knowledge_scope()
                    
        except FileNotFoundError:
            print("⚠️ File 'knowledge_scope.json' non trovato. Creando ambito generico...")
            self._create_default_knowledge_scope()
            
        except json.JSONDecodeError as e:
            print(f"❌ Errore nel parsing del file JSON: {e}")
            self._create_default_knowledge_scope()

    def _create_default_knowledge_scope(self):
        """Crea un ambito di conoscenza di default."""
        self.knowledge_scope = [
            "Normative alimentari", "Etichettatura prodotti", "Sicurezza alimentare",
            "Additivi e conservanti", "Controlli sanitari", "Legislazione europea",
            "Regolamenti ministeriali", "Certificazioni qualità"
        ]

    def _build_chain_architecture(self):
        """
        Costruisce l'architettura a grafo con routing intelligente.
        """
        if not self.compression_retriever:
            print("❌ Impossibile costruire l'architettura: retriever non disponibile.")
            return
            
        try:
            conversational_chain = self._build_conversational_chain()
            intelligent_refusal_chain = self._build_refusal_chain()
            rag_chain_with_sources = self._build_rag_chain()
            classification_chain = self._build_classification_chain()

            branch = RunnableBranch(
                (lambda x: x["destination"] == "pertinente", rag_chain_with_sources),
                (lambda x: x["destination"] == "conversazionale", conversational_chain),
                intelligent_refusal_chain
            )

            self.full_chain = (
                {"destination": classification_chain, "query": itemgetter("query")} 
                | branch
            )
            
            print("✅ Architettura a grafo con routing intelligente completata.")
            
        except Exception as e:
            print(f"❌ ERRORE nella costruzione dell'architettura: {e}")
            traceback.print_exc()
            raise

    def _build_conversational_chain(self):
        """
        Costruisce la catena per interazioni conversazionali.
        """
        return (
            itemgetter("query")
            | PromptTemplate.from_template(
                "Sei un assistente AI cordiale di nome Agente AI specializzato in normative alimentari. "
                "Rispondi in modo amichevole e conciso alla seguente interazione: {query}"
            ) 
            | self.llm_main 
            | StrOutputParser()
        )

    def _build_refusal_chain(self):
        """
        Costruisce la catena per il rifiuto intelligente.
        """
        refusal_template = """Sei un assistente AI specializzato in legislazione alimentare.
Non sono in grado di rispondere alla domanda: '{query}'

La mia conoscenza è limitata esclusivamente ai documenti forniti nella mia base dati.
Per ottenere risposte accurate, ti suggerisco di formulare domande sugli argomenti che conosco bene.

I principali argomenti su cui posso aiutarti includono:
{knowledge_scope}

Per favore, riformula la tua domanda focalizzandoti su uno di questi temi specifici."""

        return (
            {
                "query": itemgetter("query"),
                "knowledge_scope": lambda x: self._format_knowledge_scope()
            }
            | PromptTemplate.from_template(refusal_template)
            | self.llm_main
            | StrOutputParser()
        )

    def _build_rag_chain(self):
        """
        Costruisce la catena RAG avanzata con citazioni automatiche.
        """
        def format_docs_with_ids(docs):
            if not docs:
                return "Nessun documento trovato."
            
            formatted_docs = []
            for i, doc in enumerate(docs):
                source_info = doc.metadata.get("source", "Fonte sconosciuta")
                source_name = os.path.basename(source_info) if source_info != "Fonte sconosciuta" else source_info
                
                formatted_docs.append(
                    f"Contenuto dal documento [doc-{i+1}] ({source_name}):\n{doc.page_content.strip()}"
                )
            
            return "\n\n---\n\n".join(formatted_docs)

        rag_template = """Sei "Agente AI", un consulente esperto di legislazione alimentare.

ISTRUZIONI OPERATIVE:
1. Analizza attentamente il contesto fornito dai documenti numerati [doc-1], [doc-2], ecc.
2. Rispondi ESCLUSIVAMENTE basandoti su questi documenti ufficiali.
3. CITAZIONI OBBLIGATORIE: Dopo ogni affermazione specifica, cita immediatamente la fonte usando [doc-N]. Esempio: "Il limite massimo è 5 mg/kg [doc-2]."
4. Per affermazioni supportate da più fonti, cita tutte: "L'etichettatura deve essere chiara [doc-1, doc-3]."
5. NON raggruppare le citazioni alla fine - devono essere integrate nel testo.
6. Se le informazioni non sono sufficienti, dichiara: "Le informazioni disponibili nei documenti non sono sufficienti per rispondere completamente."

CONTESTO DOCUMENTALE:
{context}

DOMANDA:
{question}

RISPOSTA PROFESSIONALE CON CITAZIONI INLINE:"""

        rag_prompt = PromptTemplate.from_template(rag_template)

        # CORREZIONE: Catena pulita senza assegnazioni ridondanti
        return (
            RunnablePassthrough.assign(
                source_documents=itemgetter("query") | self.compression_retriever
            )
            .assign(question=itemgetter("query")) # Aggiunge 'question' per il prompt
            .assign(context=lambda x: format_docs_with_ids(x["source_documents"]))
            .assign(answer=rag_prompt | self.llm_main | StrOutputParser())
            .pick(["answer", "source_documents"])
        )

    def _build_classification_chain(self):
        """
        Costruisce la catena per la classificazione delle query.
        """
        class RouteQuery(BaseModel):
            """Modello Pydantic per la classificazione delle query."""
            destination: Literal["pertinente", "non_pertinente", "conversazionale"]

        # CORREZIONE: Prompt semplificato senza istruzioni contraddittorie
        route_prompt = PromptTemplate(
            input_variables=["query"],
            template="""Classifica la seguente query per un assistente di legislazione alimentare: '{query}'

CRITERI DI CLASSIFICAZIONE:
- "pertinente": domande su normative alimentari, sicurezza, etichettatura, additivi, ecc.
- "conversazionale": saluti, ringraziamenti, domande sull'assistente.
- "non_pertinente": qualsiasi altra cosa (sport, politica, storia, ecc.)."""
        )

        return (
            route_prompt 
            | self.llm_router.with_structured_output(RouteQuery)
            # CORREZIONE: Aggiunta gestione del caso None per massima robustezza
            | (lambda x: x.destination if x else "non_pertinente")
        )

    def _format_knowledge_scope(self) -> str:
        """
        Formatta l'ambito di conoscenza per la visualizzazione.
        """
        if not self.knowledge_scope:
            return "Nessun ambito specifico definito."
        
        scope_items = self.knowledge_scope[:8]
        formatted = "\n".join(f"• {item}" for item in scope_items)
        
        if len(self.knowledge_scope) > 8:
            formatted += f"\n• ... e altri {len(self.knowledge_scope) - 8} argomenti correlati"
            
        return formatted

    def get_response(self, query: str) -> Dict[str, Any]:
        """
        Punto di ingresso principale per ottenere risposte dal sistema RAG.
        """
        if not query or not query.strip():
            return {"answer": "Per favore, inserisci una domanda valida.", "source_documents": []}
            
        if not self.full_chain:
            return {"answer": "Sistema non disponibile. Riprova più tardi.", "source_documents": []}
        
        try:
            print(f"🔍 Elaborazione query: {query[:50]}...")
            result = self.full_chain.invoke({"query": query.strip()})
            return self._normalize_response(result)
                
        except Exception as e:
            print(f"❌ ERRORE nella generazione della risposta: {e}")
            traceback.print_exc()
            return {"answer": "Mi dispiace, si è verificato un errore tecnico. Per favore riprova.", "source_documents": []}

    def _normalize_response(self, result) -> Dict[str, Any]:
        """
        Normalizza la risposta per garantire formato consistente.
        """
        if isinstance(result, dict):
            return {
                "answer": result.get("answer", "Risposta non disponibile."),
                "source_documents": result.get("source_documents", [])
            }
        else:
            return {"answer": str(result), "source_documents": []}

    def get_system_status(self) -> Dict[str, Any]:
        """
        Restituisce lo stato del sistema RAG per diagnostica.
        """
        try:
            doc_count = 0
            if self.compression_retriever:
                try:
                    vector_store = self.compression_retriever.base_retriever.vectorstore
                    doc_count = vector_store._collection.count()
                except:
                    doc_count = -1
            
            is_operational = all([self.llm_main, self.llm_router, self.compression_retriever, self.full_chain])
            
            return {
                "llm_main_available": self.llm_main is not None,
                "llm_router_available": self.llm_router is not None,
                "retriever_available": self.compression_retriever is not None,
                "chain_available": self.full_chain is not None,
                "document_count": doc_count,
                "knowledge_scope_items": len(self.knowledge_scope),
                "status": "operational" if is_operational else "degraded"
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def reload_knowledge_scope(self, new_scope_path: str = "knowledge_scope.json"):
        """
        Ricarica l'ambito di conoscenza da file.
        """
        try:
            with open(new_scope_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.knowledge_scope = data.get("scope", [])
                print(f"✅ Ambito di conoscenza ricaricato: {len(self.knowledge_scope)} argomenti.")
                
        except Exception as e:
            print(f"❌ Errore nel ricaricare l'ambito di conoscenza: {e}")

    def test_connection(self) -> bool:
        """
        Testa la connessione ai servizi esterni.
        """
        try:
            self.llm_main.invoke("Test di connessione.")
            if self.compression_retriever:
                self.compression_retriever.get_relevant_documents("test")
            print("✅ Test di connessione completato con successo.")
            return True
            
        except Exception as e:
            print(f"❌ Test di connessione fallito: {e}")
            return False


# Funzioni di utilità per il backend
def create_default_knowledge_scope_file():
    """Crea un file di knowledge scope di default se non esiste."""
    if not os.path.exists("knowledge_scope.json"):
        default_scope = {
            "scope": [
                "Normative alimentari europee", "Regolamenti ministeriali italiani",
                "Etichettatura prodotti alimentari", "Sicurezza alimentare e HACCP",
                "Additivi e conservanti autorizzati", "Controlli sanitari e ispezioni",
                "Certificazioni di qualità", "Allergeni e intolleranze", "Limiti microbiologici",
                "Tracciabilità alimentare", "Novel food e alimenti innovativi", "Sostanze contaminanti",
                "Materiali a contatto con alimenti", "Etichettatura nutrizionale", "Claim salutistici"
            ]
        }
        try:
            with open("knowledge_scope.json", 'w', encoding='utf-8') as f:
                json.dump(default_scope, f, ensure_ascii=False, indent=2)
            print("✅ File knowledge_scope.json creato con successo.")
        except Exception as e:
            print(f"❌ Errore nella creazione del file knowledge_scope.json: {e}")


def log_error(error_details: str, error_type: str = "BACKEND_ERROR"):
    """
    Registra errori del backend in un log separato.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {error_type}: {error_details}\n"
    
    try:
        with open("backend_errors.log", "a", encoding='utf-8') as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Errore nel logging: {e}")


# Inizializzazione automatica del knowledge scope
if __name__ == "__main__":
    create_default_knowledge_scope_file()
    print("Backend RAG Engine caricato correttamente.")