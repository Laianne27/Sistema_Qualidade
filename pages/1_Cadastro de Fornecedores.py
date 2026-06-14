import streamlit as st
import sqlite3
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

# Configuração da página e design tokens
aplicar_tema("Cadastro de Fornecedores", "📦")
perfil_ativo = st.session_state.get("role", "Administrador")

def buscar_fornecedores(termo_busca=""):
    """Busca fornecedores no banco de dados, aplicando filtro se termo_busca for fornecido."""
    if termo_busca.strip():
        query = """
            SELECT NomeEmpresa, CNPJ, Endereco, Email, Telefone 
            FROM fornecedores 
            WHERE NomeEmpresa LIKE ? OR CNPJ LIKE ?
            ORDER BY NomeEmpresa ASC
        """
        params = (f"%{termo_busca}%", f"%{termo_busca}%")
        return executar_query(query, params)
    else:
        query = "SELECT NomeEmpresa, CNPJ, Endereco, Email, Telefone FROM fornecedores ORDER BY NomeEmpresa ASC"
        return executar_query(query)

# --- Configuração da Página ---
st.title("📦 Cadastro de Fornecedores")
st.markdown("Gerenciamento centralizado de parceiros comerciais e auditoria de cadastros.")
st.markdown("---")

# --- Lógica de Limpeza de Campos ---
campos = ["nome", "cnpj", "telefone", "endereco", "email"]
if 'limpeza_solicitada' not in st.session_state:
    st.session_state.limpeza_solicitada = False

def solicitar_limpeza():
    st.session_state.limpeza_solicitada = True

if st.session_state.limpeza_solicitada:
    for campo in campos:
        st.session_state[campo] = ""
    st.session_state.limpeza_solicitada = False

for campo in campos:
    if campo not in st.session_state:
        st.session_state[campo] = ""

# --- Layout Split Screen (Formulário à esquerda, Lista à direita) ---
col_form, col_lista = st.columns([5, 7])

with col_form:
    st.subheader("📝 Novo Fornecedor")
    
    with st.form("formulario_fornecedor", clear_on_submit=False):
        st.markdown("Preencha os dados abaixo para registrar o fornecedor.")
        
        nome_empresa = st.text_input("Razão Social / Nome da Empresa", key="nome")
        cnpj = st.text_input("CNPJ (somente números)", key="cnpj")
        
        col_tel, col_email = st.columns(2)
        with col_tel:
            telefone_contato = st.text_input("Telefone", key="telefone")
        with col_email:
            email_contato = st.text_input("E-mail de Contato", key="email")
            
        endereco = st.text_input("Endereço Completo", key="endereco")

        submitted = st.form_submit_button("💾 Salvar Fornecedor")

        if submitted:
            # Validação de campos vazios
            if not all([nome_empresa, cnpj, endereco, email_contato, telefone_contato]):
                st.warning("⚠️ Por favor, preencha todos os campos obrigatórios.")
            else:
                try:
                    # Verifica se o CNPJ já existe
                    cnpj_existente = executar_query("SELECT CNPJ FROM fornecedores WHERE CNPJ = ?", (cnpj,))
                    if not cnpj_existente.empty:
                        st.error("❌ Já existe um fornecedor cadastrado com este CNPJ.")
                    else:
                        # Insere o novo fornecedor
                        executar_dml("""
                        INSERT INTO fornecedores (NomeEmpresa, CNPJ, Endereco, Email, Telefone)
                        VALUES (?, ?, ?, ?, ?)
                        """, (nome_empresa, cnpj, endereco, email_contato, telefone_contato))
                        
                        st.success("✅ Fornecedor cadastrado com sucesso!")
                        
                        # Se for perfil Fornecedor, faz login automático
                        if perfil_ativo == "Fornecedor":
                            st.session_state["fornecedor_cnpj_input"] = cnpj
                            st.session_state["fornecedor_logado_nome"] = nome_empresa
                            st.session_state["fornecedor_logado_cnpj"] = cnpj
                            
                        solicitar_limpeza()
                        st.rerun()
                except sqlite3.Error as e:
                    st.error(f"Erro no banco de dados: {e}")
                    
    # Botão de limpeza fora do formulário
    st.button("🧹 Limpar Campos", on_click=solicitar_limpeza, help="Limpa todos os campos digitados acima.")

with col_lista:
    # Se for perfil Fornecedor, oculta parceiros comerciais para privacidade
    if perfil_ativo == "Fornecedor":
        st.subheader("📋 Autocredenciamento")
        st.info(
            """
            Para começar a agendar suas entregas de grãos, primeiro realize o autocadastro 
            preenchendo a ficha ao lado com as informações da sua empresa.
            
            **Após clicar em Salvar:**
            1. Sua empresa será conectada automaticamente com o CNPJ cadastrado.
            2. A navegação será atualizada e os módulos operacionais (agendamentos, frotas e janelas) serão liberados para o seu perfil.
            """
        )
    else:
        st.subheader("📋 Parceiros Cadastrados")
        
        # Caixa de pesquisa dinâmica
        busca = st.text_input("🔍 Filtrar Fornecedores", placeholder="Pesquise por Nome ou CNPJ...")
        
        # Carrega dados
        df_fornecedores = buscar_fornecedores(busca)
        
        if df_fornecedores.empty:
            if busca:
                st.info("Nenhum fornecedor corresponde aos termos de pesquisa digitados.")
            else:
                st.info("Ainda não há fornecedores cadastrados no banco de dados.")
        else:
            st.info(f"Exibindo **{len(df_fornecedores)}** fornecedores.")
            
            # Renomeia colunas para exibição premium
            df_show = df_fornecedores.rename(columns={
                'NomeEmpresa': 'Empresa / Razão Social',
                'CNPJ': 'CNPJ',
                'Endereco': 'Endereço',
                'Email': 'E-mail',
                'Telefone': 'Telefone'
            })
            st.dataframe(df_show, use_container_width=True, hide_index=True)