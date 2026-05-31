import streamlit as st
import sqlite3
from datetime import datetime
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

# Configuração de Página e Estilos Globais
aplicar_tema("Análise de Recebimento", "🧪")

st.title("🧪 Análise de Recebimento de Insumos")
st.markdown("Módulo do Chão de Fábrica para controle de qualidade e classificação automática de grãos e derivados.")

# 1. BUSCAR FORNECEDORES DO BANCO DE DADOS
fornecedores_df = executar_query("SELECT ID, NomeEmpresa FROM fornecedores ORDER BY NomeEmpresa ASC")

# Insumos disponíveis (com Milho Comum renomeado para Milho em Grão)
LISTA_INSUMOS = [
    "Milho em Grão",
    "Milho Pipoca",
    "Soja",
    "Trigo",
    "Farinha de Trigo",
    "Farinha de Milho"
]

if fornecedores_df.empty:
    st.error("⚠️ Nenhum fornecedor cadastrado. Cadastre um fornecedor antes de iniciar a análise de recebimento.")
else:
    # Divide a tela em duas colunas: Formulário na esquerda e Painel de Avaliação na direita
    col_form, col_hist = st.columns([5, 7])

    with col_form:
        st.subheader("📝 Laudo de Entrada")
        
        with st.form("form_analise", clear_on_submit=False):
            # Identificação
            analista = st.text_input("Identificação do Analista (Nome / Matrícula)")
            
            # Fornecedor
            fornecedor_selecionado = st.selectbox(
                "Selecione o Fornecedor",
                options=fornecedores_df['NomeEmpresa'],
                index=None,
                placeholder="Escolha o fornecedor..."
            )
            
            # Seletor do Insumo
            insumo_selecionado = st.selectbox(
                "Selecione o Insumo Recebido",
                options=LISTA_INSUMOS,
                index=0
            )
            
            col_nf, col_lote = st.columns(2)
            with col_nf:
                nota_fiscal = st.text_input("Número da Nota Fiscal")
            with col_lote:
                lote = st.text_input("Lote do Fornecedor")
                
            st.markdown("---")
            st.write(f"**📊 Parâmetros Físico-Químicos para: {insumo_selecionado}**")
            
            # Inicializando variáveis dos parâmetros como None
            umidade = 0.0
            pureza = None
            aflatoxina = None
            capacidade_expansao = None
            peso_hectolitrico = None
            teor_cinzas = None
            teor_ferro = None
            
            # Exibição Condicional de Campos
            umidade = st.number_input(
                "Umidade (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
                help="Teor de umidade atual do insumo."
            )
            
            if insumo_selecionado == "Milho em Grão":
                pureza = st.number_input("Pureza (%)", min_value=0.0, max_value=100.0, value=100.0, step=0.1, format="%.1f", help="IN 60/2011 MAPA (Mínimo: 98%)")
                aflatoxina = st.number_input("Aflatoxina (ppb)", min_value=0.0, step=0.1, format="%.1f", help="RDC 722/2022 ANVISA (Máximo: 20.0 ppb)")
                
            elif insumo_selecionado == "Milho Pipoca":
                capacidade_expansao = st.number_input("Capacidade de Expansão (ml/g)", min_value=0.0, step=0.1, format="%.1f", help="IN 61/2011 MAPA (Mínimo: 30.0 ml/g)")
                aflatoxina = st.number_input("Aflatoxina (ppb)", min_value=0.0, step=0.1, format="%.1f", help="RDC 722/2022 ANVISA (Máximo: 20.0 ppb)")
                
            elif insumo_selecionado == "Soja":
                pureza = st.number_input("Pureza (%)", min_value=0.0, max_value=100.0, value=100.0, step=0.1, format="%.1f", help="IN 11/2007 MAPA (Mínimo: 99.0%)")
                
            elif insumo_selecionado == "Trigo":
                peso_hectolitrico = st.number_input("Peso Hectolítrico - PH (kg/hl)", min_value=0.0, max_value=120.0, value=78.0, step=0.1, format="%.1f", help="IN 38/2010 MAPA (Mínimo tipo 2: 75.0)")
                
            elif insumo_selecionado == "Farinha de Trigo":
                teor_cinzas = st.number_input("Teor de Cinzas (%)", min_value=0.0, max_value=10.0, step=0.01, format="%.2f", help="IN 8/2005 MAPA (Máximo tipo 1: 0.8%)")
                teor_ferro = st.number_input("Teor de Ferro (mg/100g)", min_value=0.0, step=0.1, format="%.1f", help="Enriquecimento RDC 150/2017 ANVISA (Faixa: 4.0 - 9.0 mg/100g)")
                
            elif insumo_selecionado == "Farinha de Milho":
                teor_ferro = st.number_input("Teor de Ferro (mg/100g)", min_value=0.0, step=0.1, format="%.1f", help="Enriquecimento RDC 150/2017 ANVISA (Faixa: 4.0 - 9.0 mg/100g)")

            submit_analise = st.form_submit_button("⚡ Rodar Análise e Salvar")

            if submit_analise:
                if not all([analista, fornecedor_selecionado, nota_fiscal, lote]):
                    st.warning("⚠️ Todos os campos de identificação (Analista, Fornecedor, Nota Fiscal, Lote) devem ser preenchidos.")
                else:
                    # Obter ID do fornecedor
                    fornecedor_id = fornecedores_df[fornecedores_df['NomeEmpresa'] == fornecedor_selecionado]['ID'].iloc[0]
                    
                    status_params = {}
                    
                    # --- MOTOR DE DECISÃO SEGUNDO LEGISLAÇÃO ---
                    
                    # A. Regra Geral de Umidade
                    if insumo_selecionado == "Milho em Grão" or insumo_selecionado == "Soja" or insumo_selecionado == "Farinha de Milho":
                        if umidade <= 14.0:
                            status_params["Umidade"] = ("Aprovado", "Dentro do limite padrão MAPA (<= 14.0%)")
                        elif umidade <= 15.0:
                            status_params["Umidade"] = ("Aprovado com Restrição", "Acima do padrão comercial, tolerado até 15.0%")
                        else:
                            status_params["Umidade"] = ("Reprovado", "Excedeu limite crítico (> 15.0%)")
                            
                    elif insumo_selecionado == "Milho Pipoca":
                        if 13.5 <= umidade <= 14.5:
                            status_params["Umidade"] = ("Aprovado", "Faixa perfeita para estouro (13.5% - 14.5%)")
                        else:
                            status_params["Umidade"] = ("Reprovado", "Fora da faixa de estouro (Gera piruá)")
                            
                    elif insumo_selecionado == "Trigo":
                        if umidade <= 13.0:
                            status_params["Umidade"] = ("Aprovado", "Dentro do limite regulamentado (<= 13.0%)")
                        elif umidade <= 14.0:
                            status_params["Umidade"] = ("Aprovado com Restrição", "Tolerável para moagem rápida (<= 14.0%)")
                        else:
                            status_params["Umidade"] = ("Reprovado", "Risco de deterioração (> 14.0%)")
                            
                    elif insumo_selecionado == "Farinha de Trigo":
                        if umidade <= 15.0:
                            status_params["Umidade"] = ("Aprovado", "Dentro da IN 8/2005 (<= 15.0%)")
                        else:
                            status_params["Umidade"] = ("Reprovado", "Farinha úmida (> 15.0%)")

                    # B. Regras Específicas
                    # 1. Milho em Grão
                    if insumo_selecionado == "Milho em Grão":
                        status_params["Pureza"] = ("Aprovado" if pureza >= 98.0 else ("Aprovado com Restrição" if pureza >= 97.0 else "Reprovado"), f"Pureza medida: {pureza}%")
                        status_params["Aflatoxina"] = ("Aprovado" if aflatoxina <= 20.0 else "Reprovado", f"Toxina: {aflatoxina} ppb (LMT: 20 ppb)")
                        
                    # 2. Milho Pipoca
                    elif insumo_selecionado == "Milho Pipoca":
                        status_params["Expansão"] = ("Aprovado" if capacidade_expansao >= 35.0 else ("Aprovado com Restrição" if capacidade_expansao >= 30.0 else "Reprovado"), f"Expansão: {capacidade_expansao} ml/g")
                        status_params["Aflatoxina"] = ("Aprovado" if aflatoxina <= 20.0 else "Reprovado", f"Toxina: {aflatoxina} ppb")
                        
                    # 3. Soja
                    elif insumo_selecionado == "Soja":
                        status_params["Pureza"] = ("Aprovado" if pureza >= 99.0 else ("Aprovado com Restrição" if pureza >= 98.0 else "Reprovado"), f"Pureza Soja: {pureza}%")
                        
                    # 4. Trigo
                    elif insumo_selecionado == "Trigo":
                        status_params["Peso Hectolítrico (PH)"] = ("Aprovado" if peso_hectolitrico >= 78.0 else ("Aprovado com Restrição" if peso_hectolitrico >= 75.0 else "Reprovado"), f"PH trigo: {peso_hectolitrico} kg/hl")
                        
                    # 5. Farinha de Trigo
                    elif insumo_selecionado == "Farinha de Trigo":
                        status_params["Teor de Cinzas"] = ("Aprovado" if teor_cinzas <= 0.8 else ("Aprovado com Restrição" if teor_cinzas <= 1.0 else "Reprovado"), f"Cinzas: {teor_cinzas}%")
                        status_params["Teor de Ferro"] = ("Aprovado" if 4.0 <= teor_ferro <= 9.0 else "Reprovado", f"Ferro: {teor_ferro} mg/100g")
                        
                    # 6. Farinha de Milho
                    elif insumo_selecionado == "Farinha de Milho":
                        status_params["Teor de Ferro"] = ("Aprovado" if 4.0 <= teor_ferro <= 9.0 else "Reprovado", f"Ferro: {teor_ferro} mg/100g")
                        
                    # Decisão Final do Lote
                    lista_decisoes = [v[0] for v in status_params.values()]
                    if "Reprovado" in lista_decisoes:
                        status_final = "Reprovado"
                    elif "Aprovado com Restrição" in lista_decisoes:
                        status_final = "Aprovado com Restrição"
                    else:
                        status_final = "Aprovado"
                        
                    # Salvar no Banco de Dados
                    try:
                        data_hora_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        executar_dml("""
                            INSERT INTO analises (FornecedorID, Insumo, NotaFiscal, LoteFornecedor, Umidade, Pureza, Aflatoxina, CapacidadeExpansao, PesoHectolitrico, TeorCinzas, TeorFerro, StatusLote, Analista, DataHora)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            int(fornecedor_id),
                            insumo_selecionado,
                            nota_fiscal,
                            lote,
                            umidade,
                            pureza,
                            aflatoxina,
                            capacidade_expansao,
                            peso_hectolitrico,
                            teor_cinzas,
                            teor_ferro,
                            status_final,
                            analista,
                            data_hora_agora
                        ))
                        
                        # Guardar a última análise feita no Session State
                        st.session_state.ultima_analise = {
                            "analista": analista,
                            "fornecedor": fornecedor_selecionado,
                            "insumo": insumo_selecionado,
                            "nota_fiscal": nota_fiscal,
                            "lote": lote,
                            "status_final": status_final,
                            "data_hora": data_hora_agora,
                            "detalhes": status_params
                        }
                        
                        st.success(f"Laudo de {insumo_selecionado} registrado com sucesso para a NF {nota_fiscal}!")
                        st.rerun()
                    except sqlite3.Error as e:
                        st.error(f"Erro ao salvar análise no banco de dados: {e}")

    # Exibe o resultado da avaliação atual na coluna direita
    with col_hist:
        st.subheader("🏁 Avaliação da Carga")
        
        if "ultima_analise" in st.session_state:
            res = st.session_state.ultima_analise
            
            # Definir cores para o status final
            if res["status_final"] == "Aprovado":
                st.success(f"### STATUS FINAL: {res['insumo'].upper()} APROVADO")
            elif res["status_final"] == "Aprovado com Restrição":
                st.warning(f"### STATUS FINAL: {res['insumo'].upper()} APROVADO COM RESTRIÇÃO")
            else:
                st.error(f"### STATUS FINAL: {res['insumo'].upper()} REPROVADO")
                
            st.markdown(f"**Resumo do Laudo (Lote: {res['lote']} - Nota Fiscal: {res['nota_fiscal']})**")
            
            for param, (status_param, desc) in res["detalhes"].items():
                if status_param == "Aprovado":
                    icon = "🟢"
                elif status_param == "Aprovado com Restrição":
                    icon = "🟡"
                else:
                    icon = "🔴"
                st.write(f"{icon} **{param}**: {status_param} ({desc})")
                
            st.markdown(f"*Análise realizada por **{res['analista']}** em {res['data_hora']}*")
            st.markdown("---")
        else:
            st.info("Insira os dados no formulário ao lado e clique em salvar para processar e ver a decisão do motor de qualidade.")
            st.markdown("---")

        # 2. HISTÓRICO DE ANÁLISES RECENTES
        st.subheader("📋 Últimas Análises do Dia")
        
        try:
            historico_df = executar_query("""
                SELECT a.ID, f.NomeEmpresa, a.Insumo, a.NotaFiscal, a.LoteFornecedor, a.Umidade, a.StatusLote, a.Analista, a.DataHora 
                FROM analises a
                JOIN fornecedores f ON a.FornecedorID = f.ID
                ORDER BY a.DataHora DESC
                LIMIT 5
            """)
            
            if historico_df.empty:
                st.info("Nenhuma análise cadastrada até o momento.")
            else:
                historico_show = historico_df.rename(columns={
                    'NomeEmpresa': 'Fornecedor',
                    'Insumo': 'Insumo',
                    'NotaFiscal': 'Nota Fiscal',
                    'LoteFornecedor': 'Lote',
                    'Umidade': 'Umidade (%)',
                    'StatusLote': 'Decisão',
                    'Analista': 'Analista',
                    'DataHora': 'Data/Hora'
                })
                st.dataframe(historico_show, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {e}")
