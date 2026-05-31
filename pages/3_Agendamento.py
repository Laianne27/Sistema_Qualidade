import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

aplicar_tema("Agendamento de Entregas", "📅")

def buscar_fornecedores_para_dropdown():
    """Busca o Nome e o CNPJ dos fornecedores para preencher o seletor."""
    query = "SELECT NomeEmpresa, CNPJ FROM fornecedores ORDER BY NomeEmpresa ASC"
    df = executar_query(query)
    if not df.empty:
        # Cria uma coluna formatada para exibição no dropdown
        df['display'] = df['NomeEmpresa'] + ' (' + df['CNPJ'] + ')'
    return df

# --- INTERFACE DA PÁGINA ---
st.title("📅 Agendamento de Entregas")
st.markdown("Preencha os dados abaixo para agendar um novo recebimento.")

# Busca os fornecedores para o selectbox
fornecedores = buscar_fornecedores_para_dropdown()

if fornecedores.empty:
    st.error("Nenhum fornecedor cadastrado. Por favor, cadastre um fornecedor antes de agendar.")
else:
    with st.form("formulario_agendamento", clear_on_submit=True):
        st.subheader("Dados do Agendamento")

        # Dropdown para selecionar o fornecedor
        fornecedor_display = st.selectbox(
            "Selecione o Fornecedor",
            options=fornecedores['display'],
            index=None,
            placeholder="Escolha um fornecedor..."
        )

        # Inputs do formulário
        tipo_insumo = st.text_input("Tipo de Insumo (Ex: Milho, Soja)")
        quantidade_esperada = st.number_input("Quantidade Esperada (em Kg)", min_value=0.0, step=100.0)
        placa_caminhao = st.text_input("Placa do Veículo")
        nome_motorista = st.text_input("Nome do Motorista")
        nota_fiscal = st.text_input("Número da Nota Fiscal")
        data_agendada = st.date_input("Data da Entrega", value=None)

        submitted = st.form_submit_button("Agendar Entrega")

        if submitted:
            if not all([fornecedor_display, tipo_insumo, quantidade_esperada > 0, placa_caminhao, nota_fiscal, data_agendada]):
                st.warning("Por favor, preencha todos os campos obrigatórios (Quantidade deve ser maior que 0 e a Data deve ser selecionada).")
            else:
                # Recupera o CNPJ do fornecedor selecionado
                cnpj_selecionado = fornecedores.loc[fornecedores['display'] == fornecedor_display, 'CNPJ'].iloc[0]

                try:
                    # Lógica para salvar no banco
                    executar_dml("""
                    INSERT INTO agendamentos (FornecedorCNPJ, TipoInsumo, QuantidadeEsperada, PlacaCaminhao, NomeMotorista, NotaFiscal, DataAgendada, Status, DataCadastro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cnpj_selecionado,
                        tipo_insumo,
                        quantidade_esperada,
                        placa_caminhao.upper(),
                        nome_motorista,
                        nota_fiscal,
                        data_agendada.strftime('%Y-%m-%d'),
                        'Pendente',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    st.success(f"Entrega de {tipo_insumo} agendada com sucesso para {data_agendada.strftime('%d/%m/%Y')}!")
                except sqlite3.IntegrityError:
                    st.error(f"Erro: A Nota Fiscal '{nota_fiscal}' já foi utilizada em outro agendamento.")
                except sqlite3.Error as e:
                    st.error(f"Erro no banco de dados: {e}")
