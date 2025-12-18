# ⚖️ AI Regulatory Consultant (RAG 2.0)

> **Enterprise-grade RAG System** designed for secure consultation of EU Food Regulations. It features a multi-stage architecture with Semantic Routing and Intelligent Refusal to eliminate hallucinations.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-v0.2-green?style=for-the-badge)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)

## 🧠 Project Overview

Unlike standard "chatbots" that blindly answer every query, this system implements a **"Guardrails-First" architecture** specifically engineered for regulated domains (Legal/Compliance).

**Model Agnostic & Privacy Focused:**
This system allows you to **bring your own LLM provider** (OpenRouter, OpenAI, Google AI Studio, etc.), ensuring you maintain full control over data privacy and operational costs. No API keys are embedded in this repository.

### Key Features

* **🛡️ Semantic Routing:** An LLM Router analyzes user intent *before* retrieval. If the query is off-topic (e.g., sports, politics), the system refuses to answer, strictly adhering to the `knowledge_scope`.
* **⚡ Multi-Stage Retrieval:**
    1.  **Vector Search:** Initial retrieval using ChromaDB + Multilingual Embeddings.
    2.  **Reranking:** `Flashrank` reranks the retrieved documents to filter out noise and improve context precision.
* **🔍 Explainable AI (XAI):** Every claim in the response includes interactive `[doc-N]` citations. Clicking a citation reveals the exact source passage from the PDF.
* **💸 Frugal Engineering:** Optimized to run on **Google Gemini Flash 1.5** via OpenRouter for maximum speed and near-zero cost, but fully compatible with any OpenAI-standard endpoint.

---

## 🛠️ Architecture

```mermaid
graph TD
    User[User Query] --> Router{Semantic Router}
    Router -- "Off-topic" --> Refusal[Refusal Chain]
    Router -- "Chit-chat" --> Conversational[Conversational Chain]
    Router -- "Regulatory Query" --> Retriever[Vector Store (Chroma)]
    Retriever --> Reranker[Flashrank Reranker]
    Reranker --> Generator[LLM Generation (RAG)]
    Generator --> Output[Final Response + Citations]
    Refusal --> Output
    Conversational --> Output

```

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone [https://github.com/YOUR-USERNAME/AI-Regulatory-Consultant-RAG.git](https://github.com/YOUR-USERNAME/AI-Regulatory-Consultant-RAG.git)
cd AI-Regulatory-Consultant-RAG

```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

```

### 3. ⚙️ Configure Your API Service (Crucial Step)

⚠️ **IMPORTANT:** For security reasons, this project does not include an `.env` file. You must create one to authenticate with your chosen LLM provider.

**Option A: Using OpenRouter (Recommended)**
This project is pre-configured for OpenRouter (access to Gemini Flash, Claude 3, Llama 3, etc.).

1. Get your API Key from OpenRouter.
2. Create a file named `.env` in the root directory of the project.
3. Add your key inside the file:

```ini
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here...

```

**Option B: Using OpenAI / Google / LocalLLM**
If you prefer a different provider:

1. Open `backend/rag_engine.py`.
2. Locate the `_initialize_llms` method.
3. Modify the `base_url` and `model` parameters to match your provider (e.g., `https://api.openai.com/v1`).

### 4. Ingest Your Data

The system needs to build the vector database from your PDF documents.

1. Place your regulatory PDF files in the `DATASET/` folder.
2. Run the ingestion script:

```bash
python ingest.py

```

*This will create a local `storage/` directory containing the vector embeddings.*

### 5. Run the Application

Launch the desktop interface:

```bash
python app.py

```

---

## 📂 Project Structure

* `backend/rag_engine.py`: Core logic (Routing, Chain construction, Reranking).
* `ui/chat_interface.py`: CustomTkinter GUI with interactive citation management.
* `config/`: Centralized settings and theme management.
* `DATASET/`: Directory for regulatory PDF documents.
* `ingest.py`: Script for document parsing and vectorization.

---

## 🛡️ Disclaimer

This is a portfolio project demonstrating advanced RAG techniques. While accurate, it should not replace professional legal advice.

**Author:** Zampier Zago
*Built with Python, LangChain, and Frugal Engineering principles.*
