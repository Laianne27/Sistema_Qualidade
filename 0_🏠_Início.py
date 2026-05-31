import streamlit as st
from datetime import datetime
from utils.db import inicializar_banco, executar_query
from utils.theme import aplicar_tema

# Inicialização do banco de dados (tabelas e schema)
inicializar_banco()

# Se o banco de dados estiver completamente vazio, popula automaticamente com dados ricos de teste
try:
    df_check = executar_query("SELECT COUNT(*) as total FROM fornecedores")
    if df_check.empty or int(df_check['total'].iloc[0]) == 0:
        from utils.seeder import popular_banco
        popular_banco(limpar_tabelas=True)
except Exception as e:
    pass

# --- PAINEL LATERAL: CONTROLE DE PERFIL DE ACESSO ---
st.sidebar.markdown("### 👤 Controle de Acesso")
perfil = st.sidebar.selectbox(
    "Perfil Operacional",
    options=["Administrador", "Portaria", "Laboratório", "Fornecedor"],
    key="role" # define st.session_state.role
)

# --- DEFINIÇÃO DAS PÁGINAS ---

# Página de Início (Carregada via Função)
def show_inicio():
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
        Utilize a barra lateral para navegar entre os módulos.
        """
    )
    st.info(f"🔑 Você está visualizando o sistema como: **{perfil}**")

    # 3. CARD GRID DE NAVEGAÇÃO RÁPIDA (Exibe links baseados no perfil ativo)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Atalhos do Módulo")
    
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    
    # Define quais atalhos exibir na tela inicial com base nas permissões
    with col_nav1:
        if perfil in ["Administrador"]:
            with st.container(border=True):
                st.subheader("📦 Fornecedores")
                st.write("Cadastro de parceiros comerciais e histórico de auditoria.")
                st.page_link("pages/1_Cadastro de Fornecedores.py", label="Ir para Fornecedores", icon="➡️")
        elif perfil in ["Portaria"]:
            with st.container(border=True):
                st.subheader("🚗 Motoristas e Veículos")
                st.write("Controle logístico de acesso. CPFs de motoristas e placas vinculadas.")
                st.page_link("pages/2_Motoristas e Veículos.py", label="Ir para Logística", icon="➡️")
        elif perfil in ["Laboratório"]:
            with st.container(border=True):
                st.subheader("👁️ Painel de Janelas")
                st.write("Fila de portaria com visão semanal e diária em cards dinâmicos.")
                st.page_link("pages/4_Visualização de Janelas.py", label="Ir para Portaria", icon="➡️")
        elif perfil in ["Fornecedor"]:
            with st.container(border=True):
                st.subheader("📅 Agendamentos")
                st.write("Planejamento e reserva de janelas horárias de recebimento por insumo na doca.")
                st.page_link("pages/3_Agendamento.py", label="Ir para Agendamento", icon="➡️")

    with col_nav2:
        if perfil in ["Administrador", "Portaria"]:
            with st.container(border=True):
                st.subheader("📅 Agendamentos")
                st.write("Planejamento e reserva de janelas horárias de recebimento.")
                st.page_link("pages/3_Agendamento.py", label="Ir para Agendamentos", icon="➡️")
        elif perfil in ["Laboratório"]:
            with st.container(border=True):
                st.subheader("🧪 Análise de Recebimento")
                st.write("Testes físico-químicos com conformidade automática.")
                st.page_link("pages/5_Análise de Recebimento.py", label="Ir para Qualidade", icon="➡️")
        elif perfil in ["Fornecedor"]:
            with st.container(border=True):
                st.subheader("👁️ Painel de Janelas")
                st.write("Monitore a fila e a previsão de descarga de suas cargas em tempo real.")
                st.page_link("pages/4_Visualização de Janelas.py", label="Ir para Portaria", icon="➡️")

    with col_nav3:
        if perfil in ["Administrador"]:
            with st.container(border=True):
                st.subheader("🧪 Análise de Recebimento")
                st.write("Testes físico-químicos com conformidade automática.")
                st.page_link("pages/5_Análise de Recebimento.py", label="Ir para Qualidade", icon="➡️")
        elif perfil in ["Portaria"]:
            with st.container(border=True):
                st.subheader("👁️ Painel de Janelas")
                st.write("Fila de portaria com visão semanal e diária.")
                st.page_link("pages/4_Visualização de Janelas.py", label="Ir para Portaria", icon="➡️")
        else:
            with st.container(border=True):
                st.subheader("💡 Informações")
                st.write("Este sistema opera de acordo com as normas da ANVISA (RDC 722/2022) e do MAPA.")
                st.write("*Status: Simulação Ativa*")

    st.markdown("---")

    # 4. FLUXOGRAMA OPERACIONAL INTEGRADO
    st.subheader("🔄 Fluxo de Processamento de Cargas")
    st.markdown("O fluxo operacional exige a validação das etapas para autorizar o descarregamento:")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        with st.container(border=True):
            st.write("### 📦 1. Cadastros")
            st.write("Registro de fornecedores, motoristas credenciados e seus respectivos veículos no banco de dados.")

    with col_f2:
        with st.container(border=True):
            st.write("### 📅 2. Agendamento")
            st.write("Programação de janelas de entrega para os insumos na doca, evitando conflito de frotas e fila na portaria.")

    with col_f3:
        with st.container(border=True):
            st.write("### 👁️ 3. Portaria")
            st.write("Chegada física do caminhão e acompanhamento operacional em tempo real na fila diária de janelas.")

    col_f4, col_f5, col_f6 = st.columns(3)
    with col_f4:
        with st.container(border=True):
            st.write("### 🧪 4. Laboratório")
            st.write("Coleta de amostra e inserção dos testes físico-químicos (Umidade, Pureza, Toxinas, PH) no sistema.")

    with col_f5:
        with st.container(border=True):
            st.write("### ⚖️ 5. Motor Legal")
            st.write("Validação provisória em tempo real e verificação de conformidade com as legislações MAPA e ANVISA.")

    with col_f6:
        with st.container(border=True):
            st.write("### 🏁 6. Decisão")
            st.write("Emissão de laudo final automático: **Aprovado**, **Aprovado com Desconto (Restrição)** ou **Reprovado**.")

    # Seção de Testes / Seeder (Somente para Administrador)
    if perfil == "Administrador":
        st.markdown("---")
        with st.expander("🧪 Ambiente de Desenvolvimento / Testes (Admin)"):
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


# Instanciando st.Page dos sub-arquivos
page_inicio = st.Page(show_inicio, title="Início", icon="🏠", default=True)
page_fornecedores = st.Page("pages/1_Cadastro de Fornecedores.py", title="Fornecedores", icon="📦")
page_motoristas = st.Page("pages/2_Motoristas e Veículos.py", title="Motoristas e Veículos", icon="🚗")
page_agendamento = st.Page("pages/3_Agendamento.py", title="Agendar Entrega", icon="📅")
page_janelas = st.Page("pages/4_Visualização de Janelas.py", title="Painel de Janelas", icon="👁️")
page_analise = st.Page("pages/5_Análise de Recebimento.py", title="Análise de Qualidade", icon="🧪")

# --- CONSTRUÇÃO DO ROTEADOR DINÂMICO BASEADO NO PERFIL ---
allowed_pages = [page_inicio]

if perfil == "Administrador":
    allowed_pages.extend([page_fornecedores, page_motoristas, page_agendamento, page_janelas, page_analise])
elif perfil == "Portaria":
    allowed_pages.extend([page_motoristas, page_agendamento, page_janelas])
elif perfil == "Laboratório":
    allowed_pages.extend([page_janelas, page_analise])
elif perfil == "Fornecedor":
    allowed_pages.extend([page_agendamento, page_janelas])

# Execução do Roteador
pg = st.navigation(allowed_pages)
pg.run()