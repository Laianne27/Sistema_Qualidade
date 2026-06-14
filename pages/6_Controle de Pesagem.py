import streamlit as st
import sqlite3
from datetime import datetime
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

# Configuração da página e temas
aplicar_tema("Controle de Pesagem", "⚖️")

st.title("⚖️ Controle de Pesagem (Balança)")
st.markdown("Fluxo logístico de balança de entrada (Peso Bruto) e saída (Tara) para aferição de volumes.")
st.markdown("---")

# Restrição de acesso: somente Admin e Portaria
perfil = st.session_state.get("role", "Administrador")
if perfil not in ["Administrador", "Portaria"]:
    st.error("⚠️ Acesso Restrito. Você não possui permissão para acessar o módulo de Balança.")
else:
    tab_entrada, tab_saida, tab_historico = st.tabs([
        "🚚 Pesagem de Entrada (Bruto)",
        "🚚 Pesagem de Saída (Tara)",
        "📋 Histórico de Pesagens"
    ])

    # --- 1. ABA: PESAGEM DE ENTRADA ---
    with tab_entrada:
        st.subheader("Entrada de Carga (Peso Bruto)")
        st.markdown("Selecione o caminhão na fila de triagem e registre o peso bruto inicial.")

        # Busca agendamentos que não possuem registro na tabela de pesagens
        query_ativos = """
            SELECT a.ID, f.NomeEmpresa, a.TipoInsumo, a.PlacaCaminhao, a.QuantidadeEsperada, a.NotaFiscal
            FROM agendamentos a
            JOIN fornecedores f ON a.FornecedorCNPJ = f.CNPJ
            LEFT JOIN pesagens p ON a.ID = p.AgendamentoID
            WHERE p.ID IS NULL AND a.Status NOT IN ('Reprovado', 'Concluído')
            ORDER BY a.DataAgendada ASC, a.ID ASC
        """
        ativos_df = executar_query(query_ativos)

        if ativos_df.empty:
            st.info("ℹ️ Nenhum caminhão aguardando pesagem de entrada na fila de portaria.")
        else:
            # Formata display para o selectbox
            ativos_df['display'] = ativos_df['PlacaCaminhao'] + ' | ' + ativos_df['NomeEmpresa'] + ' (' + ativos_df['TipoInsumo'] + ') - NF: ' + ativos_df['NotaFiscal']
            
            selecionado_display = st.selectbox(
                "Selecione o Veículo para Pesagem de Entrada *",
                options=ativos_df['display'],
                index=None,
                placeholder="Selecione a placa do veículo..."
            )

            if selecionado_display:
                row_sel = ativos_df[ativos_df['display'] == selecionado_display].iloc[0]
                
                with st.form("form_pesagem_entrada", clear_on_submit=True):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"🏢 **Fornecedor:** {row_sel['NomeEmpresa']}")
                        st.write(f"🌾 **Insumo:** {row_sel['TipoInsumo']}")
                    with col_info2:
                        st.write(f"📄 **Nota Fiscal:** {row_sel['NotaFiscal']}")
                        peso_nf_str = f"{row_sel['QuantidadeEsperada']:,}".replace(',', '.')
                        st.write(f"⚖️ **Peso NF (Esperado):** {peso_nf_str} Kg")
                    
                    st.divider()
                    
                    peso_bruto = st.number_input(
                        "Peso Bruto Medido na Balança (Kg) *",
                        min_value=0.0,
                        step=50.0,
                        help="Insira o peso total do veículo carregado."
                    )
                    
                    peso_nf_efetivo = st.number_input(
                        "Peso Declarado na Nota Fiscal (Kg) *",
                        min_value=0.0,
                        value=float(row_sel['QuantidadeEsperada']),
                        step=50.0,
                        help="Confirme o valor declarado na Nota Fiscal impressa."
                    )

                    submit_entrada = st.form_submit_button("💾 Salvar Pesagem de Entrada")

                    if submit_entrada:
                        if peso_bruto <= 0 or peso_nf_efetivo <= 0:
                            st.warning("⚠️ O peso medido e o peso declarado da nota fiscal devem ser maiores que zero.")
                        else:
                            try:
                                # Insere pesagem inicial
                                data_hora_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                executar_dml("""
                                    INSERT INTO pesagens (AgendamentoID, PesoBruto, PesoNotaFiscal, DataHoraEntrada)
                                    VALUES (?, ?, ?, ?)
                                """, (int(row_sel['ID']), peso_bruto, peso_nf_efetivo, data_hora_agora))
                                
                                # Atualiza status do agendamento
                                executar_dml(
                                    "UPDATE agendamentos SET Status = 'Em Pesagem' WHERE ID = ?",
                                    (int(row_sel['ID']),)
                                )
                                
                                st.success(f"✅ Pesagem de entrada registrada com sucesso para o veículo **{row_sel['PlacaCaminhao']}**!")
                                st.toast("Entrada registrada!", icon="⚖️")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar pesagem: {e}")

    # --- 2. ABA: PESAGEM DE SAÍDA ---
    with tab_saida:
        st.subheader("Saída de Carga (Peso Tara)")
        st.markdown("Selecione o veículo descarregado para registrar o peso tara e finalizar o recebimento.")

        # Busca pesagens que possuem apenas peso bruto (entrada) registrado
        query_pendentes_saida = """
            SELECT p.ID as PesagemID, a.ID as AgendamentoID, f.NomeEmpresa, a.TipoInsumo, 
                   a.PlacaCaminhao, p.PesoBruto, p.PesoNotaFiscal, p.DataHoraEntrada, a.NotaFiscal
            FROM pesagens p
            JOIN agendamentos a ON p.AgendamentoID = a.ID
            JOIN fornecedores f ON a.FornecedorCNPJ = f.CNPJ
            WHERE p.PesoTara IS NULL AND a.Status NOT IN ('Reprovado')
        """
        pendentes_saida_df = executar_query(query_pendentes_saida)

        if pendentes_saida_df.empty:
            st.info("ℹ️ Nenhum veículo aguardando pesagem de saída na balança.")
        else:
            pendentes_saida_df['display'] = pendentes_saida_df['PlacaCaminhao'] + ' | ' + pendentes_saida_df['NomeEmpresa'] + ' (Entrada: ' + pendentes_saida_df['DataHoraEntrada'] + ')'
            
            selecionado_saida = st.selectbox(
                "Selecione o Veículo para Pesagem de Saída *",
                options=pendentes_saida_df['display'],
                index=None,
                placeholder="Selecione a placa..."
            )

            if selecionado_saida:
                row_saida = pendentes_saida_df[pendentes_saida_df['display'] == selecionado_saida].iloc[0]
                
                with st.form("form_pesagem_saida", clear_on_submit=True):
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        st.write(f"🏢 **Fornecedor:** {row_saida['NomeEmpresa']}")
                        st.write(f"🌾 **Insumo:** {row_saida['TipoInsumo']}")
                        st.write(f"📄 **Nota Fiscal:** {row_saida['NotaFiscal']}")
                    with col_s2:
                        peso_bruto_str = f"{row_saida['PesoBruto']:,}".replace(',', '.')
                        peso_nf_saida_str = f"{row_saida['PesoNotaFiscal']:,}".replace(',', '.')
                        st.write(f"⚖️ **Peso Bruto Entrada:** {peso_bruto_str} Kg")
                        st.write(f"📋 **Peso Declarado na NF:** {peso_nf_saida_str} Kg")
                    
                    st.divider()

                    peso_tara = st.number_input(
                        "Peso Tara Medido na Balança (Kg) *",
                        min_value=0.0,
                        step=50.0,
                        help="Insira o peso do caminhão vazio após a descarga."
                    )

                    submit_saida = st.form_submit_button("💾 Salvar Pesagem de Saída e Fechar Carga")

                    if submit_saida:
                        if peso_tara <= 0:
                            st.warning("⚠️ O peso tara deve ser maior que zero.")
                        elif peso_tara >= row_saida['PesoBruto']:
                            st.error("❌ O peso tara (caminhão vazio) não pode ser maior ou igual ao peso bruto (entrada).")
                        else:
                            # Calcula pesos e diferença
                            peso_liquido = row_saida['PesoBruto'] - peso_tara
                            diferenca_kg = peso_liquido - row_saida['PesoNotaFiscal']
                            diferenca_percentual = (diferenca_kg / row_saida['PesoNotaFiscal']) * 100
                            
                            try:
                                data_hora_saida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                
                                # Atualiza tabela de pesagens
                                executar_dml("""
                                    UPDATE pesagens 
                                    SET PesoTara = ?, PesoLiquido = ?, DiferencaPercentual = ?, DataHoraSaida = ?
                                    WHERE ID = ?
                                """, (peso_tara, peso_liquido, diferenca_percentual, data_hora_saida, int(row_saida['PesagemID'])))
                                
                                # Verifica o status atual da análise de qualidade da carga (para não sobrescrever Reprovado/Quarentena)
                                check_status = executar_query("SELECT Status FROM agendamentos WHERE ID = ?", (int(row_saida['AgendamentoID']),))
                                current_status = check_status['Status'].iloc[0] if not check_status.empty else 'Pendente'
                                
                                # Se a carga não estiver em Quarentena ou Reprovada, marca como Concluída
                                next_status = 'Concluído' if current_status not in ['Quarentena', 'Reprovado'] else current_status
                                
                                executar_dml(
                                    "UPDATE agendamentos SET Status = ? WHERE ID = ?",
                                    (next_status, int(row_saida['AgendamentoID']))
                                )

                                # Exibe recibo de pesagem formatado
                                st.success("✅ Pesagem de saída concluída e carga finalizada!")
                                st.toast("Carga concluída na balança!", icon="⚖️")
                                
                                # Exibe resumo do recibo em container
                                with st.container(border=True):
                                    st.subheader("🧾 Recibo de Fechamento de Carga")
                                    col_r1, col_r2 = st.columns(2)
                                    peso_bruto_recibo = f"{row_saida['PesoBruto']:,}".replace(',', '.')
                                    peso_tara_recibo = f"{peso_tara:,}".replace(',', '.')
                                    peso_liq_recibo = f"{peso_liquido:,}".replace(',', '.')
                                    peso_nf_recibo = f"{row_saida['PesoNotaFiscal']:,}".replace(',', '.')
                                    
                                    col_r1.write(f"**Veículo Placa:** {row_saida['PlacaCaminhao']}")
                                    col_r1.write(f"**Peso Bruto (Entrada):** {peso_bruto_recibo} Kg")
                                    col_r1.write(f"**Peso Tara (Saída):** {peso_tara_recibo} Kg")
                                    
                                    col_r2.write(f"**Peso Líquido Aferido:** {peso_liq_recibo} Kg")
                                    col_r2.write(f"**Peso Declarado (Nota Fiscal):** {peso_nf_recibo} Kg")
                                    
                                    # Formata diferença
                                    color_diff = "green" if abs(diferenca_percentual) <= 0.5 else "red"
                                    diff_kg_str = f"{diferenca_kg:+,}".replace(",", ".")
                                    diff_pct_str = f"{diferenca_percentual:+.2f}%".replace(".", ",")
                                    col_r2.markdown(f"**Diferença:** <span style='color:{color_diff}; font-weight:bold;'>{diff_kg_str} Kg ({diff_pct_str})</span>", unsafe_allow_html=True)
                                    
                                    if abs(diferenca_percentual) > 0.5:
                                        st.warning("⚠️ Atenção: A diferença de peso excedeu a tolerância padrão da indústria (+/- 0.5%).")
                                    else:
                                        st.success("✔️ Peso líquido dentro da tolerância aceitável.")
                                
                                # Rerun após exibição (opcional, mas bom ter botão de prosseguir)
                                if st.button("🔄 Atualizar Fila"):
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao finalizar pesagem: {e}")

    # --- 3. ABA: HISTÓRICO DE PESAGENS ---
    with tab_historico:
        st.subheader("Histórico Geral de Recebimentos")
        st.markdown("Consulte as cargas pesadas e finalize relatórios de balança.")

        try:
            historico_pesagens = executar_query("""
                SELECT a.PlacaCaminhao as 'Placa', f.NomeEmpresa as 'Fornecedor', a.TipoInsumo as 'Insumo',
                       p.PesoBruto as 'Bruto (Kg)', p.PesoTara as 'Tara (Kg)', p.PesoLiquido as 'Líquido Aferido (Kg)', 
                       p.PesoNotaFiscal as 'NF (Kg)', p.DiferencaPercentual as 'Desvio (%)',
                       p.DataHoraEntrada as 'Hora Entrada', p.DataHoraSaida as 'Hora Saída', a.Status
                FROM pesagens p
                JOIN agendamentos a ON p.AgendamentoID = a.ID
                JOIN fornecedores f ON a.FornecedorCNPJ = f.CNPJ
                ORDER BY p.DataHoraEntrada DESC
            """)

            if historico_pesagens.empty:
                st.info("ℹ️ Nenhuma pesagem registrada no histórico.")
            else:
                st.dataframe(
                    historico_pesagens,
                    use_container_width=True,
                    hide_index=True
                )
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {e}")
