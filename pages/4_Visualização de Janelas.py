import streamlit as st
from datetime import datetime, timedelta
from utils.db import executar_query
from utils.theme import aplicar_tema

# Configuração de Página e Estilo
aplicar_tema("Visualização de Janelas", "👁️")

st.title("👁️ Painel Operacional - Janelas de Entrega")
st.markdown("Acompanhamento visual da fila de cargas, agendamentos diários e planejamento semanal.")

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
        st.warning("Nenhum agendamento cadastrado no sistema. Vá para a página de agendamentos ou use o Seeder na Home.")
    else:
        # Métricas Globais no topo
        total_agendamentos = len(agendamentos_df)
        total_pendentes = len(agendamentos_df[agendamentos_df['Status'] == 'Pendente'])
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total de Entregas Agendadas", f"{total_agendamentos} cargas")
        with col_m2:
            st.metric("Aguardando Recebimento (Pendentes)", f"{total_pendentes} cargas")
            
        st.markdown("---")
        
        # Criação das Abas
        tab_diaria, tab_semanal = st.tabs(["📆 Visão Diária (Painel de Doca)", "📅 Programação Semanal"])
        
        # 1. ABA DIÁRIA
        with tab_diaria:
            st.subheader("Fila Operacional do Dia")
            
            # Seletor de data (padrão: hoje)
            dia_selecionado = st.date_input("Filtrar por data:", value=datetime.now().date())
            dia_str = dia_selecionado.strftime('%Y-%m-%d')
            
            # Filtra agendamentos para a data selecionada
            cargas_dia = agendamentos_df[agendamentos_df['DataAgendada'] == dia_str]
            
            if cargas_dia.empty:
                st.info(f"Nenhuma carga agendada para {dia_selecionado.strftime('%d/%m/%Y')} ({dia_da_semana_pt(dia_selecionado)}).")
            else:
                st.success(f"Encontrada(s) **{len(cargas_dia)}** carga(s) para este dia.")
                
                # Exibição de cards em colunas (3 por linha)
                cols_cards = st.columns(3)
                
                for idx, (_, row) in enumerate(cargas_dia.iterrows()):
                    col_card = cols_cards[idx % 3]
                    
                    # Cores para o status badge
                    if row['Status'] == "Pendente":
                        color_bg = "rgba(245, 158, 11, 0.15)"
                        color_text = "#D97706"
                    elif row['Status'] == "Aprovado":
                        color_bg = "rgba(16, 185, 129, 0.15)"
                        color_text = "#059669"
                    else:
                        color_bg = "rgba(239, 68, 68, 0.15)"
                        color_text = "#DC2626"
                        
                    with col_card:
                        card_html = f"""
                        <div style="
                            background-color: var(--st-secondary-background-color);
                            border: 1px solid var(--st-secondary-background-color);
                            border-radius: 14px;
                            padding: 22px;
                            margin-bottom: 20px;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
                            transition: all 0.3s ease;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <span style="font-weight: 700; color: var(--st-text-color); font-size: 16px;">🌾 {row['TipoInsumo']}</span>
                                <span style="
                                    background-color: {color_bg};
                                    color: {color_text};
                                    padding: 4px 10px;
                                    border-radius: 8px;
                                    font-size: 12px;
                                    font-weight: 600;
                                    text-transform: uppercase;
                                ">{row['Status']}</span>
                            </div>
                            <div style="font-size: 14px; color: var(--st-text-color); opacity: 0.8; margin-bottom: 6px;">🏢 <b>Fornecedor:</b> {row['NomeEmpresa']}</div>
                            <div style="font-size: 14px; color: var(--st-text-color); opacity: 0.8; margin-bottom: 6px;">🚚 <b>Placa:</b> {row['PlacaCaminhao']}</div>
                            <div style="font-size: 14px; color: var(--st-text-color); opacity: 0.8; margin-bottom: 6px;">👤 <b>Motorista:</b> {row['NomeMotorista']}</div>
                            <div style="font-size: 14px; color: var(--st-text-color); opacity: 0.8; margin-bottom: 12px;">📄 <b>NF:</b> {row['NotaFiscal']}</div>
                            <div style="
                                border-top: 1px dashed var(--st-text-color); 
                                opacity: 0.15;
                                margin-top: 10px;
                                margin-bottom: 10px;
                            "></div>
                            <div style="
                                font-size: 16px; 
                                color: var(--st-text-color); 
                                font-weight: 700;
                                display: flex;
                                justify-content: space-between;
                            ">
                                <span>Volume:</span>
                                <span>{row['QuantidadeEsperada']:,} Kg</span>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
        # 2. ABA SEMANAL
        with tab_semanal:
            st.subheader("Calendário de Entregas da Semana")
            st.markdown("Agrupamento das cargas programadas para os próximos 7 dias.")
            
            hoje_date = datetime.now().date()
            
            # Loop pelos próximos 7 dias
            for i in range(7):
                dia_futuro = hoje_date + timedelta(days=i)
                dia_futuro_str = dia_futuro.strftime('%Y-%m-%d')
                
                # Filtra agendamentos do dia futuro
                cargas_do_dia = agendamentos_df[agendamentos_df['DataAgendada'] == dia_futuro_str]
                total_cargas = len(cargas_do_dia)
                
                # Nome do cabeçalho do expander
                dia_semana_str = dia_da_semana_pt(dia_futuro)
                data_formatada_br = dia_futuro.strftime('%d/%m/%Y')
                
                expander_label = f"📅 {dia_semana_str} ({data_formatada_br}) — {total_cargas} carga(s)"
                
                with st.expander(expander_label, expanded=(i == 0)):
                    if cargas_do_dia.empty:
                        st.write("*Nenhuma carga planejada para esta data.*")
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
