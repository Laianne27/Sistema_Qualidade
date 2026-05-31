import streamlit as st
import sqlite3
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

aplicar_tema("Cadastro de Fornecedores", "📦")

def buscar_todos_fornecedores():
    """Busca todos os registros de fornecedores e retorna como um DataFrame pandas."""
    query = "SELECT NomeEmpresa, CNPJ, Endereco, Email, Telefone FROM fornecedores"
    return executar_query(query)

# --- Configuração da Página ---
st.title("📦 Cadastro de Fornecedores")
st.markdown("Preencha os dados abaixo para cadastrar um novo fornecedor no sistema.")

# --- Lógica de Limpeza de Campos ---
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
            try:
                # Verifica se o CNPJ já existe
                cnpj_existente = executar_query("SELECT CNPJ FROM fornecedores WHERE CNPJ = ?", (cnpj,))
                if not cnpj_existente.empty:
                    st.error("❌ Já existe um fornecedor cadastrado com esse CNPJ.")
                else:
                    # Insere o novo fornecedor
                    executar_dml("""
                    INSERT INTO fornecedores (NomeEmpresa, CNPJ, Endereco, Email, Telefone)
                    VALUES (?, ?, ?, ?, ?)
                    """, (nome_empresa, cnpj, endereco, email_contato, telefone_contato))
                    
                    st.success("✅ Fornecedor cadastrado com sucesso!")
                    solicitar_limpeza()
                    st.rerun()
            except sqlite3.Error as e:
                st.error(f"Ocorreu um erro no banco de dados: {e}")

# Botão de Reset/Limpeza Manual
st.button("🧹 Limpar Dados / Resetar", on_click=solicitar_limpeza, help="Clique aqui para limpar todos os campos e começar de novo.")

# --- SEÇÃO DE VISUALIZAÇÃO E DIAGNÓSTICO ---
st.markdown("---")
st.subheader("📋 Fornecedores Cadastrados")

df_fornecedores = buscar_todos_fornecedores()

if df_fornecedores.empty:
    st.info("Ainda não há fornecedores cadastrados no banco de dados.")
else:
    st.info(f"**Encontrados {len(df_fornecedores)} fornecedores no banco de dados.**")
    st.dataframe(df_fornecedores, use_container_width=True)