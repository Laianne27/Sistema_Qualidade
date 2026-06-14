import streamlit as st
import sqlite3
from datetime import datetime
from utils.db import executar_query, executar_dml
from utils.theme import aplicar_tema

# Configuração da página e estilos
aplicar_tema("Análise de Recebimento", "🧪")

def gerar_html_certificado(res):
    linhas_tabela = ""
    for param, (status_param, val_medido, desc) in res["detalhes"].items():
        cor_status = "#16a34a" if status_param == "Aprovado" else ("#d97706" if status_param == "Aprovado com Restrição" else "#dc2626")
        linhas_tabela += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: 500;">{param}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: center;">{val_medido}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: center; color: {cor_status}; font-weight: bold; text-transform: uppercase; font-size: 12px;">{status_param}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-size: 13px; color: #64748b;">{desc}</td>
        </tr>
        """
    
    status_cor = "#16a34a" if res['status_final'] == "Aprovado" else ("#d97706" if res['status_final'] in ["Aprovado com Restrição", "Aprovado com Desvio"] else "#dc2626")
    if res['status_final'] == "Quarentena":
        status_cor = "#e11d48"
        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Certificado de Qualidade - QualiHub</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            body {{
                font-family: 'Inter', sans-serif;
                margin: 40px;
                color: #1e293b;
                background-color: #ffffff;
            }}
            .cert-container {{
                border: 3px double #cbd5e1;
                border-radius: 12px;
                padding: 30px;
                max-width: 800px;
                margin: 0 auto;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #cbd5e1;
                padding-bottom: 20px;
                margin-bottom: 25px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 800;
                color: #0f172a;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .header p {{
                margin: 5px 0 0 0;
                font-size: 13px;
                color: #64748b;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 25px;
                background-color: #f8fafc;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
            }}
            .info-item {{
                line-height: 1.5;
            }}
            .info-item strong {{
                color: #475569;
            }}
            .status-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 800;
                text-transform: uppercase;
                font-size: 16px;
                color: #ffffff;
                background-color: {status_cor};
                margin-top: 10px;
                letter-spacing: 0.5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 25px;
            }}
            th {{
                background-color: #f1f5f9;
                color: #475569;
                font-weight: 600;
                text-align: left;
                padding: 12px 10px;
                border-bottom: 2px solid #cbd5e1;
                font-size: 13px;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                font-size: 12px;
                color: #94a3b8;
                border-top: 1px dashed #cbd5e1;
                padding-top: 20px;
            }}
            .signature-area {{
                margin-top: 30px;
                display: flex;
                justify-content: space-around;
                font-size: 14px;
            }}
            .sig-line {{
                border-top: 1px solid #94a3b8;
                width: 200px;
                text-align: center;
                padding-top: 5px;
                margin-top: 40px;
                color: #64748b;
            }}
        </style>
    </head>
    <body>
        <div class="cert-container">
            <div class="header">
                <h1>QualiHub</h1>
                <p>Sistema Digital de Gestão e Certificação de Qualidade</p>
                <p style="font-size: 11px; margin-top: 2px;">Laudo de Conformidade de Recebimento de Grãos</p>
            </div>
            
            <div class="info-grid">
                <div class="info-item">
                    <strong>Fornecedor:</strong> {res['fornecedor']}<br>
                    <strong>Tipo de Insumo:</strong> {res['insumo']}<br>
                    <strong>Lote do Fornecedor:</strong> {res['lote']}
                </div>
                <div class="info-item">
                    <strong>Nº Nota Fiscal:</strong> {res['nota_fiscal']}<br>
                    <strong>Analista Responsável:</strong> {res['analista']}<br>
                    <strong>Data/Hora de Emissão:</strong> {res['data_hora']}
                </div>
            </div>
            
            <div style="text-align: center; margin-bottom: 30px;">
                <span style="font-size: 12px; text-transform: uppercase; font-weight: 600; color: #64748b; display: block;">Resultado do Parecer Técnico</span>
                <div class="status-badge">{res['status_final']}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 30%;">Parâmetro</th>
                        <th style="width: 20%; text-align: center;">Medição</th>
                        <th style="width: 20%; text-align: center;">Status</th>
                        <th style="width: 30%;">Especificação Reguladora</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_tabela}
                </tbody>
            </table>
            
            <div class="signature-area">
                <div class="sig-line">
                    Assinatura do Analista<br>
                    <span style="font-size: 11px; font-style: italic;">{res['analista']}</span>
                </div>
                <div class="sig-line">
                    Controle de Qualidade<br>
                    <span style="font-size: 11px; font-style: italic;">QualiHub Automático</span>
                </div>
            </div>
            
            <div class="footer">
                <p>Este documento foi gerado eletronicamente e atesta a conformidade do insumo nas dependências de recepção industrial.</p>
                <p>© {datetime.now().year} QualiHub Inc. Todos os direitos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

st.title("🧪 Análise de Recebimento de Insumos")
st.markdown("Módulo laboratorial para controle físico-químico de grãos e derivados, com classificação automática de conformidade regulatória.")
st.markdown("---")

# 1. BUSCAR FORNECEDORES DO BANCO DE DADOS
fornecedores_df = executar_query("SELECT ID, NomeEmpresa FROM fornecedores ORDER BY NomeEmpresa ASC")

# Lista de insumos disponíveis
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
    # Split Layout (Entradas à esquerda, Monitor Interativo à direita)
    col_inputs, col_monitor = st.columns([5, 5])
    
    with col_inputs:
        st.subheader("📝 Ficha de Inspeção")
        
        # Identificação básica fora de st.form para permitir atualização em tempo real
        analista = st.text_input("Identificação do Analista (Nome / Matrícula)", key="an_analista")
        
        fornecedor_selecionado = st.selectbox(
            "Selecione o Fornecedor *",
            options=fornecedores_df['NomeEmpresa'],
            index=None,
            placeholder="Escolha o fornecedor...",
            key="an_fornecedor"
        )
        
        insumo_selecionado = st.selectbox(
            "Selecione o Insumo Recebido *",
            options=LISTA_INSUMOS,
            index=0,
            key="an_insumo"
        )
        
        col_nf, col_lote = st.columns(2)
        with col_nf:
            nota_fiscal = st.text_input("Número da Nota Fiscal *", key="an_nf")
        with col_lote:
            lote = st.text_input("Lote do Fornecedor *", key="an_lote")
            
        st.divider()
        st.markdown(f"**📊 Parâmetros de Teste para: {insumo_selecionado}**")
        
        # Parâmetros Físico-Químicos básicos
        umidade = st.number_input(
            "Umidade (%) *",
            min_value=0.0,
            max_value=100.0,
            value=12.0,
            step=0.1,
            format="%.1f",
            help="Percentual de umidade detectado no analisador de grãos."
        )
        
        # Inicializando variáveis específicas
        pureza = 100.0
        aflatoxina = 0.0
        capacidade_expansao = 35.0
        peso_hectolitrico = 78.0
        teor_cinzas = 0.5
        teor_ferro = 5.0
        
        # Exibição de campos condicionais baseados no insumo selecionado
        if insumo_selecionado == "Milho em Grão":
            pureza = st.number_input("Pureza (%)", min_value=0.0, max_value=100.0, value=99.0, step=0.1, format="%.1f", help="Mínimo MAPA: 98.0%")
            aflatoxina = st.number_input("Aflatoxina (ppb)", min_value=0.0, value=5.0, step=0.1, format="%.1f", help="Máximo ANVISA: 20.0 ppb")
            
        elif insumo_selecionado == "Milho Pipoca":
            capacidade_expansao = st.number_input("Capacidade de Expansão (ml/g)", min_value=0.0, value=38.0, step=0.1, format="%.1f", help="Mínimo comercial ideal: 30.0 ml/g")
            aflatoxina = st.number_input("Aflatoxina (ppb)", min_value=0.0, value=5.0, step=0.1, format="%.1f", help="Máximo ANVISA: 20.0 ppb")
            
        elif insumo_selecionado == "Soja":
            pureza = st.number_input("Pureza (%)", min_value=0.0, max_value=100.0, value=99.5, step=0.1, format="%.1f", help="Mínimo MAPA: 99.0%")
            
        elif insumo_selecionado == "Trigo":
            peso_hectolitrico = st.number_input("Peso Hectolítrico - PH (kg/hl)", min_value=0.0, max_value=120.0, value=79.0, step=0.1, format="%.1f", help="Mínimo MAPA Tipo 2: 75.0 PH")
            
        elif insumo_selecionado == "Farinha de Trigo":
            teor_cinzas = st.number_input("Teor de Cinzas (%)", min_value=0.0, max_value=10.0, value=0.65, step=0.01, format="%.2f", help="Máximo MAPA Tipo 1: 0.80%")
            teor_ferro = st.number_input("Teor de Ferro (mg/100g)", min_value=0.0, value=5.5, step=0.1, format="%.1f", help="Enriquecimento ANVISA: 4.0 - 9.0 mg/100g")
            
        elif insumo_selecionado == "Farinha de Milho":
            teor_ferro = st.number_input("Teor de Ferro (mg/100g)", min_value=0.0, value=5.5, step=0.1, format="%.1f", help="Enriquecimento ANVISA: 4.0 - 9.0 mg/100g")

        st.markdown("<br>", unsafe_allow_html=True)
        submit_analise = st.button("⚡ Registrar Laudo e Finalizar", type="primary")

        # Processamento do formulário no clique do botão
        if submit_analise:
            if not all([analista, fornecedor_selecionado, nota_fiscal, lote]):
                st.warning("⚠️ Todos os campos de identificação (Analista, Fornecedor, Nota Fiscal, Lote) devem ser preenchidos.")
            else:
                fornecedor_id = fornecedores_df[fornecedores_df['NomeEmpresa'] == fornecedor_selecionado]['ID'].iloc[0]
                
                # Executa motor de decisão final
                status_params = {}
                
                # Regras gerais
                if insumo_selecionado in ["Milho em Grão", "Soja", "Farinha de Milho"]:
                    if umidade <= 14.0:
                        status_params["Umidade"] = ("Aprovado", f"{umidade}%", "Dentro do limite (<= 14.0%)")
                    elif umidade <= 15.0:
                        status_params["Umidade"] = ("Aprovado com Restrição", f"{umidade}%", "Tolerado com desconto (14.1% - 15.0%)")
                    else:
                        status_params["Umidade"] = ("Reprovado", f"{umidade}%", "Excedeu limite (> 15.0%)")
                elif insumo_selecionado == "Milho Pipoca":
                    if 13.5 <= umidade <= 14.5:
                        status_params["Umidade"] = ("Aprovado", f"{umidade}%", "Faixa perfeita (13.5% - 14.5%)")
                    else:
                        status_params["Umidade"] = ("Reprovado", f"{umidade}%", "Fora da faixa ideal (Gera piruá)")
                elif insumo_selecionado == "Trigo":
                    if umidade <= 13.0:
                        status_params["Umidade"] = ("Aprovado", f"{umidade}%", "Dentro do limite (<= 13.0%)")
                    elif umidade <= 14.0:
                        status_params["Umidade"] = ("Aprovado com Restrição", f"{umidade}%", "Tolerado (13.1% - 14.0%)")
                    else:
                        status_params["Umidade"] = ("Reprovado", f"{umidade}%", "Excedeu limite (> 14.0%)")
                elif insumo_selecionado == "Farinha de Trigo":
                    if umidade <= 15.0:
                        status_params["Umidade"] = ("Aprovado", f"{umidade}%", "Dentro da IN 8/2005 (<= 15.0%)")
                    else:
                        status_params["Umidade"] = ("Reprovado", f"{umidade}%", "Farinha úmida (> 15.0%)")

                # Regras específicas
                if insumo_selecionado == "Milho em Grão":
                    status_params["Pureza"] = ("Aprovado" if pureza >= 98.0 else ("Aprovado com Restrição" if pureza >= 97.0 else "Reprovado"), f"{pureza}%", "Mínimo: 98%")
                    status_params["Aflatoxina"] = ("Aprovado" if aflatoxina <= 20.0 else "Reprovado", f"{aflatoxina} ppb", "Máximo: 20 ppb")
                elif insumo_selecionado == "Milho Pipoca":
                    status_params["Expansão"] = ("Aprovado" if capacidade_expansao >= 35.0 else ("Aprovado com Restrição" if capacidade_expansao >= 30.0 else "Reprovado"), f"{capacidade_expansao} ml/g", "Mínimo: 30 ml/g")
                    status_params["Aflatoxina"] = ("Aprovado" if aflatoxina <= 20.0 else "Reprovado", f"{aflatoxina} ppb", "Máximo: 20 ppb")
                elif insumo_selecionado == "Soja":
                    status_params["Pureza"] = ("Aprovado" if pureza >= 99.0 else ("Aprovado com Restrição" if pureza >= 98.0 else "Reprovado"), f"{pureza}%", "Mínimo: 99%")
                elif insumo_selecionado == "Trigo":
                    status_params["Peso Hectolítrico"] = ("Aprovado" if peso_hectolitrico >= 78.0 else ("Aprovado com Restrição" if peso_hectolitrico >= 75.0 else "Reprovado"), f"{peso_hectolitrico} kg/hl", "Mínimo: 75 PH")
                elif insumo_selecionado == "Farinha de Trigo":
                    status_params["Teor de Cinzas"] = ("Aprovado" if teor_cinzas <= 0.8 else ("Aprovado com Restrição" if teor_cinzas <= 1.0 else "Reprovado"), f"{teor_cinzas}%", "Máximo: 0.8%")
                    status_params["Teor de Ferro"] = ("Aprovado" if 4.0 <= teor_ferro <= 9.0 else "Reprovado", f"{teor_ferro} mg", "Faixa: 4.0 - 9.0 mg")
                elif insumo_selecionado == "Farinha de Milho":
                    status_params["Teor de Ferro"] = ("Aprovado" if 4.0 <= teor_ferro <= 9.0 else "Reprovado", f"{teor_ferro} mg", "Faixa: 4.0 - 9.0 mg")

                decisoes = [v[0] for v in status_params.values()]
                if "Reprovado" in decisoes:
                    status_final = "Quarentena"
                elif "Aprovado com Restrição" in decisoes:
                    status_final = "Aprovado com Restrição"
                else:
                    status_final = "Aprovado"

                try:
                    data_hora_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    executar_dml("""
                        INSERT INTO analises (FornecedorID, Insumo, NotaFiscal, LoteFornecedor, Umidade, Pureza, Aflatoxina, CapacidadeExpansao, PesoHectolitrico, TeorCinzas, TeorFerro, StatusLote, Analista, DataHora)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        int(fornecedor_id), insumo_selecionado, nota_fiscal, lote, umidade,
                        pureza, aflatoxina, capacidade_expansao, peso_hectolitrico, teor_cinzas, teor_ferro,
                        status_final, analista, data_hora_agora
                    ))
                    
                    # Atualiza o status do agendamento com base na análise de qualidade
                    executar_dml(
                        "UPDATE agendamentos SET Status = ? WHERE NotaFiscal = ?",
                        (status_final, nota_fiscal)
                    )
                    
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
                    
                    st.success("✅ Laudo de Recebimento registrado com sucesso!")
                    st.toast("Laudo salvo no banco!", icon="🔬")
                    st.rerun()
                except sqlite3.Error as e:
                    st.error(f"Erro ao salvar no banco: {e}")

    with col_monitor:
        st.subheader("🏁 Monitor de Qualidade em Tempo Real")
        
        # Realiza validação dos parâmetros inseridos em tempo real para exibir indicadores visuais
        realtime_status = {}
        
        # Validação Umidade Real-time
        if insumo_selecionado in ["Milho em Grão", "Soja", "Farinha de Milho"]:
            if umidade <= 14.0:
                realtime_status["Umidade"] = ("Aprovado", umidade, 14.0, True) # (status, valor, limite, menor_melhor)
            elif umidade <= 15.0:
                realtime_status["Umidade"] = ("Aprovado com Restrição", umidade, 14.0, True)
            else:
                realtime_status["Umidade"] = ("Reprovado", umidade, 14.0, True)
        elif insumo_selecionado == "Milho Pipoca":
            if 13.5 <= umidade <= 14.5:
                realtime_status["Umidade"] = ("Aprovado", umidade, "13.5% - 14.5%", None)
            else:
                realtime_status["Umidade"] = ("Reprovado", umidade, "13.5% - 14.5%", None)
        elif insumo_selecionado == "Trigo":
            if umidade <= 13.0:
                realtime_status["Umidade"] = ("Aprovado", umidade, 13.0, True)
            elif umidade <= 14.0:
                realtime_status["Umidade"] = ("Aprovado com Restrição", umidade, 13.0, True)
            else:
                realtime_status["Umidade"] = ("Reprovado", umidade, 13.0, True)
        elif insumo_selecionado == "Farinha de Trigo":
            realtime_status["Umidade"] = ("Aprovado" if umidade <= 15.0 else "Reprovado", umidade, 15.0, True)

        # Validação de Parâmetros Específicos Real-time
        if insumo_selecionado == "Milho em Grão":
            realtime_status["Pureza"] = ("Aprovado" if pureza >= 98.0 else ("Aprovado com Restrição" if pureza >= 97.0 else "Reprovado"), pureza, 98.0, False)
            realtime_status["Aflatoxina"] = ("Aprovado" if aflatoxina <= 20.0 else "Reprovado", aflatoxina, 20.0, True)
        elif insumo_selecionado == "Milho Pipoca":
            realtime_status["Capacidade Expansão"] = ("Aprovado" if capacidade_expansao >= 35.0 else ("Aprovado com Restrição" if capacidade_expansao >= 30.0 else "Reprovado"), capacidade_expansao, 30.0, False)
            realtime_status["Aflatoxina"] = ("Aprovado" if aflatoxina <= 20.0 else "Reprovado", aflatoxina, 20.0, True)
        elif insumo_selecionado == "Soja":
            realtime_status["Pureza"] = ("Aprovado" if pureza >= 99.0 else ("Aprovado com Restrição" if pureza >= 98.0 else "Reprovado"), pureza, 99.0, False)
        elif insumo_selecionado == "Trigo":
            realtime_status["Peso Hectolítrico"] = ("Aprovado" if peso_hectolitrico >= 78.0 else ("Aprovado com Restrição" if peso_hectolitrico >= 75.0 else "Reprovado"), peso_hectolitrico, 75.0, False)
        elif insumo_selecionado == "Farinha de Trigo":
            realtime_status["Teor de Cinzas"] = ("Aprovado" if teor_cinzas <= 0.8 else ("Aprovado com Restrição" if teor_cinzas <= 1.0 else "Reprovado"), teor_cinzas, 0.8, True)
            realtime_status["Teor de Ferro"] = ("Aprovado" if 4.0 <= teor_ferro <= 9.0 else "Reprovado", teor_ferro, "4.0 - 9.0", None)
        elif insumo_selecionado == "Farinha de Milho":
            realtime_status["Teor de Ferro"] = ("Aprovado" if 4.0 <= teor_ferro <= 9.0 else "Reprovado", teor_ferro, "4.0 - 9.0", None)

        # Cálculo da decisão provisória baseada nos dados digitados na tela
        rt_decisoes = [v[0] for v in realtime_status.values()]
        if "Reprovado" in rt_decisoes:
            rt_status_final = "Quarentena"
            badge_color = "#e11d48"
            badge_bg = "rgba(225, 29, 72, 0.15)"
        elif "Aprovado com Restrição" in rt_decisoes:
            rt_status_final = "Aprovado com Restrição"
            badge_color = "#ffc107"
            badge_bg = "rgba(255, 193, 7, 0.15)"
        else:
            rt_status_final = "Aprovado"
            badge_color = "#28a745"
            badge_bg = "rgba(40, 167, 69, 0.15)"

        # 1. Card de status dinâmico do lote
        status_card_html = f"""
        <div style="
            background-color: {badge_bg};
            border: 1.5px solid {badge_color};
            border-radius: 12px;
            padding: 18px;
            text-align: center;
            margin-bottom: 24px;
        ">
            <h4 style="margin: 0; font-size: 13px; font-weight: 600; text-transform: uppercase; color: {badge_color};">Status Preliminar do Lote</h4>
            <h2 style="margin: 6px 0 0 0; font-size: 22px; font-weight: 800; text-transform: uppercase; color: {badge_color};">{rt_status_final}</h2>
        </div>
        """
        st.markdown(status_card_html, unsafe_allow_html=True)

        # 2. Exibição das barras de conformidade em HTML para os parâmetros
        st.markdown("**Valores Medidos vs. Limites Legais:**")
        
        for param, (status, val, limit, menor_melhor) in realtime_status.items():
            # Determina cor
            if status == "Aprovado":
                color = "#28a745"
            elif status == "Aprovado com Restrição":
                color = "#ffc107"
            else:
                color = "#dc3545"
                
            # Calcula porcentagem preenchida da barra gráfica de forma segura
            if type(limit) in [int, float] and type(val) in [int, float] and limit > 0:
                if menor_melhor: # Se menor é melhor (ex: umidade, cinzas), mostramos o preenchimento proporcional
                    prog_percent = min(100, max(0, int((val / (limit * 1.3)) * 100)))
                else: # Se maior é melhor (ex: pureza, PH)
                    prog_percent = min(100, max(0, int((val / limit) * 100)))
            else:
                prog_percent = 75 # Fallback para faixas
                
            bar_html = f"""
            <div style="margin-bottom: 16px; font-family: 'Inter', sans-serif;">
                <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
                    <span><b>{param}:</b> {val} (Limite: {limit})</span>
                    <span style="color: {color}; font-weight: 700; text-transform: uppercase; font-size: 11px;">{status}</span>
                </div>
                <div style="background-color: rgba(128, 128, 128, 0.15); border-radius: 10px; height: 8px; width: 100%;">
                    <div style="background-color: {color}; border-radius: 10px; height: 8px; width: {prog_percent}%; transition: width 0.3s ease;"></div>
                </div>
            </div>
            """
            st.markdown(bar_html, unsafe_allow_html=True)
            
        # 3. Painel Regulatório (Reference Box)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("⚖️ **Referências Regulatórias Ativas:**")
            if insumo_selecionado == "Milho em Grão":
                st.caption("- **Limites Físicos**: Instrução Normativa nº 60/2011 do MAPA.")
                st.caption("- **Toxinas (Aflatoxina)**: RDC nº 722/2022 da ANVISA (LMT: 20.0 ppb).")
            elif insumo_selecionado == "Milho Pipoca":
                st.caption("- **Padrão Oficial**: Instrução Normativa nº 61/2011 do MAPA.")
                st.caption("- **Toxinas**: RDC nº 722/2022 da ANVISA (LMT: 20.0 ppb).")
            elif insumo_selecionado == "Soja":
                st.caption("- **Padrão Classificação**: Instrução Normativa nº 11/2007 do MAPA (Mín. 99% pureza).")
            elif insumo_selecionado == "Trigo":
                st.caption("- **Regulamento Técnico**: Instrução Normativa nº 38/2010 do MAPA (Trigo moagem).")
            elif insumo_selecionado == "Farinha de Trigo":
                st.caption("- **Padrão de Identidade**: Instrução Normativa nº 8/2005 do MAPA.")
                st.caption("- **Enriquecimento**: RDC nº 150/2017 da ANVISA (Adição obrigatória de Ferro).")
            elif insumo_selecionado == "Farinha de Milho":
                st.caption("- **Enriquecimento**: RDC nº 150/2017 da ANVISA (Adição de Ferro).")

    # --- HISTÓRICO E DIAGNÓSTICO (Em tela cheia na parte inferior) ---
    st.markdown("---")
    st.subheader("📋 Laudos Registrados Recentemente")
    
    # Aba para alternar visualização do histórico
    tab_hist, tab_detalhes = st.tabs(["Últimas Análises", "Último Laudo Emitido"])
    
    with tab_hist:
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
                    'StatusLote': 'Decisão Final',
                    'Analista': 'Analista',
                    'DataHora': 'Data/Hora'
                })
                st.dataframe(historico_show, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {e}")
            
    with tab_detalhes:
        if "ultima_analise" in st.session_state:
            res = st.session_state.ultima_analise
            
            # Cabeçalho do laudo estruturado
            st.markdown(f"### LAUDO DE INSPEÇÃO TÉCNICA #{res['nota_fiscal']}")
            
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.write(f"🏢 **Fornecedor:** {res['fornecedor']}")
                st.write(f"🌾 **Insumo:** {res['insumo']}")
                st.write(f"📦 **Lote:** {res['lote']}")
            with col_l2:
                st.write(f"👤 **Analista:** {res['analista']}")
                st.write(f"🕒 **Data/Hora:** {res['data_hora']}")
                
                # Badge formatado da decisão
                if res["status_final"] == "Aprovado":
                    st.success(f"**STATUS: APROVADO**")
                elif res["status_final"] in ["Aprovado com Restrição", "Aprovado com Desvio"]:
                    st.warning(f"**STATUS: {res['status_final'].upper()}**")
                elif res["status_final"] == "Quarentena":
                    st.info(f"**STATUS: RETIDO EM QUARENTENA**")
                else:
                    st.error(f"**STATUS: REPROVADO**")
                    
            st.divider()
            st.write("**Parâmetros Analisados:**")
            
            # Loop pelos parâmetros para exibir detalhes textuais do laudo
            for param, (status_param, val_medido, desc) in res["detalhes"].items():
                icon = "🟢" if status_param == "Aprovado" else ("🟡" if status_param == "Aprovado com Restrição" else "🔴")
                st.write(f"{icon} **{param}**: {val_medido} — {status_param} ({desc})")
                
            st.divider()
            
            # Botão para baixar certificado em HTML
            html_cert = gerar_html_certificado(res)
            st.download_button(
                label="📥 Baixar Certificado de Qualidade (HTML)",
                data=html_cert,
                file_name=f"certificado_qualidade_NF_{res['nota_fiscal']}.html",
                mime="text/html",
                help="Gera e baixa um certificado técnico de conformidade imprimível."
            )
        else:
            st.info("Nenhuma análise cadastrada nesta sessão do navegador para visualização de detalhes.")
