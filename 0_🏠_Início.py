import streamlit as st
from utils.db import inicializar_banco
from utils.theme import aplicar_tema

# Inicialização do banco de dados (tabelas e schema)
inicializar_banco()

# Configuração de Página e Estilos Globais
aplicar_tema("Início", "🏢")

st.title("🏢 QualiHub - Sistema de Gestão da Qualidade")
st.markdown("---")

st.header("Módulo de Recebimento de Insumos")
st.write(
    """
    Bem-vindo(a) ao **QualiHub**! Este é o sistema desenvolvido para digitalizar, centralizar 
    e automatizar os processos de qualidade no recebimento de grãos e matérias-primas.
    
    **👈 Por favor, utilize o menu na barra lateral para navegar entre os módulos operacionais.**
    """
)

st.subheader("Módulos Disponíveis: ")
st.markdown(
    """
    - **[Cadastro de Fornecedores](Cadastro_de_Fornecedores)**: Cadastro de parceiros comerciais.
    - **[Motoristas e Veículos](Motoristas_e_Veículos)**: Cadastro e controle logístico de acesso.
    - **[Agendamento de Entregas](Agendamento)**: Planejamento de entregas de insumos.
    - **[Análise de Recebimento](Análise_de_Recebimento)**: Testes físico-químicos e Motor de Decisão de qualidade.
    - **[Visualização de Janelas](Visualização_de_Janelas)**: Fila e monitoramento operacional de portaria.
    """
)

st.info("Este projeto está configurado para simulação de recebimento na doca.")

# Seção de Testes
st.markdown("---")
with st.expander("🧪 Ambiente de Desenvolvimento / Testes"):
    st.write("Carregue dados fictícios de demonstração para simular o uso operacional imediatamente.")
    if st.button("⚡ Popular Banco de Dados"):
        from utils.seeder import popular_banco
        sucesso = popular_banco(limpar_tabelas=True)
        if sucesso:
            st.success("✅ Banco de dados redefinido e populado com sucesso com dados de teste ricos!")
            st.toast("Dados fictícios gerados com sucesso!", icon="⚡")
        else:
            st.error("❌ Falha ao popular o banco de dados.")