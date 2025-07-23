import streamlit as st
import pandas as pd
import sqlite3
import os # É uma boa prática importar todas as bibliotecas no início

# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
DB_NAME = "fornecedores.db"

def inicializar_banco():
    """
    Cria o banco de dados e a tabela 'fornecedores' se não existirem.
    A cláusula 'IF NOT EXISTS' é a chave para não apagar os dados.
    """
    # Usamos um 'try...finally' para garantir que a conexão seja sempre fechada.
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            NomeEmpresa TEXT NOT NULL,
            CNPJ TEXT PRIMARY KEY NOT NULL,
            Endereco TEXT,
            Email TEXT,
            Telefone TEXT
        );
        """)
        conn.commit()
    finally:
        conn.close()

# Chamamos a função de inicialização no início da execução do script
inicializar_banco()

def buscar_todos_fornecedores():
    """
    Busca todos os registros e retorna como um DataFrame pandas.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        query = "SELECT NomeEmpresa, CNPJ, Endereco, Email, Telefone FROM fornecedores"
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df

# --- Configuração da Página ---
st.title("📦 Cadastro de Fornecedores com Banco de Dados")
st.markdown("Preencha os dados abaixo para cadastrar um novo fornecedor no sistema.")

# --- Lógica de Limpeza (sem alterações) ---
campos = ["nome", "cnpj", "telefone", "endereco", "email"]
if 'limpeza_solicitada' not in st.session_state:
    st.session_state.limpeza_solicitada = False
def solicitar_limpeza():
    st.session_state.limpeza_solicitada = True
if st.session_state.limpeza_solicitada:
    for campo in campos:
        st.session_state[campo] = ""
    st.success("Campos limpos!")
    st.session_state.limpeza_solicitada = False
for campo in campos:
    if campo not in st.session_state:
        st.session_state[campo] = ""

# --- Formulário de Cadastro ---
with st.form("formulario_fornecedor", clear_on_submit=False):
    st.subheader("📝 Informações do Fornecedor")
    nome_empresa = st.text_input("Nome da empresa", key="nome")
    col1, col2 = st.columns(2)
    with col1:
        cnpj = st.text_input("CNPJ", key="cnpj")
    with col2:
        telefone_contato = st.text_input("Telefone de contato", key="telefone")
    endereco = st.text_input("Endereço", key="endereco")
    email_contato = st.text_input("Email de contato", key="email")

    submitted = st.form_submit_button("💾 Salvar")

    if submitted:
        # Validação de campos vazios
        if not all([nome_empresa, cnpj, endereco, email_contato, telefone_contato]):
            st.warning("Por favor, preencha todos os campos.")
        else:
            conn = sqlite3.connect(DB_NAME)
            try:
                cursor = conn.cursor()
                # Verifica se o CNPJ já existe
                cursor.execute("SELECT CNPJ FROM fornecedores WHERE CNPJ = ?", (cnpj,))
                if cursor.fetchone():
                    st.error("❌ Já existe um fornecedor cadastrado com esse CNPJ.")
                else:
                    # Se não existe, insere o novo fornecedor
                    cursor.execute("""
                    INSERT INTO fornecedores (NomeEmpresa, CNPJ, Endereco, Email, Telefone)
                    VALUES (?, ?, ?, ?, ?)
                    """, (nome_empresa, cnpj, endereco, email_contato, telefone_contato))
                    conn.commit()
                    st.success("✅ Fornecedor cadastrado com sucesso no banco de dados!")
                    solicitar_limpeza() # Solicita a limpeza dos campos do formulário
            except sqlite3.Error as e:
                st.error(f"Ocorreu um erro no banco de dados: {e}")
            finally:
                conn.close()

# Botão de Reset/Limpeza Manual
st.button("🧹 Limpar Dados / Resetar", on_click=solicitar_limpeza, help="Clique aqui para limpar todos os campos e começar de novo.")

# --- SEÇÃO DE VISUALIZAÇÃO E DIAGNÓSTICO ---
st.markdown("---")
st.subheader("📋 Fornecedores Cadastrados")

# Busca os dados mais recentes do banco
df_fornecedores = buscar_todos_fornecedores()

# Exibe na tela
if df_fornecedores.empty:
    st.info("Ainda não há fornecedores cadastrados no banco de dados.")
else:
    # Mostra o número de registros encontrados (nosso diagnóstico)
    st.info(f"**Encontrados {len(df_fornecedores)} fornecedores no banco de dados.**")
    st.dataframe(df_fornecedores)