"""Tableau de bord du Robot traducteur.
Lancer avec :  streamlit run tableau_de_bord.py
"""
import html
import tempfile
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import config
from donnees import db
from ia.pipeline import traiter
from ia.comprendre import llm_disponible
from ia.traduction import nllb_disponible
from ia.transcription import whisper_disponible
from ia.voix import tts_disponible

st.set_page_config(page_title="Robot traducteur", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

NAVY, BLEU, CIEL, VERT, OR, ROSE = "#0F2954", "#2F6FD6", "#7FB2FF", "#2A9D8F", "#F2B33D", "#FF6B8B"

# ------------------------------------------------------------------ STYLE
CSS = f"""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stMarkdown, .stTextInput, button, input {{ font-family: 'Poppins', sans-serif !important; }}
.stApp {{ background: radial-gradient(circle at 10% 0%, #EAF1FF 0, #F7F9FD 35%, #FFFFFF 100%); }}
.block-container {{ padding-top: 1.2rem; max-width: 1300px; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* ---------- Bandeau ---------- */
.hero {{ position:relative; overflow:hidden; border-radius:26px; padding:30px 38px; color:#fff;
  background: linear-gradient(120deg, {NAVY} 0%, #1D4E9E 55%, {BLEU} 100%);
  box-shadow: 0 18px 40px rgba(15,41,84,.25); display:flex; align-items:center; justify-content:space-between; }}
.hero:before {{ content:""; position:absolute; width:420px; height:420px; border-radius:50%; right:-120px; top:-200px;
  background: radial-gradient(circle, rgba(127,178,255,.45), transparent 70%); }}
.hero h1 {{ color:#fff !important; font-size:2.6rem; font-weight:800; margin:0; line-height:1.05; letter-spacing:-1px; }}
.hero .sous {{ font-size:1.05rem; opacity:.9; margin:8px 0 16px; }}
.hero .lang {{ display:inline-block; background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.25);
  padding:4px 14px; border-radius:20px; margin-right:8px; font-weight:600; font-size:.9rem; }}
.robot {{ width:150px; flex:0 0 150px; animation: flotte 3s ease-in-out infinite; z-index:1; }}
@keyframes flotte {{ 0%,100% {{ transform: translateY(0) }} 50% {{ transform: translateY(-10px) }} }}
.oeil {{ animation: cligne 4s infinite; transform-origin: center; transform-box: fill-box; }}
@keyframes cligne {{ 0%,92%,100% {{ transform: scaleY(1) }} 95% {{ transform: scaleY(.1) }} }}
.antenne {{ animation: brille 1.6s ease-in-out infinite; }}
@keyframes brille {{ 0%,100% {{ fill:{OR}; }} 50% {{ fill:#fff3c4; }} }}

/* ---------- Pastilles d'état ---------- */
.etats {{ display:flex; gap:10px; flex-wrap:wrap; margin:18px 0 6px; }}
.etat {{ background:#fff; border-radius:14px; padding:9px 14px; box-shadow:0 4px 14px rgba(15,41,84,.08);
  font-size:.86rem; font-weight:600; color:{NAVY}; display:flex; align-items:center; gap:8px; }}
.point {{ width:10px; height:10px; border-radius:50%; }}
.vert {{ background:#22C55E; box-shadow:0 0 0 4px rgba(34,197,94,.18); }}
.jaune {{ background:{OR}; box-shadow:0 0 0 4px rgba(242,179,61,.22); }}
.etat small {{ color:#8892a6; font-weight:500; }}

/* ---------- Onglets ---------- */
.stTabs [data-baseweb="tab"] {{ font-weight:600; font-size:1rem; padding:6px 14px; }}
.stTabs [aria-selected="true"] {{ color:{BLEU} !important; }}
/* ---------- Cartes ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {{ background:#fff; border-radius:22px !important; border:1px solid #E8EEF8 !important;
  box-shadow:0 10px 30px rgba(15,41,84,.07); }}
.titre-carte {{ font-size:1.25rem; font-weight:700; color:{NAVY}; margin-bottom:2px; }}
.aide {{ color:#7a8396; font-size:.88rem; margin-bottom:10px; }}

/* ---------- Bouton principal ---------- */
.stButton > button[kind="primary"] {{ background:linear-gradient(120deg,{BLEU},#5B8DEF); border:none; border-radius:14px;
  padding:.6rem 1.6rem; font-weight:700; box-shadow:0 8px 20px rgba(47,111,214,.35); transition: transform .15s; }}
.stButton > button[kind="primary"]:hover {{ transform: translateY(-2px); }}

/* ---------- Conversation ---------- */
.ligne {{ display:flex; gap:10px; margin:12px 0; align-items:flex-end; }}
.ligne.moi {{ justify-content:flex-end; }}
.avatar {{ width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.2rem; flex:0 0 38px; }}
.av-moi {{ background:#FFE3EA; }} .av-robot {{ background:#E3EDFF; }}
.bulle {{ max-width:78%; padding:12px 16px; border-radius:20px; font-size:.98rem; line-height:1.4; }}
.bulle.moi {{ background:linear-gradient(120deg,{BLEU},#5B8DEF); color:#fff; border-bottom-right-radius:6px; }}
.bulle.robot {{ min-width:60%; background:#F2F6FD; color:{NAVY}; border-bottom-left-radius:6px; border:1px solid #E1E9F7; }}
.bulle .trad {{ font-size:1.45rem; font-weight:700; margin:4px 0 2px; }}
.bulle .meta {{ font-size:.78rem; color:#7a8396; }}
.tag {{ display:inline-block; border-radius:10px; padding:2px 9px; font-size:.74rem; font-weight:700; margin-right:5px; }}
.t-en {{ background:#E3EDFF; color:{BLEU}; }} .t-da {{ background:#E1F5F1; color:{VERT}; }} .t-llm {{ background:#FFF3D6; color:#9A6A00; }}

/* ---------- Étapes ---------- */
.etapes {{ display:flex; gap:8px; margin-top:6px; }}
.etape {{ flex:1; background:#F7F9FD; border-radius:14px; padding:10px 8px; text-align:center; border:1px solid #E8EEF8; }}
.etape .ico {{ font-size:1.3rem; }} .etape .nom {{ font-size:.75rem; color:#7a8396; font-weight:600; }}
.etape .ms {{ font-size:1.05rem; font-weight:800; color:{NAVY}; }}

/* ---------- Indicateurs ---------- */
.kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:6px 0 18px; }}
.kpi {{ border-radius:20px; padding:18px 20px; color:#fff; box-shadow:0 10px 24px rgba(15,41,84,.15); }}
.kpi .v {{ font-size:2rem; font-weight:800; line-height:1.1; }} .kpi .l {{ font-size:.85rem; opacity:.9; }}
.k1 {{ background:linear-gradient(130deg,{NAVY},{BLEU}); }} .k2 {{ background:linear-gradient(130deg,#1A8FB5,{VERT}); }}
.k3 {{ background:linear-gradient(130deg,#E08A00,{OR}); }} .k4 {{ background:linear-gradient(130deg,#E0457A,{ROSE}); }}

.vide {{ text-align:center; padding:40px 10px; color:#7a8396; }} .vide .gros {{ font-size:3rem; }}
section[data-testid="stSidebar"] {{ background:linear-gradient(180deg,#0F2954,#163a75); }}
section[data-testid="stSidebar"] * {{ color:#E8EEFA !important; }}
section[data-testid="stSidebar"] .stButton button {{ background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.25); border-radius:12px; }}
</style>"""
st.markdown("\n".join(l for l in CSS.splitlines() if l.strip()), unsafe_allow_html=True)

ROBOT_SVG = f"""<svg class="robot" viewBox="0 0 200 220" xmlns="http://www.w3.org/2000/svg">
<line x1="100" y1="18" x2="100" y2="42" stroke="#fff" stroke-width="5"/>
<circle class="antenne" cx="100" cy="14" r="10" fill="{OR}"/>
<rect x="38" y="40" width="124" height="98" rx="34" fill="#fff"/>
<rect x="54" y="60" width="92" height="56" rx="24" fill="{NAVY}"/>
<ellipse class="oeil" cx="82" cy="88" rx="10" ry="12" fill="{CIEL}"/>
<ellipse class="oeil" cx="118" cy="88" rx="10" ry="12" fill="{CIEL}"/>
<path d="M88 104 Q100 112 112 104" stroke="{CIEL}" stroke-width="4" fill="none" stroke-linecap="round"/>
<rect x="26" y="74" width="14" height="30" rx="7" fill="#DCE6F7"/><rect x="160" y="74" width="14" height="30" rx="7" fill="#DCE6F7"/>
<rect x="56" y="146" width="88" height="58" rx="22" fill="#fff"/>
<rect x="86" y="160" width="28" height="10" rx="5" fill="{BLEU}"/>
<circle cx="78" cy="186" r="5" fill="{ROSE}"/><circle cx="100" cy="186" r="5" fill="{OR}"/><circle cx="122" cy="186" r="5" fill="#22C55E"/>
</svg>"""


@st.cache_data(ttl=30)
def etat_composants():
    return [("🎤", "Whisper", "voix → texte", whisper_disponible()),
            ("🧠", "LLM " + config.LLM_MODELE, "comprendre", llm_disponible()),
            ("🌍", "NLLB-200", "traduction", nllb_disponible()),
            ("🔊", "MMS-TTS", "voix du robot", tts_disponible())]


etat = etat_composants()
nb_reels = sum(e[3] for e in etat)

# ------------------------------------------------------------------ BARRE LATÉRALE
with st.sidebar:
    robot_petit = ROBOT_SVG.replace('class="robot"', 'style="width:110px"')
    st.markdown(f"<div style='text-align:center;margin-top:-10px'>{robot_petit}</div>", unsafe_allow_html=True)
    st.markdown("### 🤖 Le robot")
    st.markdown(f"**{nb_reels}/4** outils réels actifs")
    st.progress(nb_reels / 4)
    for ico, nom, role, ok in etat:
        st.markdown(f"{'🟢' if ok else '🟡'} {ico} **{nom}**  \n<span style='opacity:.7;font-size:.82rem'>{role} · {'réel' if ok else 'mode démo'}</span>", unsafe_allow_html=True)
    st.divider()
    st.markdown("**🧪 Avant la démo**")
    if st.button("🧹 Vider l'historique", use_container_width=True):
        with db.connexion() as c:
            c.execute("DELETE FROM echanges")
        st.session_state["conversation"] = []
        st.toast("Historique vidé", icon="🧹")
        st.rerun()
    st.divider()
    st.caption("HESTIM · 5A IIIA · 2026/2027  \nAwa Aimée Benzekry  \nRamatoulaye Diawane  \nEncadrant : Dr. Sridath TULA")

# ------------------------------------------------------------------ BANDEAU
st.markdown(f"""<div class="hero"><div style="z-index:1">
<h1>Robot traducteur</h1>
<div class="sous">Parle-lui en français, il te répond en anglais ou en darija 👋</div>
<span class="lang">🇫🇷 Français</span><span class="lang">→ 🇬🇧 Anglais</span><span class="lang">→ 🇲🇦 Darija</span>
</div>{ROBOT_SVG}</div>""", unsafe_allow_html=True)

st.markdown("<div class='etats'>" + "".join(
    f"<div class='etat'><span class='point {'vert' if ok else 'jaune'}'></span>{ico} {nom} <small>{'réel' if ok else 'démo'}</small></div>"
    for ico, nom, role, ok in etat) + "</div>", unsafe_allow_html=True)

onglet_cmd, onglet_hist, onglet_stats = st.tabs(["🎙️  Commander", "📜  Historique", "📊  Statistiques"])

if "conversation" not in st.session_state:
    st.session_state["conversation"] = []


def tag_langue(langue):
    return "<span class='tag t-da'>🇲🇦 darija</span>" if langue == "darija" else "<span class='tag t-en'>🇬🇧 anglais</span>"


# ------------------------------------------------------------------ COMMANDER
with onglet_cmd:
    gauche, droite = st.columns([5, 6], gap="large")
    with gauche:
        with st.container(border=True):
            st.markdown("<div class='titre-carte'>💬 Parle au robot</div><div class='aide'>Écris ou dis une phrase en français.</div>", unsafe_allow_html=True)
            choix = st.segmented_control("Langue de traduction", ["✨ Auto", "🇬🇧 Anglais", "🇲🇦 Darija"], default="✨ Auto")
            langue_forcee = {"🇬🇧 Anglais": "anglais", "🇲🇦 Darija": "darija"}.get(choix)
            if choix == "✨ Auto" or choix is None:
                st.caption("✨ Le LLM devine la langue dans ta phrase (« en darija… », « en anglais… »).")
            mode = st.segmented_control("Comment veux-tu parler ?", ["✍️ J'écris", "🎤 Je parle"], default="✍️ J'écris")
            resultat = None
            if mode == "🎤 Je parle":
                son = st.audio_input("Appuie sur le micro et parle")
                if son is not None and st.button("🚀 Traduire ma voix", type="primary", use_container_width=True):
                    chemin = Path(tempfile.gettempdir()) / "entree_micro.wav"
                    chemin.write_bytes(son.getvalue())
                    with st.spinner("🤖 J'écoute, je comprends, je traduis..."):
                        resultat = traiter(audio=chemin, canal="voix", langue_forcee=langue_forcee)
            else:
                phrase = st.text_input("Ta phrase", placeholder="Ex. : Comment on dit merci beaucoup en darija ?", label_visibility="collapsed")
                ex = st.pills("Ou essaie un exemple 👇", ["En anglais : où se trouve la bibliothèque ?",
                                                          "Comment on dit merci beaucoup en darija ?",
                                                          "Bonjour, je cherche la salle 12"])
                texte = phrase or ex
                if st.button("🚀 Traduire", type="primary", disabled=not texte, use_container_width=True):
                    with st.spinner("🤖 Je réfléchis..."):
                        resultat = traiter(texte=texte, canal="texte", langue_forcee=langue_forcee)
            if resultat:
                st.session_state["dernier"] = resultat
                st.session_state["conversation"].insert(0, resultat)
                st.toast("Traduction prête !", icon="🤖")

        r = st.session_state.get("dernier")
        if r:
            with st.container(border=True):
                st.markdown("<div class='titre-carte'>⚡ Le parcours de la phrase</div><div class='aide'>Temps passé à chaque étape</div>", unsafe_allow_html=True)
                t = r["temps"]
                etapes = [("🎤", "Écoute", t["transcription_ms"]), ("🧠", "Compréhension", t["comprehension_ms"]),
                          ("🌍", "Traduction", t["traduction_ms"]), ("🔊", "Voix", t["voix_ms"])]
                st.markdown("<div class='etapes'>" + "".join(
                    f"<div class='etape'><div class='ico'>{i}</div><div class='nom'>{n}</div><div class='ms'>{v} ms</div></div>"
                    for i, n, v in etapes) + "</div>", unsafe_allow_html=True)
                conf = "–" if r["confiance"] is None else f"{r['confiance']:.0%}"
                st.markdown(f"<div class='aide' style='margin-top:10px'>⏱️ Total : <b>{r['temps_total_ms']} ms</b> · 🎯 Confiance de l'écoute : <b>{conf}</b></div>", unsafe_allow_html=True)

    with droite:
        with st.container(border=True):
            st.markdown("<div class='titre-carte'>🤖 Conversation avec le robot</div><div class='aide'>Les dernières traductions, de la plus récente à la plus ancienne.</div>", unsafe_allow_html=True)
            conv = st.session_state["conversation"][:6]
            if not conv:
                st.markdown("<div class='vide'><div class='gros'>👋</div>Dis bonjour au robot !<br>Ta première traduction apparaîtra ici.</div>", unsafe_allow_html=True)
            for i, c in enumerate(conv):
                canal = "🎤 dit" if c["canal"] == "voix" else "✍️ écrit"
                bulles = (
                    f"<div class='ligne moi'><div class='bulle moi'>{html.escape(c['phrase_brute'])}"
                    f"<div style='font-size:.72rem;opacity:.8;margin-top:3px'>{canal}</div></div><div class='avatar av-moi'>🙋‍♀️</div></div>"
                    f"<div class='ligne'><div class='avatar av-robot'>🤖</div><div class='bulle robot'>"
                    f"{tag_langue(c['langue'])}<span class='tag t-llm'>🧠 {c['methode_comprehension']}</span>"
                    f"<div class='trad' dir='auto'>{html.escape(c['traduction'])}</div>"
                    f"<div class='meta'>« {html.escape(c['phrase_fr'])} » · {c['methode_traduction']} · {c['temps_total_ms']} ms</div></div></div>")
                st.markdown(bulles, unsafe_allow_html=True)
                if i == 0 and c.get("audio_sortie"):
                    st.audio(c["audio_sortie"], autoplay=True)

# ------------------------------------------------------------------ HISTORIQUE
with onglet_hist:
    df = db.tout_lire()
    if df.empty:
        st.markdown("<div class='vide'><div class='gros'>📭</div>Aucune traduction pour l'instant.</div>", unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown("<div class='titre-carte'>🔎 Filtrer</div>", unsafe_allow_html=True)
            f1, f2, f3 = st.columns([1, 1, 2])
            langues = f1.multiselect("Langue", sorted(df["langue"].dropna().unique()), placeholder="Toutes")
            canaux = f2.multiselect("Canal", sorted(df["canal"].dropna().unique()), placeholder="Tous")
            mot = f3.text_input("Mot-clé", placeholder="bibliothèque, merci...")
        vue = df.copy()
        if langues:
            vue = vue[vue["langue"].isin(langues)]
        if canaux:
            vue = vue[vue["canal"].isin(canaux)]
        if mot:
            m = mot.lower()
            vue = vue[vue["phrase_fr"].str.lower().str.contains(m, na=False) | vue["traduction"].str.lower().str.contains(m, na=False)]
        vue_aff = vue.copy()
        vue_aff["langue"] = vue_aff["langue"].map({"anglais": "🇬🇧 anglais", "darija": "🇲🇦 darija"}).fillna(vue_aff["langue"])
        vue_aff["canal"] = vue_aff["canal"].map({"voix": "🎤 voix", "texte": "✍️ texte", "ros2": "🤖 ROS 2"}).fillna(vue_aff["canal"])
        vue_aff["corrigée"] = vue_aff["correction"].fillna("").str.len() > 0
        st.dataframe(
            vue_aff[["id", "date", "canal", "phrase_fr", "langue", "traduction", "temps_ms", "corrigée", "methode_comprehension"]],
            use_container_width=True, hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("N°", width="small"),
                "date": "🕒 Date", "canal": "Canal", "phrase_fr": "🇫🇷 Phrase", "langue": "Langue", "traduction": "Traduction",
                "temps_ms": st.column_config.ProgressColumn("⏱️ Temps (ms)", min_value=0, max_value=int(max(df["temps_ms"].max(), 1)), format="%d ms"),
                "corrigée": st.column_config.CheckboxColumn("✏️ Corrigée"),
                "methode_comprehension": "🧠 Compris par",
            })
        st.download_button("⬇️ Télécharger en CSV", vue.to_csv(index=False).encode("utf-8"), "historique_traductions.csv", "text/csv")

        with st.container(border=True):
            st.markdown("<div class='titre-carte'>✏️ Corriger une traduction</div><div class='aide'>Aide le robot à progresser : les corrections servent à repérer ses erreurs.</div>", unsafe_allow_html=True)
            k1, k2 = st.columns([1, 3])
            choix_id = k1.selectbox("N° de l'échange", vue["id"].tolist())
            ligne = df[df["id"] == choix_id].iloc[0]
            k2.markdown(f"« {html.escape(str(ligne['phrase_fr']))} » → <b dir='auto'>{html.escape(str(ligne['traduction']))}</b>", unsafe_allow_html=True)
            correction = k2.text_input("Bonne traduction", value=ligne["correction"] or "")
            if k2.button("💾 Enregistrer la correction", type="primary"):
                db.corriger(int(choix_id), correction)
                st.toast("Correction enregistrée, merci !", icon="✏️")
                st.rerun()

# ------------------------------------------------------------------ STATISTIQUES
with onglet_stats:
    df = db.tout_lire()
    if df.empty:
        st.markdown("<div class='vide'><div class='gros'>📊</div>Les statistiques apparaîtront après les premières traductions.</div>", unsafe_allow_html=True)
    else:
        df["date"] = pd.to_datetime(df["date"])
        nb_corr = int(df["correction"].fillna("").str.len().gt(0).sum())
        st.markdown(f"""<div class="kpis">
<div class="kpi k1"><div class="l">🌍 Traductions</div><div class="v">{len(df)}</div></div>
<div class="kpi k2"><div class="l">⏱️ Temps moyen</div><div class="v">{df['temps_ms'].mean():.0f} ms</div></div>
<div class="kpi k3"><div class="l">🇲🇦 Part en darija</div><div class="v">{(df['langue'] == 'darija').mean():.0%}</div></div>
<div class="kpi k4"><div class="l">✏️ Corrigées</div><div class="v">{nb_corr}</div></div></div>""", unsafe_allow_html=True)

        couleurs = alt.Scale(domain=["anglais", "darija"], range=[BLEU, VERT])
        g1, g2 = st.columns(2, gap="large")
        with g1:
            with st.container(border=True):
                st.markdown("<div class='titre-carte'>🌍 Langues demandées</div>", unsafe_allow_html=True)
                d = df["langue"].value_counts().reset_index()
                d.columns = ["langue", "nombre"]
                st.altair_chart(alt.Chart(d).mark_arc(innerRadius=70, cornerRadius=6).encode(
                    theta="nombre:Q", color=alt.Color("langue:N", scale=couleurs, legend=alt.Legend(orient="bottom", title=None)),
                    tooltip=["langue", "nombre"]).properties(height=260), use_container_width=True)
        with g2:
            with st.container(border=True):
                st.markdown("<div class='titre-carte'>🎤 Voix ou ✍️ texte</div>", unsafe_allow_html=True)
                d = df["canal"].value_counts().reset_index()
                d.columns = ["canal", "nombre"]
                st.altair_chart(alt.Chart(d).mark_bar(cornerRadiusEnd=8, height=34).encode(
                    y=alt.Y("canal:N", title=None, sort="-x"), x=alt.X("nombre:Q", title=None),
                    color=alt.Color("canal:N", scale=alt.Scale(range=[NAVY, ROSE, OR]), legend=None),
                    tooltip=["canal", "nombre"]).properties(height=260), use_container_width=True)
        g3, g4 = st.columns(2, gap="large")
        with g3:
            with st.container(border=True):
                st.markdown("<div class='titre-carte'>🕒 Utilisation par heure</div>", unsafe_allow_html=True)
                d = df["date"].dt.hour.value_counts().sort_index().reset_index()
                d.columns = ["heure", "nombre"]
                st.altair_chart(alt.Chart(d).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color=VERT).encode(
                    x=alt.X("heure:O", title="Heure"), y=alt.Y("nombre:Q", title=None), tooltip=["heure", "nombre"]
                ).properties(height=240), use_container_width=True)
        with g4:
            with st.container(border=True):
                st.markdown("<div class='titre-carte'>⏱️ Temps de réponse</div>", unsafe_allow_html=True)
                d = df.sort_values("date")[["id", "temps_ms", "langue"]]
                st.altair_chart(alt.Chart(d).mark_line(point=True, interpolate="monotone").encode(
                    x=alt.X("id:O", title="Traduction n°"), y=alt.Y("temps_ms:Q", title="ms"),
                    color=alt.Color("langue:N", scale=couleurs, legend=alt.Legend(orient="bottom", title=None)),
                    tooltip=["id", "langue", "temps_ms"]).properties(height=240), use_container_width=True)
        corr = df[df["correction"].fillna("").str.len() > 0]
        if not corr.empty:
            with st.container(border=True):
                st.markdown("<div class='titre-carte'>🧐 Phrases corrigées</div><div class='aide'>Là où le robot se trompe le plus</div>", unsafe_allow_html=True)
                st.dataframe(corr[["phrase_fr", "langue", "traduction", "correction"]], use_container_width=True, hide_index=True)