"""Étape reconnaissance vocale : Whisper (voix -> texte)."""
import config

_modele = None

# Fonction pour vérifier si la reconnaissance vocale est disponible (modèles installés et non en mode démo)
def whisper_disponible():
    if config.MODE is True:
        return False
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:
        return False

# Fonction pour transcrire un fichier audio en texte, avec confiance approximative
def transcrire(chemin_audio):
    """Renvoie {'texte', 'confiance', 'methode'} à partir d'un fichier audio (wav, mp3...)."""
    global _modele
    if not whisper_disponible():
        return {"texte": "Où se trouve la bibliothèque ?", "confiance": None, "methode": "démo"}
    if _modele is None:
        from faster_whisper import WhisperModel
        _modele = WhisperModel(config.WHISPER_MODELE, device="auto", compute_type="int8")
    segments, info = _modele.transcribe(str(chemin_audio), language="fr")
    segments = list(segments)
    texte = " ".join(s.text.strip() for s in segments).strip()
    # confiance approximative : moyenne des probabilités des segments (0 à 1)
    import math
    conf = round(sum(math.exp(s.avg_logprob) for s in segments) / len(segments), 2) if segments else None
    return {"texte": texte, "confiance": conf, "methode": f"Whisper {config.WHISPER_MODELE}"}
