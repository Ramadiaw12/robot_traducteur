"""Étape synthèse vocale : texte -> fichier audio WAV (modèles MMS-TTS)."""
import config

_cache = {}

# Fonction pour vérifier si la synthèse vocale est disponible (modèles installés et non en mode démo)
def tts_disponible():
    if config.MODE is True:
        return False
    try:
        import transformers, torch, scipy  # noqa: F401
        return True
    except Exception:
        return False

# Fonction pour générer un fichier audio à partir d'un texte et d'une langue donnée
def parler(texte, langue, fichier_sortie):
    """Crée un fichier WAV. Renvoie le chemin, ou None si la voix n'est pas disponible."""
    if not tts_disponible():
        return None
    try:
        import torch
        import scipy.io.wavfile
        from transformers import VitsModel, AutoTokenizer
        nom = config.TTS_MODELES[langue] # nom du modèle MMS-TTS pour la langue qui correspond par défaut à la demande (anglais ou darija)
        if nom not in _cache:
            _cache[nom] = (VitsModel.from_pretrained(nom), AutoTokenizer.from_pretrained(nom))
        modele, tok = _cache[nom]
        if getattr(tok, "is_uroman", False):  # certaines langues demandent une écriture en lettres latines
            import uroman
            texte = uroman.Uroman().romanize_string(texte) # exemple : "السلام" -> "alslam"
        entrees = tok(texte, return_tensors="pt")
        with torch.no_grad():
            onde = modele(**entrees).waveform[0].numpy()
        scipy.io.wavfile.write(str(fichier_sortie), rate=modele.config.sampling_rate, data=onde)
        return str(fichier_sortie)
    except Exception as e:
        print("Synthèse vocale impossible :", e)
        return None
