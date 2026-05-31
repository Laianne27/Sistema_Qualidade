import streamlit as st
from datetime import datetime, timedelta
from utils.db import executar_query
from utils.theme import aplicar_tema

# Configuração de Página e Estilo
aplicar_tema("Visualização de Janelas", "👁️")

st.title("👁️ Painel Operacional - Janelas de Entrega")
st.markdown("Monitoramento em tempo real do fluxo de docas, agendamentos diários e planejamento logístico semanal.")
st.markdown("---")

# Função para formatar dia da semana em português
def dia_da_semana_pt(date_obj):
    dias = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo"
    }
    return dias[date_obj.weekday()]

# Buscar agendamentos do banco de dados
try:
    agendamentos_df = executar_query("""
        SELECT a.ID, f.NomeEmpresa, a.TipoInsumo, a.QuantidadeEsperada, a.PlacaCaminhao, a.NomeMotorista, a.NotaFiscal, a.DataAgendada, a.Status 
        FROM agendamentos a
        JOIN fornecedores f ON a.FornecedorCNPJ = f.CNPJ
        ORDER BY a.DataAgendada ASC, a.ID ASC
    """)
    
    if agendamentos_df.empty:
        st.warning("⚠️ Nenhum agendamento cadastrado no sistema. Vá para a página de agendamentos ou use o Seeder na Home para popular dados fictícios.")
    else:
        # Métricas Globais da Operação no topo
        total_agendamentos = len(agendamentos_df)
        total_pendentes = len(agendamentos_df[agendamentos_df['Status'] == 'Pendente'])
        total_aprovados = len(agendamentos_df[agendamentos_df['Status'] == 'Aprovado'])
        total_recusados = len(agendamentos_df[agendamentos_df['Status'] == 'Recusado'])
        
        col_glob1, col_glob2, col_glob3, col_glob4 = st.columns(4)
        with col_glob1:
            st.metric("Total Planejado", f"{total_agendamentos} cargas")
        with col_glob2:
            st.metric("Aguardando Chegada", f"{total_pendentes} cargas")
        with col_glob3:
            st.metric("Descargas Concluídas", f"{total_aprovados} cargas")
        with col_glob4:
            st.metric("Cargas Recusadas", f"{total_recusados} cargas")
            
        st.markdown("---")
        
        # Criação das Abas
        tab_diaria, tab_semanal = st.tabs(["📆 Painel de Portaria (Diário)", "📅 Calendário Semanal"])
        
        # 1. ABA DIÁRIA
        with tab_diaria:
            st.subheader("Fila Operacional de Doca")
            
            # Seletor de data (padrão: hoje)
            dia_selecionado = st.date_input("Selecione a Data Operacional:", value=datetime.now().date())
            dia_str = dia_selecionado.strftime('%Y-%m-%d')
            
            # Filtra agendamentos para a data selecionada
            cargas_dia = agendamentos_df[agendamentos_df['DataAgendada'] == dia_str]
            
            if cargas_dia.empty:
                st.info(f"ℹ️ Nenhuma carga agendada para {dia_selecionado.strftime('%d/%m/%Y')} ({dia_da_semana_pt(dia_selecionado)}).")
            else:
                # Métricas do Dia Selecionado
                dia_total = len(cargas_dia)
                dia_volume = cargas_dia['QuantidadeEsperada'].sum()
                dia_pendentes = len(cargas_dia[cargas_dia['Status'] == 'Pendente'])
                dia_concluidas = len(cargas_dia[cargas_dia['Status'] == 'Aprovado'])
                
                col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                with col_d1:
                    st.metric("Cargas Programadas", f"{dia_total} caminhões")
                with col_d2:
                    st.metric("Volume Previsto", f"{dia_volume:,.0f} Kg")
                with col_d3:
                    st.metric("Aguardando Triagem", f"{dia_pendentes} cargas")
                with col_d4:
                    st.metric("Finalizadas", f"{dia_concluidas} cargas")
                
                st.markdown("---")
                
                # Exibição de cards em colunas (3 por linha)
                cols_cards = st.columns(3)
                
                for idx, (_, row) in enumerate(cargas_dia.iterrows()):
                    col_card = cols_cards[idx % 3]
                    
                    with col_card:
                        with st.container(border=True):
                            # Status Badge HTML
                            if row['Status'] == "Pendente":
                                badge_html = '<span style="background-color: rgba(245, 158, 11, 0.15); color: #D97706; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 600; text-transform: uppercase;">Pendente</span>'
                            elif row['Status'] == "Aprovado":
                                badge_html = '<span style="background-color: rgba(16, 185, 129, 0.15); color: #059669; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 600; text-transform: uppercase;">Aprovado</span>'
                            else:
                                badge_html = '<span style="background-color: rgba(239, 68, 68, 0.15); color: #DC2626; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 600; text-transform: uppercase;">Recusado</span>'
                                
                            header_html = f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <span style="font-weight: 700; font-size: 16px;">🌾 {row['TipoInsumo']}</span>
                                {badge_html}
                            </div>
                            """
                            st.markdown(header_html, unsafe_allow_html=True)
                            
                            st.markdown(f"🏢 **Fornecedor:** {row['NomeEmpresa']}")
                            st.markdown(f"🚚 **Placa:** {row['PlacaCaminhao']}")
                            st.markdown(f"👤 **Motorista:** {row['NomeMotorista']}")
                            st.markdown(f"📄 **NF:** {row['NotaFiscal']}")
                            
                            st.divider()
                            
                            footer_html = f"""
                            <div style="display: flex; justify-content: space-between; font-size: 16px; font-weight: 700;">
                                <span>Volume:</span>
                                <span>{row['QuantidadeEsperada']:,} Kg</span>
                            </div>
                            """
                            st.markdown(footer_html, unsafe_allow_html=True)
                        
        # 2. ABA SEMANAL
        with tab_semanal:
            st.subheader("Programação Semanal de Entregas")
            st.markdown("Agrupamento das cargas planejadas para os próximos 7 dias.")
            
            hoje_date = datetime.now().date()
            
            # Loop pelos próximos 7 dias
            for i in range(7):
                dia_futuro = hoje_date + timedelta(days=i)
                dia_futuro_str = dia_futuro.strftime('%Y-%m-%d')
                
                # Filtra agendamentos do dia futuro
                cargas_do_dia = agendamentos_df[agendamentos_df['DataAgendada'] == dia_futuro_str]
                total_cargas = len(cargas_do_dia)
                volume_total = cargas_do_dia['QuantidadeEsperada'].sum() if total_cargas > 0 else 0
                
                # Nome do cabeçalho do expander
                dia_semana_str = dia_da_semana_pt(dia_futuro)
                data_formatada_br = dia_futuro.strftime('%d/%m/%Y')
                
                # Se for hoje, adiciona uma tag
                tag_hoje = " (HOJE)" if i == 0 else ""
                
                expander_label = f"📅 {dia_semana_str} ({data_formatada_br}){tag_hoje} — {total_cargas} carga(s) | Volume Total: {volume_total:,.0f} Kg"
                
                with st.expander(expander_label, expanded=(i == 0)):
                    if cargas_do_dia.empty:
                        st.write("*Nenhuma entrega agendada para esta data.*")
                    else:
                        # Exibe em formato de tabela minimalista dentro do expander
                        cargas_show = cargas_do_dia[['NomeEmpresa', 'TipoInsumo', 'QuantidadeEsperada', 'PlacaCaminhao', 'NomeMotorista', 'NotaFiscal', 'Status']].rename(columns={
                            'NomeEmpresa': 'Fornecedor',
                            'TipoInsumo': 'Insumo',
                            'QuantidadeEsperada': 'Volume (Kg)',
                            'PlacaCaminhao': 'Placa',
                            'NomeMotorista': 'Motorista',
                            'NotaFiscal': 'Nota Fiscal',
                            'Status': 'Status'
                        })
                        st.dataframe(cargas_show, use_container_width=True, hide_index=True)
                        
except Exception as e:
    st.error(f"Erro ao carregar painel de janelas: {e}")
