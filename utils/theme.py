# utils/theme.py

import streamlit as st

def aplicar_tema(titulo_pagina, icone_pagina):
    """
    Configura a página do Streamlit e aplica uma folha de estilo CSS premium.
    Centraliza a identidade visual do QualiHub.
    """
    st.set_page_config(
        page_title=f"QualiHub - {titulo_pagina}",
        page_icon=icone_pagina,
        layout="wide"
    )
    
    # CSS Customizado para Revamp de Layout
    css = """
    <style>
    /* 1. Importando e aplicando a fonte Outfit */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* 2. Títulos e Subtítulos Premium */
    h1 {
        font-weight: 700 !important;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        padding-bottom: 5px !important;
    }
    
    h2, h3 {
        color: #1E3A8A !important;
        font-weight: 600 !important;
        margin-top: 15px !important;
    }
    
    /* Linhas divisórias com degradê */
    hr {
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
        border: 0 !important;
        border-top: 2px solid rgba(59, 130, 246, 0.15) !important;
    }
    
    /* 3. Estilização dos Formulários (Form Cards) */
    div[data-testid="stForm"] {
        border: 1px solid rgba(30, 58, 138, 0.1) !important;
        border-radius: 16px !important;
        padding: 30px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03) !important;
        background-color: #FFFFFF !important;
    }
    
    /* 4. Estilização de Botões */
    div.stButton > button, div[data-testid="stForm"] button[type="submit"] {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.18) !important;
        transition: all 0.3s ease !important;
        width: auto !important;
    }
    
    div.stButton > button:hover, div[data-testid="stForm"] button[type="submit"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%) !important;
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    /* 5. Estilização de Métricas (Dashboard Cards) */
    div[data-testid="stMetric"] {
        background-color: rgba(30, 58, 138, 0.03);
        border: 1px solid rgba(30, 58, 138, 0.08);
        border-radius: 16px;
        padding: 20px 25px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.01);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div[data-testid="stMetric"]:hover {
        background-color: rgba(30, 58, 138, 0.06);
        border-color: rgba(30, 58, 138, 0.18);
        box-shadow: 0 8px 20px rgba(30, 58, 138, 0.08);
        transform: translateY(-2px);
    }
    
    div[data-testid="stMetric"] label {
        font-size: 14px !important;
        color: #4B5563 !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
    }
    
    /* 6. Customização do Dataframe */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(30, 58, 138, 0.08) !important;
    }
    
    /* Estilização da barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    section[data-testid="stSidebar"] div.stSubheader {
        font-weight: 600 !important;
        color: #0F172A !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
