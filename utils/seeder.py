# utils/seeder.py

import sqlite3
import random
from datetime import datetime, timedelta
from utils.db import get_connection, inicializar_banco

def popular_banco(limpar_tabelas=True):
    """
    Popula o banco de dados com registros ricos simulando 90 dias de operações:
    cadastro de parceiros, frotas, pesagens de entrada/saída, análises laboratoriais e
    quarentenas liberadas ou recusadas.
    """
    inicializar_banco()
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        if limpar_tabelas:
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DELETE FROM veiculos;")
            cursor.execute("DELETE FROM motoristas;")
            cursor.execute("DELETE FROM agendamentos;")
            cursor.execute("DELETE FROM analises;")
            cursor.execute("DELETE FROM pesagens;")
            cursor.execute("DELETE FROM fornecedores;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            
        # 1. Inserir Fornecedores Estáticos
        fornecedores_dados = [
            ("Cerealista Amambai Ltda", "12.345.678/0001-90", "Rodovia BR-163, Km 45, Dourados - MS", "qualidade@cerealistaamambai.com", "(67) 3421-9988"),
            ("Cooperativa AgroIndustrial Vale", "98.765.432/0001-21", "Av. Paraná, 1200, Cascavel - PR", "recebimento@coopervale.coop.br", "(45) 3220-4400"),
            ("Moinho Central do Brasil S/A", "45.678.901/0001-34", "Rua Industrial, 75, Porto Alegre - RS", "laudos@moinhocentral.com.br", "(51) 3344-5566")
        ]
        
        fornecedor_ids = {}
        for nome, cnpj, end, email, tel in fornecedores_dados:
            cursor.execute("""
                INSERT INTO fornecedores (NomeEmpresa, CNPJ, Endereco, Email, Telefone)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, cnpj, end, email, tel))
            fornecedor_ids[nome] = cursor.lastrowid
            
        # 2. Inserir Motoristas
        motoristas_dados = [
            ("José Carlos Silva", "111.222.333-44", "(45) 99911-2233", fornecedor_ids["Cooperativa AgroIndustrial Vale"]),
            ("Marcos Souza Santos", "555.666.777-88", "(67) 99888-7766", fornecedor_ids["Cerealista Amambai Ltda"]),
            ("Ronaldo de Oliveira", "999.888.777-66", "(51) 98765-4321", fornecedor_ids["Moinho Central do Brasil S/A"]),
            ("Claudio Rodrigues", "222.333.444-55", "(45) 99922-3344", fornecedor_ids["Cooperativa AgroIndustrial Vale"]),
            ("Lucas Mendes Pinto", "777.888.999-00", "(67) 99811-2233", fornecedor_ids["Cerealista Amambai Ltda"])
        ]
        
        motorista_ids = {}
        for nome, cpf, tel, fid in motoristas_dados:
            cursor.execute("""
                INSERT INTO motoristas (Nome, CPF, Telefone, FornecedorID)
                VALUES (?, ?, ?, ?)
            """, (nome, cpf, tel, fid))
            motorista_ids[nome] = cursor.lastrowid
            
        # 3. Inserir Veículos
        veiculos_dados = [
            ("AAA1A11", "Volvo FH 540", "Rodotrem", motorista_ids["José Carlos Silva"]),
            ("BBB2B22", "Scania R450", "Bitrem", motorista_ids["Marcos Souza Santos"]),
            ("CCC3C33", "Mercedes-Benz Actros", "Vanderleia", motorista_ids["Ronaldo de Oliveira"]),
            ("DDD4D44", "Volvo FH 460", "Carreta", motorista_ids["Claudio Rodrigues"]),
            ("EEE5E55", "Scania R500", "Rodotrem", motorista_ids["Lucas Mendes Pinto"])
        ]
        
        for placa, mod, tipo, mid in veiculos_dados:
            cursor.execute("""
                INSERT INTO veiculos (Placa, Modelo, Tipo, MotoristaID)
                VALUES (?, ?, ?, ?)
            """, (placa, mod, tipo, mid))

        # 4. Geração Dinâmica de Dados Históricos (90 dias)
        hoje = datetime.now().date()
        random.seed(42) # semente para consistência
        
        LISTA_INSUMOS = ["Milho em Grão", "Soja", "Trigo", "Farinha de Trigo", "Farinha de Milho", "Milho Pipoca"]
        
        for d in range(90, -3, -1): # de 90 dias atrás até 2 dias no futuro
            data_corrente = hoje - timedelta(days=d)
            data_corrente_str = data_corrente.strftime('%Y-%m-%d')
            
            # Número de caminhões programados para o dia (1 a 4)
            num_cargas = random.randint(1, 4)
            
            for i in range(num_cargas):
                # Escolhe fornecedor e insumo aleatórios
                forn_nome = random.choice(list(fornecedor_ids.keys()))
                forn_cnpj = [f[1] for f in fornecedores_dados if f[0] == forn_nome][0]
                fid = fornecedor_ids[forn_nome]
                
                insumo = random.choice(LISTA_INSUMOS)
                
                # Escolhe veículo/motorista condizente com o fornecedor
                candidatos_mot = [m for m in motoristas_dados if m[3] == fid]
                mot_nome = random.choice(candidatos_mot)[0]
                placa = [v[0] for v in veiculos_dados if v[3] == motorista_ids[mot_nome]][0]
                
                # Volume da carga
                vol_nf = float(random.choice([32000, 36000, 40000, 48000]))
                
                # Nota fiscal única
                nf_num = f"NF-{data_corrente.strftime('%y%m%d')}{i+1:02d}"
                
                # Horário do agendamento
                data_cadastro = (data_corrente - timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d 10:00:00')
                
                # Define status regulatórios laboratoriais e logísticos
                # 85% Conformes, 10% Quarentena/Desvio, 5% Reprovados
                rand_qual = random.random()
                if rand_qual < 0.85:
                    umi = round(random.uniform(11.5, 13.9), 1)
                    status_qualidade = "Aprovado"
                elif rand_qual < 0.95:
                    umi = round(random.uniform(14.1, 15.0), 1)
                    status_qualidade = "Aprovado com Restrição"
                elif rand_qual < 0.98:
                    umi = round(random.uniform(15.1, 15.5), 1)
                    status_qualidade = "Quarentena"  # Irá virar Aprovado com Desvio ou Reprovado no histórico
                else:
                    umi = round(random.uniform(15.6, 16.5), 1)
                    status_qualidade = "Reprovado"

                # Define status final logístico baseado no tempo (passado vs hoje vs futuro)
                if data_corrente < hoje:
                    # Cargas passadas são fechadas/concluídas ou recusadas
                    if status_qualidade == "Quarentena":
                        # No passado, a quarentena já foi resolvida (Aprovado com Desvio ou Reprovado)
                        final_status = random.choice(["Aprovado com Desvio", "Reprovado"])
                    else:
                        final_status = "Concluído" if status_qualidade in ["Aprovado", "Aprovado com Restrição"] else "Reprovado"
                elif data_corrente == hoje:
                    # Cargas de hoje podem estar em qualquer etapa do fluxo
                    final_status = random.choice(["Pendente", "Em Pesagem", "Quarentena", "Concluído"])
                else:
                    # Futuras estão pendentes
                    final_status = "Pendente"
                
                # Insere o agendamento no banco
                cursor.execute("""
                    INSERT INTO agendamentos (FornecedorCNPJ, TipoInsumo, QuantidadeEsperada, PlacaCaminhao, NomeMotorista, NotaFiscal, DataAgendada, Status, DataCadastro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (forn_cnpj, insumo, vol_nf, placa, mot_nome, nf_num, data_corrente_str, final_status, data_cadastro))
                agendamento_id = cursor.lastrowid
                
                # Insere dados de pesagem e análise se a carga passou da entrada (Concluído, Desvio, Reprovado, Em Pesagem)
                if final_status in ["Concluído", "Aprovado com Desvio", "Reprovado", "Em Pesagem", "Quarentena"]:
                    # Pesagem de Entrada
                    peso_bruto = vol_nf + 15000.0 + random.randint(-150, 150) # tara aproximada de 15t
                    data_hora_entrada = f"{data_corrente_str} {random.choice(['08:15:00', '09:30:00', '10:45:00', '14:20:00'])}"
                    
                    if final_status in ["Concluído", "Aprovado com Desvio", "Reprovado"] or (final_status == "Quarentena" and random.choice([True, False])):
                        # Carga já pesou a saída
                        peso_tara = 15000.0
                        peso_liquido = peso_bruto - peso_tara
                        diff_percent = ((peso_liquido - vol_nf) / vol_nf) * 100
                        data_hora_saida = f"{data_corrente_str} {random.choice(['11:00:00', '12:30:00', '13:15:00', '16:45:00'])}"
                    else:
                        # Carga ainda na planta (apenas entrada pesada)
                        peso_tara = None
                        peso_liquido = None
                        diff_percent = None
                        data_hora_saida = None
                        
                    cursor.execute("""
                        INSERT INTO pesagens (AgendamentoID, PesoBruto, PesoTara, PesoLiquido, PesoNotaFiscal, DiferencaPercentual, DataHoraEntrada, DataHoraSaida)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (agendamento_id, peso_bruto, peso_tara, peso_liquido, vol_nf, diff_percent, data_hora_entrada, data_hora_saida))
                    
                    # Insere a Análise Química correspondente
                    if final_status != "Em Pesagem":
                        # Gera parâmetros adicionais consistentes
                        pureza = round(random.uniform(98.2, 99.8), 1) if insumo in ["Milho em Grão", "Soja"] else None
                        aflatoxina = round(random.uniform(2.0, 15.0), 1) if insumo in ["Milho em Grão", "Milho Pipoca"] else None
                        expansao = round(random.uniform(32.0, 42.0), 1) if insumo == "Milho Pipoca" else None
                        ph = round(random.uniform(76.0, 82.0), 1) if insumo == "Trigo" else None
                        cinzas = round(random.uniform(0.4, 0.75), 2) if insumo == "Farinha de Trigo" else None
                        ferro = round(random.uniform(4.5, 8.5), 1) if insumo in ["Farinha de Trigo", "Farinha de Milho"] else None
                        
                        analista = random.choice(["Roberto Souza", "Ana Lúcia"])
                        status_lote_efetivo = final_status if final_status in ["Aprovado com Desvio", "Reprovado"] else status_qualidade
                        
                        # Tratamento para desvios e quarentenas do passado
                        desvio_liberado = 0
                        desvio_aut = None
                        desvio_just = None
                        desvio_dt = None
                        
                        if final_status == "Aprovado com Desvio":
                            desvio_liberado = 1
                            desvio_aut = "Roberto Souza"
                            desvio_just = f"Liberado sob desvio com desconto comercial de 2.0%. Motivo: Umidade de {umi}% acima do limite padrão."
                            desvio_dt = data_hora_entrada
                        elif final_status == "Reprovado" and status_qualidade == "Quarentena":
                            desvio_liberado = 0
                            desvio_aut = "Ana Lúcia"
                            desvio_just = f"Reprovado na quarentena. Motivo: Umidade de {umi}% inviabiliza armazenamento."
                            desvio_dt = data_hora_entrada
                            
                        cursor.execute("""
                            INSERT INTO analises (FornecedorID, Insumo, NotaFiscal, LoteFornecedor, Umidade, Pureza, Aflatoxina, CapacidadeExpansao, PesoHectolitrico, TeorCinzas, TeorFerro, StatusLote, Analista, DataHora, DesvioLiberado, DesvioAutorizador, DesvioJustificativa, DesvioDataHora)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (fid, insumo, nf_num, f"LOTE-{data_corrente.strftime('%y')}-{random.randint(100, 999)}", umi, pureza, aflatoxina, expansao, ph, cinzas, ferro, status_lote_efetivo, analista, data_hora_entrada, desvio_liberado, desvio_aut, desvio_just, desvio_dt))
                        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro no Seeder Avançado: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
