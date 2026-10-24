"""Réglages du projet Robot traducteur. On change les modèles ici, nulle part ailleurs."""
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent

# Base de données (fichier SQLite créé automatiquement)
BASE_DONNEES = DOSSIER / "donnees" / "historique.db"

# Modèles d'IA
WHISPER_MODELE = "small"                          # tiny, base, small, medium (plus gros = plus précis mais plus lent)
NLLB_MODELE = "facebook/nllb-200-distilled-600M"  # modèle de traduction
LLM_MODELE = "qwen2.5:1.5b"                        # modèle Ollama qui comprend la demande
TTS_MODELES = {"anglais": "facebook/mms-tts-eng", "darija": "facebook/mms-tts-ara"}

# Codes de langue NLLB
CODES_NLLB = {"francais": "fra_Latn", "anglais": "eng_Latn", "darija": "ary_Arab"}
LANGUE_PAR_DEFAUT = "anglais"

# Mode démo : True = pas de modèles, réponses simulées (utile si l'installation n'est pas finie)
# "auto" = essaie les vrais modèles et passe en démo seulement pour ceux qui manquent
MODE = "auto"
