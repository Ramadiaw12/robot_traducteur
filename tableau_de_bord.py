"""Tableau de bord du Robot traducteur.
Lancer avec :  streamlit run tableau_de_bord.py
"""
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

import config
from donnees import db
from ia.pipeline import traiter
from ia.comprendre import llm_disponible
from ia.traduction import nllb_disponible
from ia.transcription import whisper_disponible
from ia.voix import tts_disponible

st.set_page_config(page_title="Robot traducteur", page_icon="🤖", layout="wide")

st.markdown("""<style>
.block-container {padding-top: 1.6rem;}
h1 {color:#0F2954;}
.carte {background:#F2F5FA; border-radius:14px; padding:18px 22px; margin-bottom:10px;}
.carte .etiquette {color:#5b6475; font-size:0.85rem; text-transform:uppercase; letter-spacing:.04em;}
.carte .grand {font-size:1.6rem; font-weight:700; color:#0F2954;}
.pastille {display:inline-block; padding:2px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; margin-right:6px;}
.ok {background:#E3F4EA; color:#1E7A4C;} .demo {background:#FDF1D6; color:#9A6A00;}
</style>""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def etat_composants():
    return {
        "Whisper (voix → texte)": whisper_disponible(),
        f"LLM {config.LLM_MODELE} (comprendre)": llm_disponible(),
        "NLLB-200 (traduction)": nllb_disponible(),
        "Synthèse vocale MMS-TTS": tts_disponible(),
    }


etat = etat_composants()
st.title("🤖 Robot traducteur · Tableau de bord")
st.caption("Français → anglais / darija · Awa Aimée Benzekry & Ramatoulaye Diawane · HESTIM 5A IIIA")
st.markdown(" ".join(
    f"<span class='pastille {'ok' if v else 'demo'}'>{'●' if v else '○'} {k}{'' if v else ' : mode démo'}</span>"
    for k, v in etat.items()), unsafe_allow_html=True)

onglet_cmd, onglet_hist, onglet_stats = st.tabs(["🎙️ Commander", "📜 Historique", "📊 Statistiques"])

# ---------------------------------------------------------------- COMMANDER
with onglet_cmd:
    gauche, droite = st.columns([1, 1], gap="large")
    with gauche:
        st.subheader("Envoyer une phrase")
        choix = st.radio("Langue", ["Automatique (le LLM décide)", "Anglais", "Darija"], horizontal=True)
        langue_forcee = None if choix.startswith("Auto") else choix.lower()
        mode = st.segmented_control("Entrée", ["✍️ Texte", "🎤 Voix"], default="✍️ Texte")
        resultat = None
        if mode == "🎤 Voix":
            son = st.audio_input("Parlez en français")
            if son is not None and st.button("Traduire l'enregistrement", type="primary"):
                chemin = Path(tempfile.gettempdir()) / "entree_micro.wav"
                chemin.write_bytes(son.getvalue())
                with st.spinner("Écoute, compréhension, traduction..."):
                    resultat = traiter(audio=chemin, canal="voix", langue_forcee=langue_forcee)
        else:
            phrase = st.text_input("Phrase en français", placeholder="Ex. : Comment on dit merci beaucoup en darija ?")
            exemples = ["En anglais : où se trouve la bibliothèque ?", "Comment on dit merci beaucoup en darija ?",
                        "Bonjour, je cherche la salle 12"]
            ex = st.pills("Exemples", exemples)
            texte = ex or phrase
            if st.button("Traduire", type="primary", disabled=not texte):
                with st.spinner("Compréhension, traduction..."):
                    resultat = traiter(texte=texte, canal="texte", langue_forcee=langue_forcee)
        if resultat:
            st.session_state["dernier"] = resultat

    with droite:
        st.subheader("Réponse du robot")
        r = st.session_state.get("dernier")
        if not r:
            st.info("Envoyez une phrase pour voir la traduction ici.")
        else:
            drapeau = "🇬🇧" if r["langue"] == "anglais" else "🇲🇦"
            st.markdown(f"<div class='carte'><div class='etiquette'>Entendu / écrit</div>{r['phrase_brute']}</div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='carte'><div class='etiquette'>Compris par {r['methode_comprehension']}</div>"
                        f"Traduire « {r['phrase_fr']} » en <b>{r['langue']}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='carte'><div class='etiquette'>{drapeau} Traduction ({r['methode_traduction']})</div>"
                        f"<div class='grand'>{r['traduction']}</div></div>", unsafe_allow_html=True)
            if r.get("audio_sortie"):
                st.audio(r["audio_sortie"])
            t = r["temps"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Temps total", f"{r['temps_total_ms']} ms")
            c2.metric("Compréhension", f"{t['comprehension_ms']} ms")
            c3.metric("Traduction", f"{t['traduction_ms']} ms")
            c4.metric("Confiance voix", "–" if r["confiance"] is None else f"{r['confiance']:.0%}")

# ---------------------------------------------------------------- HISTORIQUE
with onglet_hist:
    df = db.tout_lire()
    if df.empty:
        st.info("Aucune traduction pour l'instant.")
    else:
        f1, f2, f3 = st.columns([1, 1, 2])
        langues = f1.multiselect("Langue", sorted(df["langue"].dropna().unique()))
        canaux = f2.multiselect("Canal", sorted(df["canal"].dropna().unique()))
        mot = f3.text_input("Mot-clé")
        vue = df.copy()
        if langues:
            vue = vue[vue["langue"].isin(langues)]
        if canaux:
            vue = vue[vue["canal"].isin(canaux)]
        if mot:
            m = mot.lower()
            vue = vue[vue["phrase_fr"].str.lower().str.contains(m, na=False) | vue["traduction"].str.lower().str.contains(m, na=False)]
        colonnes = ["id", "date", "canal", "phrase_fr", "langue", "traduction", "correction", "temps_ms", "methode_comprehension", "methode_traduction"]
        st.dataframe(vue[colonnes], use_container_width=True, hide_index=True)
        st.download_button("⬇️ Exporter en CSV", vue.to_csv(index=False).encode("utf-8"), "historique_traductions.csv", "text/csv")

        st.markdown("#### ✏️ Corriger une traduction")
        k1, k2 = st.columns([1, 3])
        choix_id = k1.selectbox("N° de l'échange", vue["id"].tolist())
        ligne = df[df["id"] == choix_id].iloc[0]
        k2.caption(f"« {ligne['phrase_fr']} » → {ligne['traduction']}")
        correction = k2.text_input("Bonne traduction", value=ligne["correction"] or "")
        if k2.button("Enregistrer la correction"):
            db.corriger(int(choix_id), correction)
            st.success("Correction enregistrée.")
            st.rerun()

# ---------------------------------------------------------------- STATISTIQUES
with onglet_stats:
    df = db.tout_lire()
    if df.empty:
        st.info("Les statistiques apparaîtront après les premières traductions.")
    else:
        df["date"] = pd.to_datetime(df["date"])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Traductions", len(df))
        m2.metric("Temps moyen", f"{df['temps_ms'].mean():.0f} ms")
        m3.metric("Part en darija", f"{(df['langue'] == 'darija').mean():.0%}")
        m4.metric("Corrigées", f"{df['correction'].fillna('').str.len().gt(0).sum()}")
        g1, g2 = st.columns(2)
        g1.markdown("**Langues demandées**")
        g1.bar_chart(df["langue"].value_counts(), color="#2F6FD6")
        g2.markdown("**Voix ou texte**")
        g2.bar_chart(df["canal"].value_counts(), color="#0F2954")
        g3, g4 = st.columns(2)
        g3.markdown("**Utilisation par heure**")
        g3.bar_chart(df["date"].dt.hour.value_counts().sort_index(), color="#2A9D8F")
        g4.markdown("**Temps de réponse moyen par langue (ms)**")
        g4.bar_chart(df.groupby("langue")["temps_ms"].mean(), color="#D99A00")
        corr = df[df["correction"].fillna("").str.len() > 0]
        if not corr.empty:
            st.markdown("**Phrases corrigées (souvent mal traduites)**")
            st.dataframe(corr[["phrase_fr", "langue", "traduction", "correction"]], use_container_width=True, hide_index=True)
