# utils/theme.py

import streamlit as st

def aplicar_tema(titulo_pagina, icone_pagina):
    """
    Configura a página do Streamlit e aplica uma folha de estilo CSS minimalista premium
    que utiliza variáveis nativas do Streamlit para suportar automaticamente os temas Claro e Escuro.
    """
    try:
        st.set_page_config(
            page_title=f"QualiHub - {titulo_pagina}",
            page_icon=icone_pagina,
            layout="wide"
        )
    except Exception:
        pass
    
    css = """
    <style>
    /* 1. Importando e aplicando a fonte Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* 2. Títulos e Subtítulos Premium */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
        padding-bottom: 5px !important;
    }
    
    h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        margin-top: 20px !important;
    }
    
    /* Linhas divisórias sutis */
    hr {
        margin-top: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        border: 0 !important;
        border-top: 1px solid rgba(128, 128, 128, 0.15) !important;
        opacity: 0.5 !important;
    }
    
    /* 3. Estilização dos Formulários (Form Cards) */
    div[data-testid="stForm"] {
        border-radius: 8px !important;
        padding: 24px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
    }
    
    /* 4. Estilização de Botões */
    div.stButton > button, div[data-testid="stForm"] button[type="submit"] {
        border-radius: 6px !important;
        padding: 8px 20px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        transition: opacity 0.15s ease-in-out !important;
    }
    
    div.stButton > button:hover, div[data-testid="stForm"] button[type="submit"]:hover {
        opacity: 0.85 !important;
    }
    
    /* 5. Estilização de Métricas (Dashboard Cards) */
    div[data-testid="stMetric"] {
        border-radius: 8px !important;
        padding: 16px 20px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02) !important;
    }
    
    div[data-testid="stMetric"] label {
        font-size: 13px !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        opacity: 0.6 !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    
    /* 6. Customização do Dataframe */
    .stDataFrame {
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    /* Estilização da barra lateral */
    section[data-testid="stSidebar"] div.stSubheader {
        font-weight: 600 !important;
    }
    
    /* Ajustando inputs do Streamlit */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 6px !important;
    }
    
    /* Estilização dos Callouts (Alerts) */
    div[data-testid="stNotification"] {
        border-radius: 8px !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def obter_badge_status(status):
    """
    Retorna o código HTML formatado com classes CSS premium para badges de status.
    Melhora o padrão DRY (Don't Repeat Yourself) em toda a aplicação.
    """
    mapa_status = {
        "Pendente": {
            "bg": "rgba(245, 158, 11, 0.15)",
            "cor": "#D97706",
            "texto": "Pendente"
        },
        "Em Pesagem": {
            "bg": "rgba(6, 182, 212, 0.15)",
            "cor": "#0891b2",
            "texto": "Em Pesagem"
        },
        "Quarentena": {
            "bg": "rgba(244, 63, 94, 0.15)",
            "cor": "#e11d48",
            "texto": "Quarentena"
        },
        "Concluído": {
            "bg": "rgba(16, 185, 129, 0.15)",
            "cor": "#059669",
            "texto": "Concluído"
        },
        "Aprovado": {
            "bg": "rgba(16, 185, 129, 0.15)",
            "cor": "#059669",
            "texto": "Concluído"
        },
        "Aprovado com Restrição": {
            "bg": "rgba(245, 158, 11, 0.15)",
            "cor": "#D97706",
            "texto": "Aprovado com Restrição"
        },
        "Aprovado com Desvio": {
            "bg": "rgba(59, 130, 246, 0.15)",
            "cor": "#2563eb",
            "texto": "Desvio Liberado"
        },
        "Recusado": {
            "bg": "rgba(239, 68, 68, 0.15)",
            "cor": "#DC2626",
            "texto": "Recusado"
        },
        "Reprovado": {
            "bg": "rgba(239, 68, 68, 0.15)",
            "cor": "#DC2626",
            "texto": "Recusado"
        }
    }
    
    cfg = mapa_status.get(status, {
        "bg": "rgba(128, 128, 128, 0.15)",
        "cor": "#4b5563",
        "texto": status
    })
    
    return f'<span style="background-color: {cfg["bg"]}; color: {cfg["cor"]}; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 600; text-transform: uppercase;">{cfg["texto"]}</span>'

