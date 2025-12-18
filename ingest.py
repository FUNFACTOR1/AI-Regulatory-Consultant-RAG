import os
import shutil
import json
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
# MODIFICA: Importa il SemanticChunker
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Definisci le cartelle di origine e di destinazione
DATA_PATH = "DATASET"
DB_PATH = "storage"
KNOWLEDGE_SCOPE_FILE = "knowledge_scope.json"

def create_vector_db():
    print("--- Inizio Script di Indicizzazione con Chunking Semantico e Embedding Legale ---")

    # --- FASE 1: CONTROLLO E PULIZIA ---
    if not os.path.exists(DATA_PATH):
        print(f"--- ERRORE CRITICO ---\nLa cartella sorgente '{DATA_PATH}' non è stata trovata.\n...")
        return
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print(f"Vecchia cartella '{DB_PATH}' eliminata per rigenerazione.")
    
    # --- FASE 2: CARICAMENTO DOCUMENTI ---
    print(f"Caricamento dei documenti PDF dalla cartella '{DATA_PATH}'...")
    loader = DirectoryLoader(DATA_PATH, glob='*.pdf', loader_cls=PyPDFLoader)
    documents = loader.load()
    if not documents:
        print(f"--- ERRORE ---\nNessun file PDF è stato trovato...\n...")
        return
    print(f"Caricati con successo {len(documents)} documenti.")

    # --- FASE 2.5: ESTRAZIONE AMBITO DI CONOSCENZA CON LLM ---
    print("Estrazione degli argomenti chiave dai documenti tramite LLM...")
    try:
        analyzer_llm = ChatOpenAI(
            model="google/gemini-flash-1.5",
            temperature=0,
            api_key="......................................................",
            base_url="........................................."
        )
        full_text_sample = " ".join([doc.page_content for doc in documents[:5]])[:8000]
        parser = JsonOutputParser()
        prompt = PromptTemplate(
            template="""Analizza il seguente testo estratto da documenti sulla legislazione alimentare. Estrai i 5-7 argomenti o temi principali trattati. Rispondi SOLO con un oggetto JSON che abbia una singola chiave "scope" contenente una lista di stringhe. TESTO DA ANALIZZARE: {text_sample} FORMATO JSON RICHIESTO: {format_instructions}""",
            input_variables=["text_sample"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | analyzer_llm | parser
        knowledge_scope = chain.invoke({"text_sample": full_text_sample})
        with open(KNOWLEDGE_SCOPE_FILE, 'w', encoding='utf-8') as f:
            json.dump(knowledge_scope, f, ensure_ascii=False, indent=4)
        print(f"✅ Ambito di conoscenza salvato con successo. Argomenti: {knowledge_scope.get('scope')}")
    except Exception as e:
        print(f"❌ ERRORE durante l'estrazione dell'ambito di conoscenza: {e}")

    # --- FASE 3: SUDDIVISIONE DEL TESTO (CHUNKING) ---
    print("\n--- INIZIO FASE 3: CHUNKING E EMBEDDING ---")
    
    # MODIFICA 1: Sostituisci il vecchio modello di embedding con quello di dominio-specifico
    print("Inizializzazione del modello di embedding legale 'nlpaueb/legal-bert-base-uncased'...")
    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    print("Modello di embedding legale caricato.")

    # MODIFICA 2: Sostituisci il vecchio splitter con il SemanticChunker
    print("Divisione dei documenti in chunks con approccio semantico...")
    text_splitter = SemanticChunker(
        embeddings,
        # CORREZIONE: Usa "percentile", l'opzione di default che è più stabile.
        breakpoint_threshold_type="percentile"
    )
    
    # Il SemanticChunker lavora meglio su un unico blocco di testo per documento
    # per mantenere la coerenza. Processiamo un documento alla volta.
    all_chunks = []
    for doc in documents:
        # Crea chunk semantici per ogni documento
        chunks = text_splitter.create_documents([doc.page_content])
        # Aggiunge i metadati del documento originale ad ogni suo chunk
        for chunk in chunks:
            chunk.metadata = doc.metadata
        all_chunks.extend(chunks)
        
    print(f"Documenti divisi in {len(all_chunks)} chunks semantici.")

    # --- FASE 4: CREAZIONE DATABASE VETTORIALE ---
    print(f"Creazione e salvataggio del nuovo database vettoriale in '{DB_PATH}'...")
    db = Chroma.from_documents(all_chunks, embeddings, persist_directory=DB_PATH)
    db.persist()

    print("\n--------------------------------------------------")
    print(f"✅ SUCCESSO! Database rigenerato con chunking semantico e embedding legali.")
    print("✅ Ora puoi avviare l'applicazione principale con 'python app.py'.")
    print("--------------------------------------------------")

if __name__ == "__main__":
    create_vector_db()