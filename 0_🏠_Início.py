import streamlit as st
from datetime import datetime
from utils.db import inicializar_banco, executar_query
from utils.theme import aplicar_tema

# Inicialização do banco de dados (tabelas e schema)
inicializar_banco()

# Configuração de Página e Estilos Globais
aplicar_tema("Início", "🏢")

st.title("🏢 QualiHub - Sistema de Gestão da Qualidade")
st.markdown("---")

# 1. CÁLCULO DE MÉTRICAS DINÂMICAS DO PAINEL
try:
    # A. Total de Fornecedores
    df_forn = executar_query("SELECT COUNT(*) as total FROM fornecedores")
    total_fornecedores = int(df_forn['total'].iloc[0]) if not df_forn.empty else 0

    # B. Agendamentos de Hoje
    hoje_str = datetime.now().strftime('%Y-%m-%d')
    df_agend = executar_query("SELECT COUNT(*) as total FROM agendamentos WHERE DataAgendada = ?", (hoje_str,))
    total_agendamentos_hoje = int(df_agend['total'].iloc[0]) if not df_agend.empty else 0

    # C. Total de Análises Realizadas
    df_analises = executar_query("SELECT COUNT(*) as total FROM analises")
    total_analises = int(df_analises['total'].iloc[0]) if not df_analises.empty else 0

    # D. Taxa de Conformidade (% Aprovado ou Aprovado com Restrição)
    df_aprov = executar_query("SELECT COUNT(*) as total FROM analises WHERE StatusLote IN ('Aprovado', 'Aprovado com Restrição')")
    total_aprovados = int(df_aprov['total'].iloc[0]) if not df_aprov.empty else 0
    
    if total_analises > 0:
        taxa_conformidade = (total_aprovados / total_analises) * 100
        taxa_str = f"{taxa_conformidade:.1f}%"
    else:
        taxa_str = "100%"
except Exception as e:
    total_fornecedores = 0
    total_agendamentos_hoje = 0
    total_analises = 0
    taxa_str = "N/A"

# Renderização do Painel de Métricas (Dashboard Superior)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="🏢 Fornecedores Cadastrados", value=total_fornecedores)
with col2:
    st.metric(label="📅 Cargas para Hoje", value=total_agendamentos_hoje)
with col3:
    st.metric(label="🔬 Análises Efetuadas", value=total_analises)
with col4:
    st.metric(label="📈 Taxa de Conformidade", value=taxa_str)

st.markdown("---")

# 2. SEÇÃO DE BOAS-VINDAS E APRESENTAÇÃO
st.header("Módulo de Recebimento de Insumos")
st.write(
    """
    Bem-vindo(a) ao **QualiHub**! Este é o sistema desenvolvido para digitalizar, centralizar 
    e automatizar os processos de qualidade no recebimento de grãos e matérias-primas nas indústrias.
    Utilize os cartões abaixo ou o menu lateral para acessar os módulos correspondentes.
    """
)

# 3. CARD GRID DE NAVEGAÇÃO RÁPIDA (Dashboard SaaS Look)
col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    with st.container(border=True):
        st.subheader("📦 Fornecedores")
        st.write("Cadastro e controle de parceiros comerciais ativos e históricos de auditoria de CNPJ.")
        st.page_link("pages/1_Cadastro de Fornecedores.py", label="Acessar Fornecedores", icon="➡️")

with col_nav2:
    with st.container(border=True):
        st.subheader("🚗 Motoristas e Veículos")
        st.write("Controle logístico de acesso. Cadastro de CPFs de motoristas e placas vinculadas.")
        st.page_link("pages/2_Motoristas e Veículos.py", label="Acessar Logística", icon="➡️")

with col_nav3:
    with st.container(border=True):
        st.subheader("📅 Agendamentos")
        st.write("Planejamento e reserva de janelas horárias de recebimento por insumo na doca.")
        st.page_link("pages/3_Agendamento.py", label="Acessar Agendamento", icon="➡️")

col_nav4, col_nav5, col_nav6 = st.columns(3)

with col_nav4:
    with st.container(border=True):
        st.subheader("🧪 Análise de Recebimento")
        st.write("Inserção de análises físico-químicas de grãos com motor de conformidade legal automático.")
        st.page_link("pages/5_Análise de Recebimento.py", label="Acessar Qualidade", icon="➡️")

with col_nav5:
    with st.container(border=True):
        st.subheader("👁️ Painel de Janelas")
        st.write("Fila de portaria com visão semanal e diária em cards dinâmicos do status da doca.")
        st.page_link("pages/4_Visualização de Janelas.py", label="Acessar Portaria", icon="➡️")

with col_nav6:
    with st.container(border=True):
        st.subheader("💡 Informações")
        st.write("Este sistema opera de acordo com as normas da ANVISA (RDC 722/2022) e do MAPA.")
        st.write("*Status: Simulação de Recebimento Ativa*")

st.markdown("---")

# 4. FLUXOGRAMA OPERACIONAL INTEGRADO
st.subheader("🔄 Fluxo de Processamento de Cargas")
st.markdown(
    """
    O fluxo abaixo ilustra as etapas de validação necessárias para que uma carga seja descarregada:
    """
)

# Desenho do diagrama Mermaid
st.mermaid(
    """
    graph TD
        A[1. Cadastro do Fornecedor] --> B[2. Cadastro de Motorista e Veículo]
        B --> C[3. Agendamento da Carga]
        C --> D[4. Chegada na Portaria e Fila de Janelas]
        D --> E[5. Análise de Amostra em Laboratório]
        E --> F{Motor de Decisão}
        F -- Conforme --> G[Aprovado: Descarga Autorizada]
        F -- Desconto Comercial --> H[Aprovado com Restrição: Descarga com Desconto]
        F -- Não Conforme --> I[Reprovado: Devolução do Veículo]
        
        style G fill:#d4edda,stroke:#28a745,stroke-width:2px;
        style H fill:#fff3cd,stroke:#ffc107,stroke-width:2px;
        style I fill:#f8d7da,stroke:#dc3545,stroke-width:2px;
    """
)

# Seção de Testes / Seeder
st.markdown("---")
with st.expander("🧪 Ambiente de Desenvolvimento / Testes"):
    st.write("Carregue dados fictícios de demonstração para simular o uso operacional imediatamente.")
    if st.button("⚡ Popular Banco de Dados"):
        from utils.seeder import popular_banco
        sucesso = popular_banco(limpar_tabelas=True)
        if sucesso:
            st.success("✅ Banco de dados redefinido e populado com sucesso com dados de teste ricos!")
            st.toast("Dados fictícios gerados com sucesso!", icon="⚡")
            st.rerun()
        else:
            st.error("❌ Falha ao popular o banco de dados.")