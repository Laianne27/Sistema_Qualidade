import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import json
import sqlite3
from datetime import datetime
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

# Configuração da página e temas
aplicar_tema("Hub de Integrações", "🔌")

st.title("🔌 Hub de Integrações e Ecossistema")
st.markdown("Centralizador de comunicações para unificação de dados da qualidade com ERPs, planilhas externas e leitura de XML de Notas Fiscais (NF-e).")
st.markdown("---")

# Restrição de acesso: somente Admin
perfil = st.session_state.get("role", "Administrador")
if perfil != "Administrador":
    st.error("⚠️ Acesso Restrito. Apenas administradores do sistema possuem permissão para configurar integrações de dados.")
else:
    tab_xml, tab_csv, tab_webhooks, tab_api = st.tabs([
        "📄 Leitor de XML (NF-e)",
        "📊 Importar Pedidos (CSV)",
        "🔔 Disparo de Webhooks",
        "💻 APIs e Desenvolvedores"
    ])

    # --- HELPER DE LEITURA DE XML NF-e ---
    def parse_nfe_xml(file_bytes):
        try:
            # Parseia o XML da NF-e brasileira de forma simplificada
            tree = ET.ElementTree(ET.fromstring(file_bytes))
            root = tree.getroot()
            
            # Remove namespaces do XML para facilitar a busca por tags
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]
            
            # Busca campos principais
            nome_emitente = root.find(".//emit/xNome")
            cnpj_emitente = root.find(".//emit/CNPJ")
            numero_nf = root.find(".//ide/nNF")
            
            # Busca primeiro produto no detalhamento da NF
            insumo_nome = root.find(".//det/prod/xProd")
            quantidade = root.find(".//det/prod/qCom")
            
            dados = {
                "fornecedor": nome_emitente.text if nome_emitente is not None else "Emitente Não Identificado",
                "cnpj": cnpj_emitente.text if cnpj_emitente is not None else "00000000000000",
                "nf": numero_nf.text if numero_nf is not None else "000000",
                "insumo": insumo_nome.text if insumo_nome is not None else "Insumo Genérico",
                "quantidade": float(quantidade.text) if quantidade is not None else 0.0
            }
            
            # Formata CNPJ se tiver 14 dígitos
            if len(dados["cnpj"]) == 14:
                c = dados["cnpj"]
                dados["cnpj"] = f"{c[0:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:14]}"
                
            return dados, None
        except Exception as e:
            return None, f"Erro ao analisar arquivo XML: {e}"

    # --- 1. ABA: LEITOR DE XML DE NF-e ---
    with tab_xml:
        st.subheader("Leitor Inteligente de XML de NF-e")
        st.markdown(
            """
            Carregue o arquivo XML de uma Nota Fiscal Eletrônica (NF-e) para realizar o 
            **autocadastro do fornecedor** (se for novo) e o **agendamento da janela** instantaneamente, 
            eliminando digitação manual.
            """
        )
        
        # Botão para baixar XML mockado de teste
        mock_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
    <NFe>
        <infNFe>
            <ide>
                <nNF>887711</nNF>
            </ide>
            <emit>
                <CNPJ>45678901000134</CNPJ>
                <xNome>Moinho Central do Brasil S/A</xNome>
            </emit>
            <det nItem="1">
                <prod>
                    <xProd>Trigo em Grão Especial</xProd>
                    <qCom>38500.00</qCom>
                </prod>
            </det>
        </infNFe>
    </NFe>
</nfeProc>"""
        
        st.download_button(
            label="📥 Baixar XML de Teste (Mock)",
            data=mock_xml_content,
            file_name="nfe_mock_teste.xml",
            mime="text/xml",
            help="Use este arquivo XML simulado para testar o upload abaixo!"
        )
        
        st.divider()

        uploaded_xml = st.file_uploader("Selecione o arquivo XML da NF-e (Chave de Acesso)", type=["xml"])
        
        if uploaded_xml:
            xml_bytes = uploaded_xml.read()
            dados_nfe, erro = parse_nfe_xml(xml_bytes)
            
            if erro:
                st.error(erro)
            else:
                st.success("✅ XML da Nota Fiscal Eletrônica lido com sucesso!")
                
                # Exibição dos dados extraídos do XML em ficha estilizada
                with st.container(border=True):
                    st.subheader("📄 Dados Extraídos da NF-e")
                    col_x1, col_x2 = st.columns(2)
                    with col_x1:
                        st.write(f"🏢 **Emitente/Fornecedor:** {dados_nfe['fornecedor']}")
                        st.write(f"📄 **CNPJ Emitente:** {dados_nfe['cnpj']}")
                    with col_x2:
                        st.write(f"🔢 **Número da Nota Fiscal:** {dados_nfe['nf']}")
                        st.write(f"🌾 **Insumo Identificado:** {dados_nfe['insumo']}")
                        st.write(f"⚖️ **Volume Declarado:** {dados_nfe['quantidade']:.2f} Kg".replace(".", ","))
                
                # Ação para cadastrar direto
                if st.button("⚡ Processar e Registrar no Sistema", type="primary"):
                    try:
                        # 1. Verifica se o fornecedor existe, senão autocadastra
                        forn_check = executar_query("SELECT CNPJ FROM fornecedores WHERE CNPJ = ?", (dados_nfe['cnpj'],))
                        if forn_check.empty:
                            executar_dml("""
                                INSERT INTO fornecedores (NomeEmpresa, CNPJ, Endereco, Email, Telefone)
                                VALUES (?, ?, ?, ?, ?)
                            """, (dados_nfe['fornecedor'], dados_nfe['cnpj'], "Endereço extraído via XML", "xml@fornecedor.com", "(00) 0000-0000"))
                            st.info(f"🏢 Fornecedor **{dados_nfe['fornecedor']}** não existia e foi cadastrado automaticamente!")
                            
                        # 2. Verifica se a NF já foi agendada
                        nf_check = executar_query("SELECT ID FROM agendamentos WHERE NotaFiscal = ?", (f"NF-{dados_nfe['nf']}",))
                        if not nf_check.empty:
                            st.error(f"❌ Erro: Já existe um agendamento registrado para a Nota Fiscal NF-{dados_nfe['nf']}.")
                        else:
                            # 3. Insere o agendamento
                            data_agora_str = datetime.now().strftime('%Y-%m-%d')
                            time_agora_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            executar_dml("""
                                INSERT INTO agendamentos (FornecedorCNPJ, TipoInsumo, QuantidadeEsperada, PlacaCaminhao, NomeMotorista, NotaFiscal, DataAgendada, Status, DataCadastro)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                dados_nfe['cnpj'], 
                                dados_nfe['insumo'], 
                                dados_nfe['quantidade'], 
                                "PLA-0000", 
                                "Motorista via XML", 
                                f"NF-{dados_nfe['nf']}", 
                                data_agora_str, 
                                "Pendente", 
                                time_agora_str
                            ))
                            
                            st.success(f"✅ Agendamento de **{dados_nfe['insumo']}** criado com sucesso para hoje ({datetime.now().strftime('%d/%m/%Y')})!")
                            st.toast("Agendamento criado via XML!", icon="📄")
                    except Exception as e:
                        st.error(f"Erro ao processar integração do XML: {e}")

    # --- 2. ABA: IMPORTADOR CSV DE PEDIDOS DE COMPRA ---
    with tab_csv:
        st.subheader("Integração de Planilhas: Pedidos de Compra ERP")
        st.markdown(
            """
            Carregue a planilha de Pedidos de Compra abertos em seu ERP (Bling, SAP, Totvs) 
            para cruzar os agendamentos com as autorizações reais de compras da empresa.
            """
        )
        
        # CSV de teste
        csv_mock = "NumeroPedido,CNPJFornecedor,Insumo,QuantidadeAutorizada\n" \
                   "PED-2026-901,12.345.678/0001-90,Milho em Grão,45000\n" \
                   "PED-2026-902,98.765.432/0001-21,Soja em Grão,60000\n" \
                   "PED-2026-903,45.678.901/0001-34,Trigo em Grão,32000"
                   
        st.download_button(
            label="📥 Baixar CSV de Pedidos de Teste (Mock)",
            data=csv_mock,
            file_name="pedidos_compras_erp.csv",
            mime="text/csv"
        )
        
        st.divider()

        uploaded_csv = st.file_uploader("Selecione o arquivo CSV de Pedidos do ERP", type=["csv"])
        
        if uploaded_csv:
            try:
                df_csv = pd.read_csv(uploaded_csv)
                st.success("✅ Arquivo de pedidos carregado com sucesso!")
                
                # Renomeia colunas para visualização premium
                df_show_csv = df_csv.rename(columns={
                    'NumeroPedido': 'Nº Pedido ERP',
                    'CNPJFornecedor': 'CNPJ Fornecedor',
                    'Insumo': 'Insumo Autorizado',
                    'QuantidadeAutorizada': 'Volume Autorizado (Kg)'
                })
                st.dataframe(df_show_csv, use_container_width=True, hide_index=True)
                
                st.info("💡 Estes pedidos integrados agora podem ser cruzados na triagem da portaria para validar a entrega.")
            except Exception as e:
                st.error(f"Erro ao ler arquivo CSV: {e}")

    # --- 3. ABA: CONSOLE DE DISPARO DE WEBHOOKS ---
    with tab_webhooks:
        st.subheader("Console de Webhooks de Qualidade")
        st.markdown(
            """
            Configure o disparo automático de eventos de rede (**Webhooks**). 
            Sempre que uma análise técnica mudar de status (Aprovada, Reprovada ou Quarentena), 
            o QualiHub enviará um payload JSON contendo o parecer final para o endpoint cadastrado.
            """
        )
        
        webhook_url = st.text_input(
            "URL do Webhook Receptor (Ex: endpoint do seu ERP)",
            value="https://api.meuerp.com.br/v1/qualidade/recebimento",
            placeholder="Insira a URL de recepção..."
        )
        
        st.divider()
        st.subheader("🧪 Simular Disparo de Evento")
        st.write("Escolha uma carga para simular o payload JSON de integração que o ERP receberia:")
        
        # Busca última análise para simulação
        last_analise = executar_query("""
            SELECT a.ID, f.NomeEmpresa, a.Insumo, a.NotaFiscal, a.StatusLote, a.Umidade, a.DataHora
            FROM analises a
            JOIN fornecedores f ON a.FornecedorID = f.ID
            ORDER BY a.DataHora DESC
            LIMIT 1
        """)
        
        if last_analise.empty:
            st.info("Nenhuma análise no histórico para simular.")
        else:
            row_l = last_analise.iloc[0]
            mock_payload = {
                "event": "qualidade.recebimento.finalizado",
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "data": {
                    "analise_id": int(row_l['ID']),
                    "fornecedor": row_l['NomeEmpresa'],
                    "insumo": row_l['Insumo'],
                    "nota_fiscal": row_l['NotaFiscal'],
                    "status_qualidade": row_l['StatusLote'],
                    "umidade_medida": float(row_l['Umidade']),
                    "data_hora_inspecao": row_l['DataHora']
                }
            }
            
            st.json(mock_payload)
            
            if st.button("⚡ Testar Envio de Payload (Simulado)"):
                st.toast("Disparando Webhook simulado para o ERP...", icon="🔌")
                st.success(f"✔️ Webhook enviado! Resposta do servidor ERP: HTTP 200 OK (Evento: {mock_payload['event']})")

    # --- 4. ABA: APIS E DESENVOLVEDORES ---
    with tab_api:
        st.subheader("Especificações de Integração (API)")
        st.markdown(
            """
            Desenvolvedores de TI podem utilizar os endpoints REST (mockados) 
            abaixo para consumir os relatórios de qualidade programaticamente no Power BI ou outros sistemas.
            """
        )
        
        # Código em cURL
        st.markdown("**1. Buscar Últimos Laudos Técnicos (GET)**")
        code_curl = 'curl -X GET "http://localhost:8501/api/v1/laudos" \\\n' \
                    '  -H "Authorization: Bearer KEY_DE_INTEGRACAO_AQUI" \\\n' \
                    '  -H "Content-Type: application/json"'
        st.code(code_curl, language="bash")
        
        # Payload JSON de retorno
        st.markdown("**Modelo de Resposta JSON (Schema)**")
        json_schema = {
            "status": "success",
            "count": 1,
            "data": [
                {
                    "id": 142,
                    "fornecedor": "Cerealista Amambai Ltda",
                    "cnpj": "12.345.678/0001-90",
                    "insumo": "Milho em Grão",
                    "nota_fiscal": "NF-99881",
                    "lote": "LOTE-2026-A1",
                    "status_qualidade": "Aprovado",
                    "parametros": {
                        "umidade_pct": 13.2,
                        "pureza_pct": 98.5,
                        "aflatoxina_ppb": 12.0
                    },
                    "analista": "Roberto Souza",
                    "data_hora": "2026-06-01 10:45:00"
                }
            ]
        }
        st.json(json_schema)
