"""Test rapide de la chaîne IA, sans tableau de bord ni robot.
Utilisation :
    python tester_pipeline.py                         -> teste 3 phrases écrites
    python tester_pipeline.py --audio ma_phrase.wav   -> teste avec un enregistrement
    python tester_pipeline.py --fichier donnees/phrases_test.csv -> traduit tout le jeu de test
"""
import argparse
import csv
from ia.pipeline import traiter

p = argparse.ArgumentParser()
p.add_argument("--audio")
p.add_argument("--fichier")
a = p.parse_args()


def afficher(r):
    print(f"\n[{r['methode_comprehension']} / {r['methode_traduction']}] {r['phrase_brute']}")
    print(f"  -> à traduire : « {r['phrase_fr']} » en {r['langue']}")
    print(f"  -> traduction : {r['traduction']}")
    print(f"  -> temps : {r['temps_total_ms']} ms {r['temps']}  | audio : {r['audio_sortie']}")


if a.audio:
    afficher(traiter(audio=a.audio, canal="voix"))
elif a.fichier:
    with open(a.fichier, encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            for langue in ("anglais", "darija"):
                afficher(traiter(texte=ligne["phrase_fr"], langue_forcee=langue, avec_voix=False))
else:
    for phrase in ["En anglais : où se trouve la bibliothèque ?",
                   "Comment on dit merci beaucoup en darija ?",
                   "Bonjour, je cherche la salle 12"]:
        afficher(traiter(texte=phrase))
