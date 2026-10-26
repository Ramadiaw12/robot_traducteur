"""Base de données SQLite : l'historique de toutes les traductions."""
import sqlite3
from datetime import datetime
import config

SCHEMA = """CREATE TABLE IF NOT EXISTS echanges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    canal TEXT NOT NULL,              -- 'voix' ou 'texte'
    phrase_brute TEXT,                -- ce qui a été dit ou écrit
    phrase_fr TEXT,                   -- la phrase à traduire (après le LLM)
    langue TEXT,                      -- 'anglais' ou 'darija'
    traduction TEXT,
    confiance REAL,                   -- confiance de Whisper (voix uniquement)
    temps_ms INTEGER,                 -- temps total de réponse
    methode_comprehension TEXT,       -- 'LLM' ou 'règles'
    methode_traduction TEXT,          -- 'NLLB-200' ou 'démo'
    correction TEXT                   -- traduction corrigée par un utilisateur
)"""


def connexion():
    config.BASE_DONNEES.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(config.BASE_DONNEES)
    c.row_factory = sqlite3.Row
    c.execute(SCHEMA)
    return c

# Enregistre un échange dans la base de données et retourne l'id de l'échange.
def enregistrer(res):
    with connexion() as c:
        cur = c.execute(
            """INSERT INTO echanges (date, canal, phrase_brute, phrase_fr, langue, traduction, confiance,
               temps_ms, methode_comprehension, methode_traduction) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (datetime.now().isoformat(timespec="seconds"), res["canal"], res["phrase_brute"], res["phrase_fr"],
             res["langue"], res["traduction"], res.get("confiance"), res.get("temps_total_ms"),
             res.get("methode_comprehension"), res.get("methode_traduction")))
        return cur.lastrowid


def tout_lire():
    import pandas as pd
    with connexion() as c:
        return pd.read_sql_query("SELECT * FROM echanges ORDER BY id DESC", c)


def corriger(id_echange, correction):
    with connexion() as c:
        c.execute("UPDATE echanges SET correction=? WHERE id=?", (correction, id_echange))
