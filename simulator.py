# simulator.py
import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding

load_dotenv()

Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434")
Settings.llm = Groq(model="llama-3.3-70b-versatile", temperature=0.3, api_key=os.getenv("GROQ_API_KEY"))

from app import get_or_create_index

class DecisionSimulator:
    def __init__(self):
        self.index = get_or_create_index()
        self.retriever = self.index.as_retriever(similarity_top_k=3)
        self.llm = Settings.llm

    def generate_scenario(self, theme="crise"):
        prompt = f"""Tu es un formateur de l'ENA. Crée un scénario de prise de décision réaliste pour un haut fonctionnaire tunisien.
Thème suggéré : {theme}.
Le scénario doit inclure :
1. Le poste occupé (ex: Gouverneur, Directeur Général)
2. La situation d'urgence ou le problème complexe
3. Des données concrètes (chiffres, lieux, acteurs)
4. Trois options possibles pour le décideur

Format : Un paragraphe descriptif suivi de la question "Quelle est votre décision ?"

Scénario :"""
        response = self.llm.complete(prompt)
        return response.text

    def evaluate_decision(self, scenario, user_decision):
        retrieval_query = f"Textes juridiques et procédures concernant : {scenario[:200]}"
        nodes = self.retriever.retrieve(retrieval_query)
        context = "\n\n".join([node.text for node in nodes])

        prompt = f"""Tu es un évaluateur expert de l'ENA. Évalue la décision suivante.

Scénario :
{scenario}

Contexte juridique de référence :
{context[:2000]}

Décision proposée :
"{user_decision}"

Analyse la décision (conformité juridique, bonnes pratiques, faisabilité, risques).
Donne une note sur 10 et un feedback détaillé en français.
Structure :
**Note : X/10**
**Points forts :** ...
**Points faibles :** ...
**Conseil :** ..."""
        response = self.llm.complete(prompt)
        return response.text

def run_simulator():
    sim = DecisionSimulator()
    print("\n🎮 Simulateur de Décision ENA")
    print("=" * 50)
    print("1. Générer un scénario")
    print("2. Évaluer une décision")
    print("3. Quitter")

    current_scenario = None

    while True:
        choice = input("\nChoix : ").strip()
        if choice == "1":
            theme = input("Thème (crise, gestion, réforme, etc.) [défaut: crise] : ").strip() or "crise"
            print("\n⏳ Génération du scénario...")
            current_scenario = sim.generate_scenario(theme)
            print("\n📋 Scénario :\n")
            print(current_scenario)
        elif choice == "2":
            if not current_scenario:
                print("⚠️  Générez d'abord un scénario (option 1).")
                continue
            decision = input("\n✍️  Votre décision : ").strip()
            if not decision:
                continue
            print("\n⏳ Évaluation en cours...")
            evaluation = sim.evaluate_decision(current_scenario, decision)
            print("\n📊 Évaluation :\n")
            print(evaluation)
        elif choice == "3":
            break
        else:
            print("Option invalide.")

if __name__ == "__main__":
    run_simulator()