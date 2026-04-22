# 🏛️ Assistant Documentaire ENA – RAG Souverain

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39%2B-FF4B4B)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Système de **recherche documentaire augmentée par IA** développé pour l'École Nationale d'Administration (ENA) de Tunisie.  
Il permet d'interroger en langage naturel une base de documents PDF (cours, mémoires, textes juridiques) et d'obtenir des réponses **précises, sourcées et vérifiables**.

---

## ✨ Fonctionnalités

- 🔍 **Recherche sémantique** dans des archives PDF en français  
- 💬 **Interface conversationnelle** élégante (Streamlit)  
- 📚 **Réponses sourcées** : extraits des documents avec numéros de page  
- 🔒 **Souveraineté des données** : indexation et embeddings **100% locaux** (CamemBERT)  
- ⚡ **LLM rapide** via API Groq (Llama 3.3 70B) – possibilité de passer en local (Mistral/Ollama)  
- 🎮 **Simulateur de décision** pour scénarios de crise (module séparé)  
- 🧹 Extraction PDF robuste avec **PyMuPDF**  

---

## 🛠️ Technologies

| Composant               | Technologie                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| Langage                 | Python 3.10+                                                                |
| Framework RAG           | [LlamaIndex](https://www.llamaindex.ai/)                                    |
| Embeddings (Français)   | `dangvantuan/sentence-camembert-base` (HuggingFace)                         |
| LLM                     | Groq API (`llama-3.3-70b-versatile`)                                        |
| Base vectorielle        | ChromaDB                                                                    |
| Interface Web           | Streamlit                                                                   |
| Extraction PDF          | PyMuPDF                                                                     |

---

## 📁 Structure du projet
ena-rag-assistant/
├── data/ # 📄 Placez vos PDFs ici (non versionnés)
├── storage/ # ⚙️ Index vectoriel (généré automatiquement)
├── chroma_db/ # 🗄️ Base ChromaDB (générée automatiquement)
├── app.py # 🖥️ Interface CLI
├── web_app.py # 🌐 Interface Web Streamlit
├── simulator.py # 🎲 Simulateur de décision
├── requirements.txt # 📦 Dépendances Python
├── .env # 🔐 Clé API Groq (à créer, non versionné)
├── .gitignore # 🙈 Fichiers exclus du versionnement
└── README.md # 📖 Ce fichier


---

## 🚀 Installation et exécution (étape par étape)

### 1️⃣ Prérequis

- **Python 3.10 ou supérieur** ([télécharger](https://www.python.org/downloads/))
- **Clé API Groq** (gratuite) – [Obtenir sur console.groq.com](https://console.groq.com)
- **Git** (optionnel, pour cloner le dépôt)

### 2️⃣ Cloner le dépôt

git clone https://github.com/Abderrazekk/ENA-RAG-Assistant.git
cd ena-rag-assistant

3️⃣ Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

4️⃣ Installer les dépendances
pip install -r requirements.txt

5️⃣ Configurer la clé API Groq
Créez un fichier nommé .env à la racine du projet et ajoutez-y :
GROQ_API_KEY=votre_cle_groq_ici

6️⃣ Ajouter vos documents PDF
Placez vos fichiers PDF (cours, mémoires, textes juridiques, etc.) dans le dossier data/.
Exemples : ce_2021_droit_public.pdf, cours_administratif.pdf, …

📌 Le dossier data/ est vide par défaut. Vous devez y mettre au moins un PDF pour que l'indexation fonctionne.

7️⃣ Lancer l'interface Web (Streamlit)
streamlit run web_app.py


🖥️ Utilisation
Interface Web (recommandée)
streamlit run web_app.py


Interface CLI (terminal)
python app.py
