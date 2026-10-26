"""Étape LLM : comprendre la demande (quel texte traduire, vers quelle langue)."""
import json
import re
import config

CONSIGNE = """Tu es l'assistant d'un robot traducteur. Tu reçois une demande en français.
Trouve la phrase à traduire et la langue demandée.
Réponds UNIQUEMENT en JSON avec deux champs :
- "texte" : la phrase à traduire, sans les mots de la consigne (« traduis », « en darija », « comment on dit »...)
- "langue" : "anglais" ou "darija" (si rien n'est précisé, mets "{defaut}")

Exemples :
Demande : « Comment on dit merci beaucoup en darija ? » -> {{"texte": "merci beaucoup", "langue": "darija"}}
Demande : « En anglais : où se trouve la bibliothèque ? » -> {{"texte": "où se trouve la bibliothèque ?", "langue": "anglais"}}
Demande : « Bonjour, je cherche la salle 12 » -> {{"texte": "Bonjour, je cherche la salle 12", "langue": "{defaut}"}}

Demande : « {phrase} »"""

# Renvoie {'texte', 'langue', 'methode'}. Si langue_forcee est donnée (choix sur la plateforme), on la garde
def llm_disponible():
    if config.MODE is True:
        return False
    try:
        import ollama
        noms = [m.get("model") or m.get("name") for m in ollama.list().get("models", [])]
        return any(n and n.startswith(config.LLM_MODELE.split(":")[0]) for n in noms)
    except Exception:
        return False

# Solution de secours sans LLM : on cherche les mots-clés
def comprendre_par_regles(phrase):
    """Solution de secours sans LLM : on cherche les mots-clés."""
    p = phrase.strip()
    bas = p.lower()
    langue = "darija" if "darija" in bas else "anglais" if "anglais" in bas else config.LANGUE_PAR_DEFAUT
    texte = re.sub(r"(?i)\b(en|vers l'|vers le)\s*(anglais|darija)\b\s*[:,]?", "", p)
    texte = re.sub(r"(?i)^(traduis(-moi)?( ça| cela)?|comment (on dit|dit-on))\s*[:,]?\s*", "", texte)
    texte = texte.strip(" :,«»\"'?") or p
    return {"texte": texte, "langue": langue, "methode": "règles"}

# Renvoie {'texte', 'langue', 'methode'}. Si langue_forcee est donnée (choix sur la plateforme), on la garde
def comprendre(phrase, langue_forcee=None):
    """Renvoie {'texte', 'langue', 'methode'}. Si langue_forcee est donnée (choix sur la plateforme), on la garde."""
    if llm_disponible():
        try:
            import ollama
            rep = ollama.chat(
                model=config.LLM_MODELE,
                messages=[{"role": "user", "content": CONSIGNE.format(phrase=phrase, defaut=config.LANGUE_PAR_DEFAUT)}],
                format="json",
                options={"temperature": 0},
            )
            res = json.loads(rep["message"]["content"])
            langue = str(res.get("langue", config.LANGUE_PAR_DEFAUT)).lower()
            if langue not in ("anglais", "darija"):
                langue = config.LANGUE_PAR_DEFAUT
            resultat = {"texte": res.get("texte") or phrase, "langue": langue, "methode": "LLM"}
        except Exception:
            resultat = comprendre_par_regles(phrase)
    else:
        resultat = comprendre_par_regles(phrase)
    if langue_forcee:
        resultat["langue"] = langue_forcee
    return resultat
