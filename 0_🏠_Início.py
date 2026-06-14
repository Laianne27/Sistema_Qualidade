import streamlit as st
import pandas as pd
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

# Inicializa variáveis no Session State para segurança de dados do Fornecedor
if "fornecedor_logado_nome" not in st.session_state:
    st.session_state["fornecedor_logado_nome"] = None
if "fornecedor_logado_cnpj" not in st.session_state:
    st.session_state["fornecedor_logado_cnpj"] = None
if "fornecedor_cnpj_input" not in st.session_state:
    st.session_state["fornecedor_cnpj_input"] = ""

def formatar_cnpj(cnpj_raw):
    digitos = "".join(filter(str.isdigit, cnpj_raw))
    if len(digitos) == 14:
        return f"{digitos[0:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:14]}"
    return cnpj_raw

if perfil == "Fornecedor":
    cnpj_input = st.sidebar.text_input(
        "CNPJ da Empresa",
        value=st.session_state["fornecedor_cnpj_input"],
        placeholder="Digite o CNPJ...",
        help="Insira o CNPJ cadastrado para acessar a sua área."
    )
    
    st.session_state["fornecedor_cnpj_input"] = cnpj_input
    
    if cnpj_input.strip():
        cnpj_formatado = formatar_cnpj(cnpj_input)
        cnpj_limpo = "".join(filter(str.isdigit, cnpj_input))
        forn_query = executar_query(
            "SELECT NomeEmpresa, CNPJ FROM fornecedores WHERE CNPJ = ? OR CNPJ = ?", 
            (cnpj_formatado, cnpj_limpo)
        )
        if not forn_query.empty:
            st.session_state["fornecedor_logado_nome"] = forn_query['NomeEmpresa'].iloc[0]
            st.session_state["fornecedor_logado_cnpj"] = forn_query['CNPJ'].iloc[0]
            st.sidebar.success(f"🏢 Conectado: **{st.session_state['fornecedor_logado_nome']}**")
        else:
            st.session_state["fornecedor_logado_nome"] = None
            st.session_state["fornecedor_logado_cnpj"] = None
            st.sidebar.warning("⚠️ CNPJ não cadastrado. Realize o autocadastro no menu.")
    else:
        st.session_state["fornecedor_logado_nome"] = None
        st.session_state["fornecedor_logado_cnpj"] = None
        st.sidebar.info("💡 Insira o CNPJ para acessar ou realize o autocadastro.")

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
            taxa_str = f"{taxa_conformidade:.1f}%".replace('.', ',')
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

    # Criando as abas para separar visão geral de atalhos e o painel analítico (BI)
    tab_dashboard, tab_analytics = st.tabs(["🏢 Visão Geral & Atalhos", "📊 Painel Analytics (BI)"])

    with tab_dashboard:
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

    with tab_analytics:
        st.subheader("📊 Indicadores de Conformidade & Volumetria")
        st.markdown("Análise temporal e estatística das cargas recebidas.")
        
        # Filtro de dados baseado no perfil do Fornecedor logado
        if perfil == "Fornecedor":
            forn_cnpj = st.session_state.get("fornecedor_logado_cnpj")
            forn_query = executar_query("SELECT ID FROM fornecedores WHERE CNPJ = ?", (forn_cnpj,))
            forn_id = int(forn_query['ID'].iloc[0]) if not forn_query.empty else -1
            
            df_analises_bi = executar_query(
                "SELECT DataHora, Umidade, Insumo, StatusLote FROM analises WHERE FornecedorID = ? ORDER BY DataHora ASC",
                (forn_id,)
            )
            df_agend_bi = executar_query(
                "SELECT DataAgendada, Status, QuantidadeEsperada FROM agendamentos WHERE FornecedorCNPJ = ? ORDER BY DataAgendada ASC",
                (forn_cnpj,)
            )
        else:
            df_analises_bi = executar_query(
                "SELECT DataHora, Umidade, Insumo, StatusLote FROM analises ORDER BY DataHora ASC"
            )
            df_agend_bi = executar_query(
                "SELECT DataAgendada, Status, QuantidadeEsperada FROM agendamentos ORDER BY DataAgendada ASC"
            )
            
        if df_analises_bi.empty and df_agend_bi.empty:
            st.info("ℹ️ Dados insuficientes no histórico para gerar relatórios de Analytics neste momento.")
        else:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("**📈 Evolução da Umidade Média por Semana (%)**")
                if not df_analises_bi.empty:
                    df_analises_bi['DataHora'] = pd.to_datetime(df_analises_bi['DataHora'])
                    df_analises_bi['Semana_Date'] = df_analises_bi['DataHora'].apply(lambda x: (x - pd.Timedelta(days=x.weekday())).date())
                    df_chart_umidade = df_analises_bi.groupby(['Semana_Date', 'Insumo'])['Umidade'].mean().unstack(fill_value=12.0)
                    df_chart_umidade.index = pd.to_datetime(df_chart_umidade.index).strftime('%d/%m')
                    st.line_chart(df_chart_umidade)
                else:
                    st.caption("Sem dados de umidade para gerar gráficos.")
                    
            with col_chart2:
                st.markdown("**📊 Status de Qualidade dos Lotes**")
                if not df_analises_bi.empty:
                    df_chart_status = df_analises_bi['StatusLote'].value_counts()
                    st.bar_chart(df_chart_status)
                else:
                    st.caption("Sem dados de classificação regulatória de qualidade.")
            
            st.markdown("---")
            col_chart3, col_chart4 = st.columns([6, 4])
            
            with col_chart3:
                st.markdown("**📅 Programação de Entrega de Cargas por Semana (Kg)**")
                if not df_agend_bi.empty:
                    df_agend_bi['DataAgendada'] = pd.to_datetime(df_agend_bi['DataAgendada'])
                    df_agend_bi['Semana_Date'] = df_agend_bi['DataAgendada'].apply(lambda x: (x - pd.Timedelta(days=x.weekday())).date())
                    df_chart_vol = df_agend_bi.groupby('Semana_Date')['QuantidadeEsperada'].sum()
                    df_chart_vol.index = pd.to_datetime(df_chart_vol.index).strftime('%d/%m')
                    st.area_chart(df_chart_vol)
                else:
                    st.caption("Sem dados de agendamentos futuros.")
                    
            with col_chart4:
                st.markdown("**📋 Resumo Regulatório de Auditoria**")
                if not df_analises_bi.empty:
                    tot_lotes = len(df_analises_bi)
                    aprovados_lotes = len(df_analises_bi[df_analises_bi['StatusLote'] == 'Aprovado'])
                    quar_lotes = len(df_analises_bi[df_analises_bi['StatusLote'] == 'Quarentena'])
                    desvio_lotes = len(df_analises_bi[df_analises_bi['StatusLote'] == 'Aprovado com Desvio'])
                    tx_aprov = ((aprovados_lotes + desvio_lotes) / tot_lotes) * 100 if tot_lotes > 0 else 0
                    
                    tx_aprov_str = f"{tx_aprov:.1f}%".replace('.', ',')
                    st.write(f"- **Total de lotes analisados:** {tot_lotes} lotes")
                    st.write(f"- **Lotes conformes de primeira:** {aprovados_lotes}")
                    st.write(f"- **Lotes liberados sob desvio:** {desvio_lotes}")
                    st.write(f"- **Lotes atualmente retidos:** {quar_lotes}")
                    st.write(f"- **Taxa de conformidade geral:** {tx_aprov_str}")
                else:
                    st.write("Sem registros de auditoria regulatória.")


# Instanciando st.Page dos sub-arquivos
page_inicio = st.Page(show_inicio, title="Início", icon="🏠", default=True)
page_fornecedores = st.Page("pages/1_Cadastro de Fornecedores.py", title="Fornecedores", icon="📦")
page_motoristas = st.Page("pages/2_Motoristas e Veículos.py", title="Motoristas e Veículos", icon="🚗")
page_agendamento = st.Page("pages/3_Agendamento.py", title="Agendar Entrega", icon="📅")
page_janelas = st.Page("pages/4_Visualização de Janelas.py", title="Painel de Janelas", icon="👁️")
page_analise = st.Page("pages/5_Análise de Recebimento.py", title="Análise de Qualidade", icon="🧪")
page_pesagem = st.Page("pages/6_Controle de Pesagem.py", title="Pesagem (Balança)", icon="⚖️")
page_quarentena = st.Page("pages/7_Gestão de Quarentena.py", title="Gestão de Quarentena", icon="🛡️")
page_integracoes = st.Page("pages/8_Hub de Integrações.py", title="Hub de Integrações", icon="🔌")

# --- CONSTRUÇÃO DO ROTEADOR DINÂMICO BASEADO NO PERFIL ---
allowed_pages = [page_inicio]

if perfil == "Administrador":
    allowed_pages.extend([page_fornecedores, page_motoristas, page_agendamento, page_janelas, page_analise, page_pesagem, page_quarentena, page_integracoes])
elif perfil == "Portaria":
    allowed_pages.extend([page_motoristas, page_agendamento, page_janelas, page_pesagem])
elif perfil == "Laboratório":
    allowed_pages.extend([page_janelas, page_analise])
elif perfil == "Fornecedor":
    if st.session_state["fornecedor_logado_nome"] is None:
        # Se for nova empresa cadastrando, só exibe Cadastro de Fornecedor
        allowed_pages.extend([page_fornecedores])
    else:
        # Se já estiver logado como empresa existente, libera operações (incluindo Motoristas/Veículos para gerenciar sua frota)
        allowed_pages.extend([page_motoristas, page_agendamento, page_janelas])

# Execução do Roteador
pg = st.navigation(allowed_pages)
pg.run()