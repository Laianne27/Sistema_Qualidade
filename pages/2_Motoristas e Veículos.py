import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURAÇÕES DO BANCO DE DADOS E INICIALIZAÇÃO ---
DB_NAME = "fornecedores.db"

def inicializar_banco_motoristas_veiculos():
    """
    Garante que as tabelas 'motoristas' e 'veiculos' existam com a estrutura correta.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabela de motoristas, com chave estrangeira para fornecedores
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

    # Tabela de veículos, com chave estrangeira para motoristas
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
def buscar_dados(tabela, colunas="*"):
    conn = sqlite3.connect(DB_NAME)
    try:
        query = f"SELECT {colunas} FROM {tabela}"
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

# Inicializa as tabelas ao carregar a página
inicializar_banco_motoristas_veiculos()

# --- INTERFACE DA PÁGINA ---
st.title("🚗 Gerenciamento de Motoristas e Veículos")

# 1. SELECIONAR O FORNECEDOR
st.header("1. Selecione o Fornecedor")
fornecedores_df = buscar_dados("fornecedores", "ID, NomeEmpresa")

if fornecedores_df.empty:
    st.error("Nenhum fornecedor cadastrado. Por favor, cadastre um fornecedor primeiro na página de Gerenciamento de Fornecedores.")
else:
    # Cria uma lista de nomes de fornecedores para o selectbox
    fornecedor_selecionado_nome = st.selectbox(
        "Fornecedor",
        options=fornecedores_df['NomeEmpresa'],
        index=None,
        placeholder="Escolha um fornecedor para gerenciar..."
    )

    # Se um fornecedor foi selecionado, continua a lógica
    if fornecedor_selecionado_nome:
        # Pega o ID do fornecedor selecionado
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
                            cursor.execute(
                                "INSERT INTO motoristas (Nome, CPF, Telefone, FornecedorID) VALUES (?, ?, ?, ?)",
                                (novo_nome, novo_cpf, novo_telefone, fornecedor_id)
                            )
                            conn.commit()
                            st.success(f"Motorista {novo_nome} cadastrado com sucesso!")
                        except sqlite3.IntegrityError:
                            st.error(f"Erro: O CPF '{novo_cpf}' já está cadastrado no sistema.")
                        finally:
                            conn.close()
                    else:
                        st.warning("Nome e CPF são obrigatórios.")

        # 3. LISTAR MOTORISTAS EXISTENTES E SEUS VEÍCULOS
        motoristas_df = buscar_dados(f"motoristas WHERE FornecedorID = {fornecedor_id}")

        if motoristas_df.empty:
            st.info("Este fornecedor ainda não possui motoristas cadastrados.")
        else:
            for index, motorista in motoristas_df.iterrows():
                st.subheader(f"Motorista: {motorista['Nome']}")
                st.write(f"**CPF:** {motorista['CPF']} | **Telefone:** {motorista['Telefone']}")

                with st.container(border=True):
                    # Lógica para veículos deste motorista
                    veiculos_df = buscar_dados(f"veiculos WHERE MotoristaID = {motorista['ID']}")

                    if not veiculos_df.empty:
                        st.write("**Veículos Cadastrados:**")
                        st.dataframe(veiculos_df[['Placa', 'Modelo', 'Tipo']], use_container_width=True)

                    # Formulário para adicionar novo veículo
                    with st.form(f"form_veiculo_{motorista['ID']}", clear_on_submit=True):
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
                                    cursor.execute(
                                        "INSERT INTO veiculos (Placa, Modelo, Tipo, MotoristaID) VALUES (?, ?, ?, ?)",
                                        (nova_placa.upper(), novo_modelo, novo_tipo, motorista['ID'])
                                    )
                                    conn.commit()
                                    st.success(f"Veículo de placa {nova_placa.upper()} adicionado!")
                                    st.rerun() # Recarrega a página para mostrar o novo veículo
                                except sqlite3.IntegrityError:
                                    st.error(f"Erro: A placa '{nova_placa.upper()}' já está cadastrada.")
                                finally:
                                    conn.close()
                            else:
                                st.warning("Placa e Modelo são obrigatórios.")