# app.py
import os
import logging
import sys
import re
from dotenv import load_dotenv

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.prompts import PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import fitz  # PyMuPDF

load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration optimisée ---

# 1. Embedding model français performant
Settings.embed_model = HuggingFaceEmbedding(
    model_name="dangvantuan/sentence-camembert-base",
    trust_remote_code=True,
    device="cpu",  # ou "cuda" si GPU disponible
)

# 2. LLM Groq (rapide, bon en français)
Settings.llm = Groq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=1024,
    api_key=os.getenv("GROQ_API_KEY"),
)

# 3. Chunking adapté aux documents administratifs
Settings.chunk_size = 1024
Settings.chunk_overlap = 200

PERSIST_DIR = "./storage"
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "ena_archives"

# --- Fonction de nettoyage des textes extraits ---
def clean_text(text: str) -> str:
    """Supprime les caractères non imprimables et normalise les espaces."""
    # Supprimer les caractères de contrôle sauf sauts de ligne et tabulations
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # Remplacer les multiples espaces par un seul
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# --- Gestion de l'index avec PyMuPDF ---
def get_or_create_index():
    db = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = db.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    if not os.path.exists(PERSIST_DIR):
        logger.info("📚 Création de l'index à partir des PDFs dans ./data...")
        if not os.path.exists("data") or not os.listdir("data"):
            logger.error("❌ Dossier 'data' vide ou inexistant.")
            sys.exit(1)

        # Extraction manuelle avec PyMuPDF
        all_documents = []
        for filename in os.listdir("data"):
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join("data", filename)
                logger.info(f"Extraction de {filename}...")
                doc = fitz.open(filepath)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                # Nettoyer le texte extrait
                text = clean_text(text)
                # Créer un document LlamaIndex
                from llama_index.core import Document
                all_documents.append(Document(text=text, metadata={"file_name": filename}))

        if not all_documents:
            logger.error("❌ Aucun document PDF valide trouvé.")
            sys.exit(1)

        logger.info(f"{len(all_documents)} documents chargés et nettoyés.")

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            all_documents, storage_context=storage_context, show_progress=True
        )
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        logger.info("✅ Index créé et sauvegardé.")
    else:
        logger.info("📂 Chargement de l'index existant...")
        storage_context = StorageContext.from_defaults(
            persist_dir=PERSIST_DIR,
            vector_store=vector_store
        )
        index = load_index_from_storage(storage_context=storage_context)
    return index

# --- Prompt optimisé en français ---
CUSTOM_PROMPT_TEMPLATE = """Tu es un assistant expert de l'École Nationale d'Administration (ENA) de Tunisie.
Réponds UNIQUEMENT en te basant sur le contexte documentaire fourni ci-dessous.
Si l'information n'est pas présente dans le contexte, réponds exactement : "Je ne trouve pas cette information dans les archives de l'ENA."
Ne mentionne pas que tu es une IA ou un modèle de langage.

Contexte des archives ENA :
---------------------
{context_str}
---------------------

Question : {query_str}

Réponse en français (précise et cite les sources quand c'est possible) :"""

def create_query_engine(index):
    qa_prompt = PromptTemplate(CUSTOM_PROMPT_TEMPLATE)
    return index.as_query_engine(
        similarity_top_k=3,
        text_qa_template=qa_prompt,
        response_mode="compact",
    )

# --- Fonction pour afficher proprement les sources ---
def display_sources(response):
    print("\n📚 Sources :")
    for i, node in enumerate(response.source_nodes):
        file_name = node.metadata.get('file_name', 'Inconnu')
        page = node.metadata.get('page_label', 'N/A')
        score = node.score if node.score else 0.0
        # Nettoyer l'extrait affiché
        snippet = node.text[:200].replace('\n', ' ') if hasattr(node, 'text') else ''
        snippet = clean_text(snippet)
        print(f"   {i+1}. {file_name} (Page {page}) - Pertinence: {score:.2f}")
        if snippet:
            print(f"      Extrait : {snippet}...")
        print()

# --- CLI ---
def main():
    print("\n" + "=" * 60)
    print("🇹🇳  ENA Assistant de Recherche Documentaire (RAG)")
    print("=" * 60)
    print("Mode CLI | LLM: Groq | Embeddings: CamemBERT (French)")
    print("Extraction PDF: PyMuPDF\n")

    index = get_or_create_index()
    query_engine = create_query_engine(index)

    print("Posez vos questions en français. Tapez 'exit' pour quitter.\n")

    while True:
        query = input("🔍 Question : ")
        if query.lower() in ["exit", "quit", "q"]:
            break

        print("\n⏳ Recherche en cours...")
        response = query_engine.query(query)

        print("\n📄 Réponse :")
        print("-" * 40)
        print(response.response)
        print("-" * 40)

        display_sources(response)

if __name__ == "__main__":
    main()