# utils/theme.py

import streamlit as st

def aplicar_tema(titulo_pagina, icone_pagina):
    """
    Configura a página do Streamlit e aplica uma folha de estilo CSS minimalista premium
    que utiliza variáveis nativas do Streamlit para suportar automaticamente os temas Claro e Escuro.
    """
    st.set_page_config(
        page_title=f"QualiHub - {titulo_pagina}",
        page_icon=icone_pagina,
        layout="wide"
    )
    
    # CSS Customizado - Adaptativo Claro/Escuro (B2B Minimalista)
    css = """
    <style>
    /* 1. Importando e aplicando a fonte Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
    }
    
    html, body, .stApp {
        background-color: var(--st-background-color) !important;
        color: var(--st-text-color) !important;
    }
    
    /* 2. Títulos e Subtítulos Adaptativos */
    h1 {
        font-weight: 700 !important;
        color: var(--st-text-color) !important;
        letter-spacing: -0.025em !important;
        padding-bottom: 5px !important;
    }
    
    h2, h3 {
        color: var(--st-text-color) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        margin-top: 20px !important;
        opacity: 0.95 !important;
    }
    
    /* Linhas divisórias sutis adaptativas */
    hr {
        margin-top: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        border: 0 !important;
        border-top: 1px solid var(--st-secondary-background-color) !important;
        opacity: 0.5 !important;
    }
    
    /* 3. Estilização dos Formulários (Form Cards) */
    div[data-testid="stForm"] {
        border: 1px solid var(--st-secondary-background-color) !important;
        border-radius: 8px !important;
        padding: 24px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
        background-color: var(--st-background-color) !important;
    }
    
    /* 4. Estilização de Botões (Contraste Invertido Adaptativo) */
    div.stButton > button, div[data-testid="stForm"] button[type="submit"] {
        background-color: var(--st-text-color) !important; /* Cor oposta ao fundo */
        color: var(--st-background-color) !important;
        border: 1px solid var(--st-text-color) !important;
        border-radius: 6px !important;
        padding: 8px 20px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        transition: opacity 0.15s ease-in-out !important;
        width: auto !important;
    }
    
    div.stButton > button:hover, div[data-testid="stForm"] button[type="submit"]:hover {
        opacity: 0.85 !important;
    }
    
    /* 5. Estilização de Métricas (Dashboard Cards) */
    div[data-testid="stMetric"] {
        background-color: var(--st-secondary-background-color) !important;
        border: 1px solid var(--st-secondary-background-color) !important;
        border-radius: 8px !important;
        padding: 16px 20px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02) !important;
        transition: border-color 0.15s ease-in-out !important;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: var(--st-text-color) !important;
    }
    
    div[data-testid="stMetric"] label {
        font-size: 13px !important;
        color: var(--st-text-color) !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        opacity: 0.6 !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 600 !important;
        color: var(--st-text-color) !important;
        letter-spacing: -0.02em !important;
    }
    
    /* 6. Customização do Dataframe */
    .stDataFrame {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid var(--st-secondary-background-color) !important;
    }
    
    /* Estilização da barra lateral */
    section[data-testid="stSidebar"] {
        background-color: var(--st-secondary-background-color) !important;
        border-right: 1px solid var(--st-secondary-background-color) !important;
    }
    
    section[data-testid="stSidebar"] div.stSubheader {
        font-weight: 600 !important;
        color: var(--st-text-color) !important;
    }
    
    /* Ajustando inputs do Streamlit */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 6px !important;
    }
    
    /* Estilização dos Callouts (Alerts) */
    div[data-testid="stNotification"] {
        border-radius: 8px !important;
        border: 1px solid var(--st-secondary-background-color) !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
