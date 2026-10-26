"""La chaîne complète : (voix ou texte) -> comprendre -> traduire -> parler -> enregistrer."""
import time
import tempfile
from pathlib import Path

from ia.comprendre import comprendre
from ia.traduction import traduire
from ia.transcription import transcrire
from ia.voix import parler
from donnees import db

# Point d'entrée unique, utilisé par le tableau de bord ET par le nœud ROS 2
def traiter(texte=None, audio=None, canal="texte", langue_forcee=None, avec_voix=True):
    """Point d'entrée unique, utilisé par le tableau de bord ET par le nœud ROS 2.
    texte : phrase écrite, ou audio : chemin d'un fichier audio. Renvoie un dictionnaire avec tout le détail."""
    t0 = time.perf_counter()
    res = {"canal": canal, "confiance": None}

    if audio is not None:
        tr = transcrire(audio)
        res.update(phrase_brute=tr["texte"], confiance=tr["confiance"], methode_transcription=tr["methode"])
    else:
        res.update(phrase_brute=texte.strip(), methode_transcription="aucune (texte)")
    t1 = time.perf_counter()

    comp = comprendre(res["phrase_brute"], langue_forcee)
    res.update(phrase_fr=comp["texte"], langue=comp["langue"], methode_comprehension=comp["methode"])
    t2 = time.perf_counter()

    trad = traduire(res["phrase_fr"], res["langue"])
    res.update(traduction=trad["traduction"], methode_traduction=trad["methode"])
    t3 = time.perf_counter()

    res["audio_sortie"] = None
    if avec_voix:
        sortie = Path(tempfile.gettempdir()) / f"traduction_{int(time.time()*1000)}.wav"
        res["audio_sortie"] = parler(res["traduction"], res["langue"], sortie)
    t4 = time.perf_counter()

    res["temps"] = {
        "transcription_ms": round((t1 - t0) * 1000), "comprehension_ms": round((t2 - t1) * 1000),
        "traduction_ms": round((t3 - t2) * 1000), "voix_ms": round((t4 - t3) * 1000),
    }
    res["temps_total_ms"] = round((t4 - t0) * 1000)
    res["id"] = db.enregistrer(res)
    return res
