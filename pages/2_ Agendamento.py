# Sistema de Qualidade/pages/2_ Agendamento.py

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
DB_NAME = "fornecedores.db"

def inicializar_banco_agendamento():
    """
    Garante que a tabela 'agendamentos' exista, usando a estrutura planejada.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabela de agendamentos, com chave estrangeira para fornecedores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        FornecedorCNPJ TEXT NOT NULL,
        TipoInsumo TEXT NOT NULL,
        QuantidadeEsperada REAL NOT NULL,
        PlacaCaminhao TEXT NOT NULL,
        NomeMotorista TEXT,
        NotaFiscal TEXT UNIQUE,
        DataAgendada TEXT NOT NULL,
        Status TEXT NOT NULL,
        DataCadastro TEXT NOT NULL,
        FOREIGN KEY (FornecedorCNPJ) REFERENCES fornecedores (CNPJ)
    );
    """)
    conn.commit()
    conn.close()

def buscar_fornecedores_para_dropdown():
    """
    Busca o Nome e o CNPJ dos fornecedores para preencher um seletor.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        query = "SELECT NomeEmpresa, CNPJ FROM fornecedores ORDER BY NomeEmpresa ASC"
        df = pd.read_sql_query(query, conn)
        # Cria uma coluna formatada para exibição no dropdown
        df['display'] = df['NomeEmpresa'] + ' (' + df['CNPJ'] + ')'
        return df[['display', 'CNPJ']]
    finally:
        conn.close()


# Inicializa a tabela ao carregar a página
inicializar_banco_agendamento()

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
        data_agendada = st.date_input("Data da Entrega")

        submitted = st.form_submit_button("Agendar Entrega")

        if submitted:
            if not all([fornecedor_display, tipo_insumo, quantidade_esperada, placa_caminhao, nota_fiscal]):
                st.warning("Por favor, preencha todos os campos obrigatórios.")
            else:
                # Recupera o CNPJ do fornecedor selecionado
                cnpj_selecionado = fornecedores.loc[fornecedores['display'] == fornecedor_display, 'CNPJ'].iloc[0]

                # Lógica para salvar no banco
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                    INSERT INTO agendamentos (FornecedorCNPJ, TipoInsumo, QuantidadeEsperada, PlacaCaminhao, NomeMotorista, NotaFiscal, DataAgendada, Status, DataCadastro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cnpj_selecionado,
                        tipo_insumo,
                        quantidade_esperada,
                        placa_caminhao,
                        nome_motorista,
                        nota_fiscal,
                        data_agendada.strftime('%Y-%m-%d'),
                        'Pendente',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    conn.commit()
                    st.success(f"Entrega de {tipo_insumo} agendada com sucesso para {data_agendada.strftime('%d/%m/%Y')}!")
                except sqlite3.IntegrityError:
                    st.error(f"Erro: A Nota Fiscal '{nota_fiscal}' já foi utilizada em outro agendamento.")
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado: {e}")
                finally:
                    conn.close()