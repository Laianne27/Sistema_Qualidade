import streamlit as st
import sqlite3
from datetime import datetime
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

# Configuração da página e design
aplicar_tema("Gestão de Quarentena", "🛡️")

st.title("🛡️ Painel de Gestão de Quarentena")
st.markdown("Interface administrativa para liberação controlada (desvio comercial) ou descarte definitivo de cargas fora de conformidade.")
st.markdown("---")

# Restrição de acesso: apenas Administrador
perfil = st.session_state.get("role", "Administrador")
if perfil != "Administrador":
    st.error("⚠️ Acesso Restrito. Apenas administradores do sistema de qualidade possuem permissão para liberar lotes sob desvio.")
else:
    # 1. BUSCAR LOTES EM QUARENTENA
    query_quarentena = """
        SELECT a.ID as AnaliseID, f.NomeEmpresa, a.Insumo, a.NotaFiscal, a.LoteFornecedor,
               a.Umidade, a.Pureza, a.Aflatoxina, a.CapacidadeExpansao, a.PesoHectolitrico, 
               a.TeorCinzas, a.TeorFerro, a.StatusLote, a.Analista, a.DataHora
        FROM analises a
        JOIN fornecedores f ON a.FornecedorID = f.ID
        WHERE a.StatusLote = 'Quarentena'
        ORDER BY a.DataHora DESC
    """
    quarentena_df = executar_query(query_quarentena)

    # Tabs para controle
    tab_pendentes, tab_desvios_liberados = st.tabs([
        "⏳ Lotes Aguardando Decisão",
        "✔️ Histórico de Desvios Liberados"
    ])

    with tab_pendentes:
        if quarentena_df.empty:
            st.success("✅ Excelente! Nenhum lote em quarentena pendente de decisão no momento.")
        else:
            st.warning(f"⚠️ Atenção: Existem **{len(quarentena_df)}** lote(s) retido(s) na quarentena.")
            
            # Formata display para o selectbox
            quarentena_df['display'] = quarentena_df['NomeEmpresa'] + ' | ' + quarentena_df['Insumo'] + ' (Lote: ' + quarentena_df['LoteFornecedor'] + ')'
            
            selecionado = st.selectbox(
                "Selecione o Lote para Análise Técnica *",
                options=quarentena_df['display'],
                index=None,
                placeholder="Selecione o lote retido..."
            )

            if selecionado:
                row = quarentena_df[quarentena_df['display'] == selecionado].iloc[0]
                
                # Split Layout (Medições do Lote à esquerda, Formulário de Decisão à direita)
                col_dados, col_decisao = st.columns([5, 5])
                
                with col_dados:
                    st.subheader("📊 Resultados de Laboratório")
                    
                    with st.container(border=True):
                        st.write(f"🏢 **Fornecedor:** {row['NomeEmpresa']}")
                        st.write(f"🌾 **Insumo:** {row['Insumo']}")
                        st.write(f"📄 **Nota Fiscal:** {row['NotaFiscal']}")
                        st.write(f"📦 **Lote do Fornecedor:** {row['LoteFornecedor']}")
                        st.write(f"👤 **Analista Responsável:** {row['Analista']}")
                        st.write(f"🕒 **Data da Análise:** {row['DataHora']}")
                    
                    st.markdown("**Valores Analisados:**")
                    
                    # Tabela detalhada das medições
                    param_table = []
                    # Verifica quais parâmetros são válidos (não nulos) e lista-os
                    params_list = {
                        "Umidade": (row['Umidade'], "%"),
                        "Pureza": (row['Pureza'], "%"),
                        "Aflatoxina": (row['Aflatoxina'], "ppb"),
                        "Capacidade de Expansão": (row['CapacidadeExpansao'], "ml/g"),
                        "Peso Hectolítrico (PH)": (row['PesoHectolitrico'], "kg/hl"),
                        "Teor de Cinzas": (row['TeorCinzas'], "%"),
                        "Teor de Ferro": (row['TeorFerro'], "mg/100g")
                    }
                    
                    for name, (val, unit) in params_list.items():
                        if val is not None and val > 0:
                            # Classifica desvio na exibição
                            is_failed = False
                            # Regra rápida para marcar desvios visualmente
                            if name == "Umidade" and val > 14.0:
                                is_failed = True
                            elif name == "Pureza" and val < 98.0:
                                is_failed = True
                            elif name == "Aflatoxina" and val > 20.0:
                                is_failed = True
                            elif name == "Capacidade de Expansão" and val < 30.0:
                                is_failed = True
                            elif name == "Peso Hectolítrico (PH)" and val < 75.0:
                                is_failed = True
                            elif name == "Teor de Cinzas" and val > 0.8:
                                is_failed = True
                            elif name == "Teor de Ferro" and (val < 4.0 or val > 9.0):
                                is_failed = True
                                
                            status_text = "❌ FORA DO PADRÃO" if is_failed else "🟢 DENTRO DO LIMITE"
                            param_table.append({
                                "Parâmetro": name,
                                "Valor Medido": f"{val} {unit}",
                                "Status": status_text
                            })
                            
                    st.table(param_table)

                with col_decisao:
                    st.subheader("⚖️ Decisão do Comitê de Qualidade")
                    
                    decisao_admin = st.radio(
                        "Qual a decisão técnica sobre este lote? *",
                        options=[
                            "Liberar sob Desvio Comercial (Aprovar com desconto)",
                            "Reprovar Lote Definitivamente (Rejeição total)"
                        ],
                        index=0
                    )
                    
                    with st.form("form_decisao_quarentena", clear_on_submit=True):
                        autorizador = st.text_input("Nome do Gestor / Matrícula *", value=st.session_state.get("user_name", ""))
                        
                        desconto_comercial = 0.0
                        if "Liberar sob Desvio" in decisao_admin:
                            desconto_comercial = st.number_input(
                                "Desconto Aplicado sobre o Volume (%) *",
                                min_value=0.0,
                                max_value=50.0,
                                value=2.0,
                                step=0.5,
                                help="Desconto comercial padrão devido à qualidade limítrofe (ex: secagem extra ou excesso de impurezas)."
                            )
                        
                        justificativa = st.text_area(
                            "Parecer Técnico / Justificativa de Decisão *",
                            placeholder="Descreva detalhadamente a justificativa para liberação sob desvio ou descarte da carga..."
                        )

                        submit_decisao = st.form_submit_button("⚡ Registrar Decisão Final")

                        if submit_decisao:
                            if not (autorizador.strip() and justificativa.strip()):
                                st.warning("⚠️ O nome do autorizador e a justificativa técnica são obrigatórios.")
                            else:
                                try:
                                    data_hora_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    
                                    if "Liberar sob Desvio" in decisao_admin:
                                        status_final = "Aprovado com Desvio"
                                        liberado = 1
                                        just_texto = f"Liberado sob desvio com desconto comercial de {desconto_comercial}%. Motivo: {justificativa}"
                                        mensagem_sucesso = f"✅ O lote foi **LIBERADO SOB DESVIO** e a carga está autorizada para descarregamento com desconto de {desconto_comercial}%!"
                                    else:
                                        status_final = "Reprovado"
                                        liberado = 0
                                        just_texto = f"Reprovado na quarentena. Justificativa: {justificativa}"
                                        mensagem_sucesso = "❌ O lote foi **REPROVADO DEFINITIVAMENTE**. A balança de saída e a portaria foram notificadas para expulsar o veículo."
                                    
                                    # 1. Atualiza tabela de analises
                                    executar_dml("""
                                        UPDATE analises 
                                        SET StatusLote = ?, 
                                            DesvioLiberado = ?, 
                                            DesvioAutorizador = ?, 
                                            DesvioJustificativa = ?, 
                                            DesvioDataHora = ?
                                        WHERE ID = ?
                                    """, (status_final, liberado, autorizador, just_texto, data_hora_agora, int(row['AnaliseID'])))
                                    
                                    # 2. Atualiza a tabela de agendamentos usando a Nota Fiscal
                                    executar_dml(
                                        "UPDATE agendamentos SET Status = ? WHERE NotaFiscal = ?",
                                        (status_final, row['NotaFiscal'])
                                    )
                                    
                                    st.success(mensagem_sucesso)
                                    st.toast("Decisão gravada!", icon="🛡️")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar decisão no banco de dados: {e}")

    with tab_desvios_liberados:
        st.subheader("Auditoria de Desvios Liberados")
        st.markdown("Consulte o histórico de lotes analisados pela diretoria de qualidade.")
        
        try:
            historico_desvios = executar_query("""
                SELECT f.NomeEmpresa as 'Fornecedor', a.Insumo, a.NotaFiscal as 'NF', a.LoteFornecedor as 'Lote',
                       a.StatusLote as 'Decisão Final', a.DesvioAutorizador as 'Autorizador', 
                       a.DesvioJustificativa as 'Justificativa Técnica', a.DesvioDataHora as 'Data/Hora Decisão'
                FROM analises a
                JOIN fornecedores f ON a.FornecedorID = f.ID
                WHERE a.DesvioAutorizador IS NOT NULL
                ORDER BY a.DesvioDataHora DESC
            """)
            
            if historico_desvios.empty:
                st.info("ℹ️ Nenhum registro de desvio no histórico de auditoria.")
            else:
                st.dataframe(historico_desvios, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Erro ao carregar histórico de desvios: {e}")
