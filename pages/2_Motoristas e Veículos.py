import streamlit as st
import sqlite3
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

# Configuração da página e estilos globais
aplicar_tema("Motoristas e Veículos", "🚗")

st.title("🚗 Controle de Motoristas e Veículos")
st.markdown("Gerencie motoristas credenciados e frotas de transporte vinculadas aos seus fornecedores parceiros.")
st.markdown("---")

# Verifica perfil de acesso para restringir dados
perfil_ativo = st.session_state.get("role", "Administrador")

# Busca fornecedores disponíveis
if perfil_ativo == "Fornecedor":
    forn_cnpj = st.session_state.get("fornecedor_logado_cnpj")
    fornecedores_df = executar_query("SELECT ID, NomeEmpresa FROM fornecedores WHERE CNPJ = ?", (forn_cnpj,))
else:
    fornecedores_df = executar_query("SELECT ID, NomeEmpresa FROM fornecedores ORDER BY NomeEmpresa ASC")

if fornecedores_df.empty:
    if perfil_ativo == "Fornecedor":
        st.error("⚠️ Sua empresa não foi localizada no banco de dados. Por favor, realize o autocadastro primeiro.")
    else:
        st.error("⚠️ Nenhum fornecedor cadastrado no sistema. Por favor, cadastre um fornecedor antes de gerenciar frotas.")
else:
    # Criação das 3 abas estruturadas
    tab_painel, tab_motorista, tab_veiculo = st.tabs([
        "📋 Controle de Frotas", 
        "👤 Cadastrar Motorista", 
        "🚚 Cadastrar Veículo"
    ])
    
    # --- 1. ABA: PAINEL DE FROTAS ---
    with tab_painel:
        st.subheader("Visualização Hierárquica de Frotas")
        
        if perfil_ativo == "Fornecedor":
            fornecedor_selecionado = st.session_state.get("fornecedor_logado_nome")
            st.info(f"🏢 Empresa: **{fornecedor_selecionado}**")
        else:
            fornecedor_selecionado = st.selectbox(
                "Selecione o Fornecedor para Visualização",
                options=fornecedores_df['NomeEmpresa'],
                index=None,
                placeholder="Escolha um fornecedor comercial...",
                key="sb_painel_forn"
            )
        
        if fornecedor_selecionado:
            fornecedor_id = fornecedores_df[fornecedores_df['NomeEmpresa'] == fornecedor_selecionado]['ID'].iloc[0]
            
            # Busca todos os motoristas do fornecedor
            motoristas = executar_query(
                "SELECT ID, Nome, CPF, Telefone FROM motoristas WHERE FornecedorID = ? ORDER BY Nome ASC",
                (int(fornecedor_id),)
            )
            
            if motoristas.empty:
                st.info(f"O fornecedor **{fornecedor_selecionado}** ainda não possui nenhum motorista credenciado.")
            else:
                st.write(f"Credenciados para **{fornecedor_selecionado}** ({len(motoristas)} motoristas):")
                
                # Loop para exibir cada motorista em um card limpo
                for idx, row in motoristas.iterrows():
                    with st.container(border=True):
                        col_m1, col_m2, col_m3 = st.columns([3, 2, 2])
                        col_m1.markdown(f"👤 **Nome:** {row['Nome']}")
                        col_m2.write(f"📄 **CPF:** {row['CPF']}")
                        col_m3.write(f"📞 **Telefone:** {row['Telefone']}")
                        
                        # Busca veículos do motorista
                        veiculos = executar_query(
                            "SELECT Placa, Modelo, Tipo FROM veiculos WHERE MotoristaID = ? ORDER BY Placa ASC",
                            (int(row['ID']),)
                        )
                        
                        # Expander interno para gerenciar veículos
                        with st.expander(f"🚚 Ver Frota de Veículos ({len(veiculos)})", expanded=False):
                            if veiculos.empty:
                                st.caption("Nenhum veículo registrado para este motorista.")
                            else:
                                df_veic_show = veiculos.rename(columns={
                                    'Placa': 'Placa do Veículo',
                                    'Modelo': 'Modelo / Marca',
                                    'Tipo': 'Tipo de Veículo'
                                })
                                st.dataframe(df_veic_show, use_container_width=True, hide_index=True)
                                
    # --- 2. ABA: CADASTRAR MOTORISTA ---
    with tab_motorista:
        st.subheader("Cadastro de Novo Motorista")
        
        if perfil_ativo == "Fornecedor":
            fornecedor_mot = st.session_state.get("fornecedor_logado_nome")
            st.info(f"🏢 Vinculado à sua Empresa: **{fornecedor_mot}**")
        else:
            fornecedor_mot = st.selectbox(
                "Vincular ao Fornecedor",
                options=fornecedores_df['NomeEmpresa'],
                index=None,
                placeholder="Escolha o fornecedor contratante...",
                key="sb_mot_forn"
            )
        
        if fornecedor_mot:
            fornecedor_id_mot = fornecedores_df[fornecedores_df['NomeEmpresa'] == fornecedor_mot]['ID'].iloc[0]
            
            with st.form("form_cadastro_motorista", clear_on_submit=True):
                nome = st.text_input("Nome Completo do Motorista")
                cpf = st.text_input("CPF (somente números)")
                telefone = st.text_input("Telefone de Contato")
                
                submit_mot = st.form_submit_button("💾 Salvar Motorista")
                
                if submit_mot:
                    if not (nome and cpf):
                        st.warning("⚠️ Nome e CPF são campos obrigatórios.")
                    else:
                        try:
                            executar_dml(
                                "INSERT INTO motoristas (Nome, CPF, Telefone, FornecedorID) VALUES (?, ?, ?, ?)",
                                (nome, cpf, telefone, int(fornecedor_id_mot))
                            )
                            st.success(f"✅ Motorista **{nome}** credenciado com sucesso!")
                            st.toast("Motorista salvo no banco!", icon="👤")
                        except sqlite3.IntegrityError:
                            st.error(f"❌ Erro: O CPF '{cpf}' já está cadastrado no sistema.")
                        except sqlite3.Error as e:
                            st.error(f"Erro no banco de dados: {e}")
                            
    # --- 3. ABA: CADASTRAR VEÍCULO ---
    with tab_veiculo:
        st.subheader("Cadastro de Veículo de Transporte")
        
        if perfil_ativo == "Fornecedor":
            fornecedor_vei = st.session_state.get("fornecedor_logado_nome")
            st.info(f"🏢 Empresa: **{fornecedor_vei}**")
        else:
            fornecedor_vei = st.selectbox(
                "Selecione o Fornecedor do Motorista",
                options=fornecedores_df['NomeEmpresa'],
                index=None,
                placeholder="Escolha o fornecedor...",
                key="sb_vei_forn"
            )
        
        if fornecedor_vei:
            fornecedor_id_vei = fornecedores_df[fornecedores_df['NomeEmpresa'] == fornecedor_vei]['ID'].iloc[0]
            
            # Filtra motoristas ativos do fornecedor selecionado
            motoristas_vei = executar_query(
                "SELECT ID, Nome, CPF FROM motoristas WHERE FornecedorID = ? ORDER BY Nome ASC",
                (int(fornecedor_id_vei),)
            )
            
            if motoristas_vei.empty:
                st.info(f"O fornecedor **{fornecedor_vei}** não possui motoristas cadastrados. Credencie um motorista antes de registrar veículos.")
            else:
                # Formata exibição do motorista no selectbox
                motoristas_vei['display'] = motoristas_vei['Nome'] + ' (CPF: ' + motoristas_vei['CPF'] + ')'
                
                motorista_selecionado_display = st.selectbox(
                    "Selecione o Motorista Proprietário/Responsável",
                    options=motoristas_vei['display'],
                    index=None,
                    placeholder="Escolha o motorista..."
                )
                
                if motorista_selecionado_display:
                    motorista_id = motoristas_vei.loc[motoristas_vei['display'] == motorista_selecionado_display, 'ID'].iloc[0]
                    
                    with st.form("form_cadastro_veiculo", clear_on_submit=True):
                        col_v1, col_v2 = st.columns(2)
                        with col_v1:
                            placa = st.text_input("Placa do Veículo (Ex: AAA0A00 / AAA0000)")
                        with col_v2:
                            modelo = st.text_input("Modelo / Marca (Ex: Scania R450, Volvo FH)")
                            
                        tipo = st.selectbox(
                            "Tipo de Carroceria / Capacidade",
                            options=["Truck (Simples)", "Bitrem", "Carreta", "Rodotrem", "Vanderleia", "Outro"]
                        )
                        
                        submit_vei = st.form_submit_button("💾 Salvar Veículo")
                        
                        if submit_vei:
                            if not placa.strip():
                                st.warning("⚠️ A placa do veículo é obrigatória.")
                            else:
                                try:
                                    placa_formatada = placa.strip().upper()
                                    executar_dml(
                                        "INSERT INTO veiculos (Placa, Modelo, Tipo, MotoristaID) VALUES (?, ?, ?, ?)",
                                        (placa_formatada, modelo, tipo, int(motorista_id))
                                    )
                                    st.success(f"✅ Veículo de placa **{placa_formatada}** registrado com sucesso!")
                                    st.toast("Veículo salvo no banco!", icon="🚚")
                                except sqlite3.IntegrityError:
                                    st.error(f"❌ Erro: A placa '{placa_formatada}' já está registrada para outro motorista.")
                                except sqlite3.Error as e:
                                    st.error(f"Erro no banco de dados: {e}")