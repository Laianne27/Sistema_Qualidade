import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURAÇÕES DO BANCO DE DADOS E INICIALIZAÇÃO ---
DB_NAME = "fornecedores.db"

def inicializar_banco_motoristas_veiculos():
    """Garante que as tabelas 'motoristas' e 'veiculos' existam."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS motoristas (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT NOT NULL,
        CPF TEXT UNIQUE NOT NULL,
        Telefone TEXT,
        FornecedorID INTEGER NOT NULL,
        FOREIGN KEY (FornecedorID) REFERENCES fornecedores (ID)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS veiculos (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Placa TEXT UNIQUE NOT NULL,
        Modelo TEXT NOT NULL,
        Tipo TEXT,
        MotoristaID INTEGER NOT NULL,
        FOREIGN KEY (MotoristaID) REFERENCES motoristas (ID)
    );
    """)
    conn.commit()
    conn.close()

# Funções para interagir com o banco de dados
def buscar_dados(query):
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

# Inicializa as tabelas ao carregar a página
inicializar_banco_motoristas_veiculos()

# --- INTERFACE DA PÁGINA ---
st.title("🚗 Gerenciamento de Motoristas e Veículos")

if 'gerenciar_motorista_id' not in st.session_state:
    st.session_state.gerenciar_motorista_id = None

# 1. SELECIONAR O FORNECEDOR
st.header("1. Selecione o Fornecedor")
fornecedores_df = buscar_dados("SELECT ID, NomeEmpresa FROM fornecedores ORDER BY NomeEmpresa ASC")

if fornecedores_df.empty:
    st.error("Nenhum fornecedor cadastrado. Por favor, cadastre um fornecedor primeiro.")
else:
    fornecedor_selecionado_nome = st.selectbox(
        "Fornecedor",
        options=fornecedores_df['NomeEmpresa'],
        index=None,
        placeholder="Escolha um fornecedor para gerenciar..."
    )

    if fornecedor_selecionado_nome:
        fornecedor_id = fornecedores_df[fornecedores_df['NomeEmpresa'] == fornecedor_selecionado_nome]['ID'].iloc[0]

        st.markdown("---")
        st.header(f"2. Motoristas de: **{fornecedor_selecionado_nome}**")

        # 2. CADASTRAR NOVO MOTORISTA
        with st.expander("➕ Adicionar Novo Motorista"):
            with st.form("form_novo_motorista", clear_on_submit=True):
                novo_nome = st.text_input("Nome do Motorista")
                novo_cpf = st.text_input("CPF do Motorista")
                novo_telefone = st.text_input("Telefone do Motorista")
                submit_motorista = st.form_submit_button("Salvar Motorista")

                if submit_motorista:
                    if novo_nome and novo_cpf:
                        try:
                            conn = sqlite3.connect(DB_NAME)
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO motoristas (Nome, CPF, Telefone, FornecedorID) VALUES (?, ?, ?, ?)", (novo_nome, novo_cpf, novo_telefone, fornecedor_id))
                            conn.commit()
                            st.success(f"Motorista {novo_nome} cadastrado com sucesso!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error(f"Erro: O CPF '{novo_cpf}' já está cadastrado.")
                        finally:
                            conn.close()
                    else:
                        st.warning("Nome e CPF são obrigatórios.")

        # 3. LISTA DE MOTORISTAS
        st.subheader("Motoristas Cadastrados")
        motoristas_df = buscar_dados(f"SELECT ID, Nome, CPF, Telefone FROM motoristas WHERE FornecedorID = {fornecedor_id}")

        if motoristas_df.empty:
            st.info("Este fornecedor ainda não possui motoristas cadastrados.")
        else:
            col_header1, col_header2, col_header3, col_header4 = st.columns([3, 2, 2, 2])
            col_header1.markdown("**Nome**")
            col_header2.markdown("**CPF**")
            col_header3.markdown("**Telefone**")
            col_header4.markdown("**Ações**")

            for index, motorista in motoristas_df.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    col1.write(motorista['Nome'])
                    col2.write(motorista['CPF'])
                    col3.write(motorista['Telefone'])
                    if col4.button("Gerenciar Veículos", key=motorista['ID']):
                        st.session_state.gerenciar_motorista_id = motorista['ID']
                        st.rerun() # Adicionado para garantir o estado correto ao clicar

        # 4. SEÇÃO PARA GERENCIAR VEÍCULOS
        if st.session_state.gerenciar_motorista_id:
            # Filtra o DataFrame para encontrar o motorista selecionado
            motorista_filtrado_df = motoristas_df[motoristas_df['ID'] == st.session_state.gerenciar_motorista_id]

            # ===== A CORREÇÃO ESTÁ AQUI =====
            # Verificamos se a filtragem encontrou o motorista na lista ATUAL
            if not motorista_filtrado_df.empty:
                motorista_selecionado = motorista_filtrado_df.iloc[0]
                
                st.markdown("---")
                st.subheader(f"Gerenciando Veículos de: **{motorista_selecionado['Nome']}**")

                veiculos_df = buscar_dados(f"SELECT Placa, Modelo, Tipo FROM veiculos WHERE MotoristaID = {st.session_state.gerenciar_motorista_id}")
                if not veiculos_df.empty:
                    st.write("**Veículos Cadastrados:**")
                    st.dataframe(veiculos_df, use_container_width=True, hide_index=True)

                with st.form(f"form_veiculo_{st.session_state.gerenciar_motorista_id}", clear_on_submit=True):
                    st.write("**Adicionar Novo Veículo:**")
                    col1, col2, col3 = st.columns(3)
                    nova_placa = col1.text_input("Placa")
                    novo_modelo = col2.text_input("Modelo")
                    novo_tipo = col3.text_input("Tipo")
                    submit_veiculo = st.form_submit_button("Adicionar Veículo")

                    if submit_veiculo:
                        if nova_placa and novo_modelo:
                            try:
                                conn = sqlite3.connect(DB_NAME)
                                cursor = conn.cursor()
                                cursor.execute("INSERT INTO veiculos (Placa, Modelo, Tipo, MotoristaID) VALUES (?, ?, ?, ?)", (nova_placa.upper(), novo_modelo, novo_tipo, st.session_state.gerenciar_motorista_id))
                                conn.commit()
                                st.success(f"Veículo de placa {nova_placa.upper()} adicionado!")
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error(f"Erro: A placa '{nova_placa.upper()}' já está cadastrada.")
                            finally:
                                conn.close()
                        else:
                            st.warning("Placa e Modelo são obrigatórios.")
            else:
                # Se o motorista não foi encontrado na lista atual, limpamos o estado para evitar erros
                st.session_state.gerenciar_motorista_id = None