# Sistema de Qualidade/app.py

import streamlit as st

st.set_page_config(
    page_title="QUALICENTRAL - Início",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 QUALICENTRAL - Sistema de Gestão da Qualidade")
st.markdown("---")
st.header("Módulo de Recebimento de Insumos")

st.write(
    """
    Bem-vindo(a) ao QUALICENTRAL! Este é o sistema desenvolvido para centralizar
    e automatizar os processos de qualidade da indústria.

    **👈 Por favor, utilize o menu na barra lateral para navegar entre os módulos.**
    """
)

st.subheader("Módulos Disponíveis:")
st.markdown(
    """
    - **[Cadastro de Fornecedores](Cadastro_de_Fornecedores)**: Adicione novos fornecedores ao sistema.
    - **[Agendamento](Agendamento)**: Em breve.
    - **[Visualização de Janelas](Visualiza_o_de_Janelas)**: Em breve.
    """
)

st.info("Este projeto está em desenvolvimento ativo. Novas funcionalidades serão adicionadas em breve.")