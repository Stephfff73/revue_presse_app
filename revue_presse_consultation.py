"""
Consultation de la revue de presse — DPIEC
=============================================
App de LECTURE, destinee aux destinataires de la revue de presse.
Affiche la derniere edition publiee par l'equipe DPIEC (via le bouton
"Publier pour vos collègues" de revue_presse_app.py), avec un
historique des editions precedentes.

Cette app doit se trouver dans le MEME dossier que revue_presse_app.py :
elle lit son dossier revues_publiees/, cree automatiquement lors de la
premiere publication.

Lancer l'app :
    pip install streamlit
    streamlit run revue_presse_consultation.py
"""

import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Revue de presse - DPIEC", page_icon="📰", layout="wide")

DOSSIER_APP = Path(__file__).resolve().parent
CONFIG_PATH = DOSSIER_APP / "config_app.json"
DOSSIER_PUBLICATION_DEFAUT = str(DOSSIER_APP / "revues_publiees")


def charger_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def sauvegarder_config():
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"dossier_publication": st.session_state.dossier_publication}, f, ensure_ascii=False)
    except Exception:
        pass


if "dossier_publication" not in st.session_state:
    st.session_state.dossier_publication = charger_config().get(
        "dossier_publication", DOSSIER_PUBLICATION_DEFAUT
    )

st.markdown(
    """
<style>
    .block-container { padding-top: 1.3rem; padding-bottom: 1rem; max-width: 900px; }
    #MainMenu, footer {visibility: hidden;}
    .bandeau-lecture {
        position: relative;
        overflow: hidden;
        border-radius: 14px;
        background: linear-gradient(120deg, #013E42 0%, #004E52 55%, #0C6E70 100%);
        padding: 24px 28px;
        margin-bottom: 22px;
        box-shadow: 0 14px 30px -18px rgba(0, 20, 20, 0.55);
    }
    .bandeau-lecture::after {
        content: "";
        position: absolute;
        top: -50px;
        right: -40px;
        width: 190px;
        height: 190px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(235, 41, 93, 0.35), transparent 70%);
        pointer-events: none;
    }
    .bandeau-lecture .ligne-haut {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .bandeau-lecture .icone {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.14);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .bandeau-lecture h1 {
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.5rem;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .bandeau-lecture p {
        color: rgba(255, 255, 255, 0.8);
        margin: 8px 0 0 58px;
        font-size: 0.92rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

_ICONE_JOURNAL_SVG = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="4" width="18" height="16" rx="2" stroke="#FFFFFF" stroke-width="1.6"/>
  <line x1="6.5" y1="8" x2="12" y2="8" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
  <line x1="6.5" y1="11" x2="17.5" y2="11" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
  <line x1="6.5" y1="14" x2="17.5" y2="14" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
  <line x1="6.5" y1="17" x2="14" y2="17" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
</svg>"""

st.markdown(
    f"""
<div class="bandeau-lecture">
  <div class="ligne-haut">
    <div class="icone">{_ICONE_JOURNAL_SVG}</div>
    <h1>Revue de presse de la DPIEC</h1>
  </div>
  <p>Toutes les éditions publiées par l'équipe — choisissez une semaine ci-dessous.</p>
</div>
""",
    unsafe_allow_html=True,
)


with st.expander("⚙️ Emplacement des revues publiées"):
    _dossier_saisi = st.text_input(
        "Dossier de publication (le même que celui réglé côté back-office, "
        "ou le dossier local de votre SharePoint synchronisé via OneDrive)",
        value=st.session_state.dossier_publication,
    )
    if _dossier_saisi != st.session_state.dossier_publication:
        st.session_state.dossier_publication = _dossier_saisi
        sauvegarder_config()
        st.rerun()

PUBLICATION_DIR = Path(st.session_state.dossier_publication)
MANIFEST_PUBLICATION = PUBLICATION_DIR / "manifest.json"


def charger_manifest():
    if MANIFEST_PUBLICATION.exists():
        try:
            with open(MANIFEST_PUBLICATION, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


manifest = charger_manifest()

if not manifest:
    st.info(
        "Aucune édition publiée pour le moment. Revenez un peu plus tard, "
        "ou contactez l'équipe DPIEC."
    )
else:
    manifest_trie = sorted(manifest, key=lambda m: m["fichier"], reverse=True)
    options = [f"{m['numero']} — semaine du {m['date']}" for m in manifest_trie]

    col_choix, col_espace = st.columns([2, 3])
    with col_choix:
        choix = st.selectbox("Édition", options=options, index=0, label_visibility="collapsed")
    edition = manifest_trie[options.index(choix)]

    chemin_html = PUBLICATION_DIR / edition["fichier"]
    if chemin_html.exists():
        with open(chemin_html, "r", encoding="utf-8") as f:
            contenu = f.read()
        st.components.v1.html(contenu, height=2400, scrolling=True)
    else:
        st.error("Le fichier de cette édition est introuvable.")
