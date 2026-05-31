import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

# Configuração da página e design
aplicar_tema("Agendamento de Entregas", "📅")

def buscar_fornecedores_para_dropdown():
    """Busca o Nome e o CNPJ dos fornecedores para preencher o seletor."""
    query = "SELECT NomeEmpresa, CNPJ FROM fornecedores ORDER BY NomeEmpresa ASC"
    df = executar_query(query)
    if not df.empty:
        df['display'] = df['NomeEmpresa'] + ' (' + df['CNPJ'] + ')'
    return df

def buscar_agendamentos_da_data(data_busca):
    """Busca agendamentos existentes para uma data específica para monitoramento de slots."""
    query = """
        SELECT f.NomeEmpresa as Fornecedor, a.TipoInsumo as Insumo, 
               a.QuantidadeEsperada as 'Volume (Kg)', a.PlacaCaminhao as Placa, a.Status
        FROM agendamentos a
        JOIN fornecedores f ON a.FornecedorCNPJ = f.CNPJ
        WHERE a.DataAgendada = ?
        ORDER BY a.DataCadastro ASC
    """
    return executar_query(query, (data_busca,))

# --- INTERFACE DA PÁGINA ---
st.title("📅 Agendamento de Entregas")
st.markdown("Agende janelas de recebimento para o controle de fluxo na doca de descarga.")
st.markdown("---")

# Busca os fornecedores para o selectbox
fornecedores = buscar_fornecedores_para_dropdown()

if fornecedores.empty:
    st.error("⚠️ Nenhum fornecedor cadastrado. Por favor, cadastre um fornecedor antes de agendar.")
else:
    # Split Layout (Formulário na esquerda, Monitor/Preview na direita)
    col_form, col_preview = st.columns([5, 5])
    
    with col_form:
        st.subheader("📝 Solicitação de Janela")
        
        # Criação de campos controlados via Session State para preview em tempo real
        fornecedor_display = st.selectbox(
            "Selecione o Fornecedor *",
            options=fornecedores['display'],
            index=None,
            placeholder="Escolha o fornecedor...",
            key="agend_fornecedor"
        )
        
        tipo_insumo = st.text_input("Tipo de Insumo (Ex: Milho em Grão, Soja) *", key="agend_insumo")
        quantidade_esperada = st.number_input("Quantidade Esperada (em Kg) *", min_value=0.0, step=100.0, key="agend_qtd")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            placa_caminhao = st.text_input("Placa do Veículo *", key="agend_placa")
        with col_v2:
            nome_motorista = st.text_input("Nome do Motorista", key="agend_motorista")
            
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            nota_fiscal = st.text_input("Nota Fiscal (Chave Única) *", key="agend_nf")
        with col_d2:
            data_agendada = st.date_input("Data da Entrega *", value=None, key="agend_data")

        # Botão de envio fora do formulário nativo do Streamlit para poder capturar inputs em tempo real sem st.form
        # Usamos st.button normal para obter atualização instantânea no preview enquanto digita!
        # Se usássemos st.form, os inputs do preview só atualizariam ao clicar em submeter.
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.button("💾 Registrar Agendamento", type="primary")

        if submitted:
            if not all([fornecedor_display, tipo_insumo, quantidade_esperada > 0, placa_caminhao, nota_fiscal, data_agendada]):
                st.warning("⚠️ Preencha todos os campos obrigatórios (Quantidade deve ser > 0 e a Data deve ser selecionada).")
            else:
                # Recupera o CNPJ do fornecedor selecionado
                cnpj_selecionado = fornecedores.loc[fornecedores['display'] == fornecedor_display, 'CNPJ'].iloc[0]
                placa_formatada = placa_caminhao.strip().upper()
                data_formatada = data_agendada.strftime('%Y-%m-%d')

                try:
                    executar_dml("""
                    INSERT INTO agendamentos (FornecedorCNPJ, TipoInsumo, QuantidadeEsperada, PlacaCaminhao, NomeMotorista, NotaFiscal, DataAgendada, Status, DataCadastro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cnpj_selecionado,
                        tipo_insumo,
                        quantidade_esperada,
                        placa_formatada,
                        nome_motorista,
                        nota_fiscal,
                        data_formatada,
                        'Pendente',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    st.success(f"✅ Entrega de {tipo_insumo} agendada com sucesso para {data_agendada.strftime('%d/%m/%Y')}!")
                    # Limpa os campos recarregando a página
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(f"❌ Erro: A Nota Fiscal '{nota_fiscal}' já foi utilizada em outro agendamento.")
                except sqlite3.Error as e:
                    st.error(f"Erro no banco de dados: {e}")

    with col_preview:
        st.subheader("🎫 Preview do Ticket")
        
        # Formata dados do ticket em tempo real
        forn_nome = fornecedor_display.split(" (")[0] if fornecedor_display else "---"
        insumo_preview = tipo_insumo if tipo_insumo else "---"
        volume_preview = f"{quantidade_esperada:,.0f} Kg" if quantidade_esperada > 0 else "0 Kg"
        placa_preview = placa_caminhao.upper() if placa_caminhao else "---"
        motorista_preview = nome_motorista if nome_motorista else "---"
        nf_preview = nota_fiscal if nota_fiscal else "---"
        data_preview = data_agendada.strftime('%d/%m/%Y') if data_agendada else "---"
        
        # Renderização do ticket simulado
        ticket_html = f"""
        <div style="
            background-color: var(--st-secondary-background-color);
            border: 1px solid var(--st-secondary-background-color);
            border-radius: 12px;
            padding: 20px;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        ">
            <div style="text-align: center; border-bottom: 2px dashed rgba(128,128,128,0.2); padding-bottom: 12px; margin-bottom: 12px;">
                <h4 style="margin: 0; font-size: 16px; font-weight: 700; text-transform: uppercase;">Ticket de Entrada (Doca)</h4>
                <span style="font-size: 11px; opacity: 0.6;">AUTOGERAÇÃO QUALIHUB</span>
            </div>
            <div style="font-size: 13px; line-height: 1.6;">
                <div style="display: flex; justify-content: space-between;"><b>Fornecedor:</b> <span>{forn_nome}</span></div>
                <div style="display: flex; justify-content: space-between;"><b>Insumo:</b> <span>{insumo_preview}</span></div>
                <div style="display: flex; justify-content: space-between;"><b>Volume:</b> <span>{volume_preview}</span></div>
                <div style="display: flex; justify-content: space-between;"><b>Placa:</b> <span>{placa_preview}</span></div>
                <div style="display: flex; justify-content: space-between;"><b>Motorista:</b> <span>{motorista_preview}</span></div>
                <div style="display: flex; justify-content: space-between;"><b>Nota Fiscal:</b> <span>{nf_preview}</span></div>
                <div style="display: flex; justify-content: space-between;"><b>Previsão:</b> <span>{data_preview}</span></div>
            </div>
            <div style="text-align: center; border-top: 2px dashed rgba(128,128,128,0.2); padding-top: 12px; margin-top: 12px;">
                <span style="font-size: 12px; font-weight: 600; background-color: rgba(245, 158, 11, 0.15); color: #D97706; padding: 3px 8px; border-radius: 4px;">AGUARDANDO CHEGADA</span>
            </div>
        </div>
        """
        st.markdown(ticket_html, unsafe_allow_html=True)
        
        # --- Ocupação da Doca ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📅 Ocupação da Doca")
        
        if data_agendada:
            data_busca = data_agendada.strftime('%Y-%m-%d')
            agendamentos_dia = buscar_agendamentos_da_data(data_busca)
            
            if agendamentos_dia.empty:
                st.success(f"✅ Doca livre! Nenhuma entrega agendada para {data_agendada.strftime('%d/%m/%Y')}.")
            else:
                st.warning(f"⚠️ Atenção: Já existem **{len(agendamentos_dia)}** carga(s) agendada(s) para {data_agendada.strftime('%d/%m/%Y')}:")
                st.dataframe(agendamentos_dia, use_container_width=True, hide_index=True)
        else:
            st.caption("Selecione uma data no formulário para visualizar a ocupação da doca.")
