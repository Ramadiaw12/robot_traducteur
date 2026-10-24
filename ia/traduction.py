"""Étape traduction : NLLB-200 (français -> anglais ou darija)."""
import config

_modele = None
_tokenizer = None

DEMO = {
    "anglais": {
        "bonjour": "Hello", "merci": "Thank you", "merci beaucoup": "Thank you very much",
        "où se trouve la bibliothèque": "Where is the library?", "où est la bibliothèque": "Where is the library?",
        "je cherche la salle 12": "I am looking for room 12", "comment ça va": "How are you?",
    },
    "darija": {
        "bonjour": "السلام", "merci": "شكرا", "merci beaucoup": "شكرا بزاف",
        "où se trouve la bibliothèque": "فين كاينة المكتبة؟", "où est la bibliothèque": "فين كاينة المكتبة؟",
        "comment ça va": "لاباس عليك؟",
    },
}


def nllb_disponible():
    if config.MODE is True:
        return False
    try:
        import transformers, torch  # noqa: F401
        return True
    except Exception:
        return False


def _charger():
    global _modele, _tokenizer
    if _modele is None:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        _tokenizer = AutoTokenizer.from_pretrained(config.NLLB_MODELE, src_lang=config.CODES_NLLB["francais"])
        _modele = AutoModelForSeq2SeqLM.from_pretrained(config.NLLB_MODELE)
    return _modele, _tokenizer


def traduire_demo(texte, langue):
    cle = texte.lower().strip(" ?!.")
    return DEMO.get(langue, {}).get(cle, f"[démo {langue}] {texte}")


def traduire(texte, langue):
    """Renvoie {'traduction', 'methode'}."""
    if not nllb_disponible():
        return {"traduction": traduire_demo(texte, langue), "methode": "démo"}
    modele, tok = _charger()
    entrees = tok(texte, return_tensors="pt")
    cible = tok.convert_tokens_to_ids(config.CODES_NLLB[langue])
    sortie = modele.generate(**entrees, forced_bos_token_id=cible, max_length=200)
    return {"traduction": tok.batch_decode(sortie, skip_special_tokens=True)[0], "methode": "NLLB-200"}
