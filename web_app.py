# web_app.py
import streamlit as st
from dotenv import load_dotenv
import os
import time

# Configuration de la page DOIT être la première commande Streamlit
st.set_page_config(
    page_title="ENA Doc Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styles CSS personnalisés
st.markdown("""
<style>
    /* Polices et couleurs ENA (inspiration bleu marine et or) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1a2a4f;
        margin-bottom: 0.5rem;
        border-bottom: 3px solid #c9a84c;
        padding-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #4a5a7a;
        font-size: 1rem;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .source-box {
        background-color: #f8f9fc;
        border-left: 4px solid #c9a84c;
        padding: 12px 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 0.9rem;
    }
    
    .chat-message-user {
        background-color: #eef2f7;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        color: #1a2a4f;
        border: 1px solid #d0dae8;
    }
    
    .chat-message-assistant {
        background-color: #ffffff;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        color: #1a2a4f;
        border: 1px solid #e0e6f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .sidebar-info {
        background: linear-gradient(145deg, #f0f4fa 0%, #ffffff 100%);
        padding: 20px 15px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .stButton button {
        background-color: #1a2a4f;
        color: white;
        border-radius: 30px;
        padding: 8px 20px;
        font-weight: 500;
        border: none;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        background-color: #c9a84c;
        color: #1a2a4f;
        border: none;
    }
    
    /* Style pour les expanders */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1a2a4f;
    }
    
    /* Badge pour le nombre de documents */
    .doc-badge {
        background-color: #c9a84c;
        color: #1a2a4f;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()

# Import des fonctions depuis app.py
from app import get_or_create_index, create_query_engine, clean_text

# --- Barre latérale ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/1a2a4f/university.png", width=80)
    st.markdown("## 🏛️ ENA Assistant")
    st.markdown("---")
    
    # Section informations
    with st.container():
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.markdown("### 📋 À propos")
        st.markdown("""
        Assistant documentaire intelligent pour l'École Nationale d'Administration.
        Il répond à vos questions en s'appuyant exclusivement sur les archives 
        (cours, mémoires, textes juridiques).
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Statistiques
    with st.container():
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.markdown("### 📊 Corpus documentaire")
        try:
            # Tenter de récupérer le nombre de documents indexés
            import chromadb
            db = chromadb.PersistentClient(path="./chroma_db")
            collection = db.get_or_create_collection("ena_archives")
            doc_count = collection.count()
        except:
            doc_count = "?"
        st.markdown(f'<span class="doc-badge">{doc_count} chunks indexés</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton de réinitialisation (optionnel)
    if st.button("🔄 Nouvelle conversation"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2025 - Projet ENA • IA Souveraine")

# --- En-tête principal ---
st.markdown('<h1 class="main-header">🏛️ Assistant Documentaire de l\'ENA</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Recherche intelligente dans les archives – propulsé par RAG (Retrieval-Augmented Generation)</p>', unsafe_allow_html=True)

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chargement de l'index (avec cache et spinner)
@st.cache_resource(show_spinner=False)
def load_index():
    with st.spinner("Chargement de l'index documentaire... Veuillez patienter."):
        return get_or_create_index()

try:
    index = load_index()
    query_engine = create_query_engine(index)
except Exception as e:
    st.error(f"Erreur lors du chargement de l'index : {e}")
    st.stop()

# --- Zone d'affichage du chat ---
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message-user">🧑‍💼 <b>Vous</b><br>{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-assistant">🏛️ <b>Assistant ENA</b><br>{message["content"]}</div>', unsafe_allow_html=True)
            # Afficher les sources si disponibles dans le message
            if "sources" in message and message["sources"]:
                with st.expander("📚 Sources consultées"):
                    for i, src in enumerate(message["sources"]):
                        st.markdown(f"""
                        <div class="source-box">
                            <b>{i+1}. {src['file']}</b> (Page {src['page']}) – Pertinence: {src['score']:.2f}<br>
                            <span style="color: #555;">{src['snippet']}</span>
                        </div>
                        """, unsafe_allow_html=True)

# --- Zone de saisie ---
if prompt := st.chat_input("Posez votre question ici..."):
    # Ajout message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with chat_container:
        st.markdown(f'<div class="chat-message-user">🧑‍💼 <b>Vous</b><br>{prompt}</div>', unsafe_allow_html=True)
    
    # Génération de la réponse
    with st.spinner("Consultation des archives..."):
        try:
            response = query_engine.query(prompt)
            answer = response.response
            # Préparer les sources
            sources = []
            for node in response.source_nodes:
                file_name = node.metadata.get('file_name', 'Inconnu')
                page = node.metadata.get('page_label', 'N/A')
                score = node.score if node.score else 0.0
                snippet = node.text[:300].replace('\n', ' ') if hasattr(node, 'text') else ''
                snippet = clean_text(snippet)
                sources.append({
                    "file": file_name,
                    "page": page,
                    "score": score,
                    "snippet": snippet
                })
            
            # Ajout message assistant avec sources
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })
            
            with chat_container:
                st.markdown(f'<div class="chat-message-assistant">🏛️ <b>Assistant ENA</b><br>{answer}</div>', unsafe_allow_html=True)
                if sources:
                    with st.expander("📚 Sources consultées"):
                        for i, src in enumerate(sources):
                            st.markdown(f"""
                            <div class="source-box">
                                <b>{i+1}. {src['file']}</b> (Page {src['page']}) – Pertinence: {src['score']:.2f}<br>
                                <span style="color: #555;">{src['snippet']}</span>
                            </div>
                            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")