# utils/seeder.py

import sqlite3
from datetime import datetime, timedelta
from utils.db import get_connection, inicializar_banco

def popular_banco(limpar_tabelas=True):
    """
    Popula o banco de dados com registros fictícios ricos para testes de interface.
    Se limpar_tabelas for True, esvazia as tabelas antes de popular.
    """
    # Garante a inicialização das tabelas e migrações antes de inserir
    inicializar_banco()
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        if limpar_tabelas:
            # Desativa restrições temporariamente para limpar as tabelas com integridade
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DELETE FROM veiculos;")
            cursor.execute("DELETE FROM motoristas;")
            cursor.execute("DELETE FROM agendamentos;")
            cursor.execute("DELETE FROM analises;")
            cursor.execute("DELETE FROM fornecedores;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            
        # 1. Inserir Fornecedores
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
            ("Ronaldo de Oliveira", "999.888.777-66", "(51) 98765-4321", fornecedor_ids["Moinho Central do Brasil S/A"])
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
            ("CCC3C33", "Mercedes-Benz Actros", "Vanderleia", motorista_ids["Ronaldo de Oliveira"])
        ]
        
        for placa, mod, tipo, mid in veiculos_dados:
            cursor.execute("""
                INSERT INTO veiculos (Placa, Modelo, Tipo, MotoristaID)
                VALUES (?, ?, ?, ?)
            """, (placa, mod, tipo, mid))
            
        # 4. Inserir Agendamentos
        hoje = datetime.now()
        amanha = hoje + timedelta(days=1)
        agendamentos_dados = [
            ("12.345.678/0001-90", "Milho em Grão", 36000.0, "BBB2B22", "Marcos Souza Santos", "NF-99881", hoje.strftime('%Y-%m-%d'), "Pendente"),
            ("98.765.432/0001-21", "Soja em Grão", 48000.0, "AAA1A11", "José Carlos Silva", "NF-55442", hoje.strftime('%Y-%m-%d'), "Pendente"),
            ("45.678.901/0001-34", "Trigo em Grão", 32000.0, "CCC3C33", "Ronaldo de Oliveira", "NF-11223", amanha.strftime('%Y-%m-%d'), "Pendente")
        ]
        
        for cnpj, insumo, qtd, placa, mot, nf, data, status in agendamentos_dados:
            cursor.execute("""
                INSERT INTO agendamentos (FornecedorCNPJ, TipoInsumo, QuantidadeEsperada, PlacaCaminhao, NomeMotorista, NotaFiscal, DataAgendada, Status, DataCadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cnpj, insumo, qtd, placa, mot, nf, data, status, hoje.strftime('%Y-%m-%d %H:%M:%S')))
            
        # 5. Inserir Análises (com diferentes insumos e status finais)
        analises_dados = [
            # 1. Milho em Grão - Aprovado
            (fornecedor_ids["Cerealista Amambai Ltda"], "Milho em Grão", "NF-99881", "LOTE-2026-A1", 13.2, 98.5, 12.0, None, None, None, None, "Aprovado", "Roberto Souza", hoje.strftime('%Y-%m-%d %H:%M:%S')),
            # 2. Soja - Aprovado com Restrição (por umidade levemente alta)
            (fornecedor_ids["Cooperativa AgroIndustrial Vale"], "Soja", "NF-55442", "LOTE-2026-B5", 14.5, 98.2, None, None, None, None, None, "Aprovado com Restrição", "Ana Lúcia", (hoje - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')),
            # 3. Milho Pipoca - Aprovado (Capacidade expansão > 35)
            (fornecedor_ids["Cerealista Amambai Ltda"], "Milho Pipoca", "NF-99881", "LOTE-2026-P1", 13.8, None, 8.0, 38.0, None, None, None, "Aprovado", "Roberto Souza", (hoje - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')),
            # 4. Trigo - Aprovado com Restrição (PH 74.0)
            (fornecedor_ids["Moinho Central do Brasil S/A"], "Trigo", "NF-11223", "LOTE-2026-T1", 12.5, 99.0, None, None, 74.0, None, None, "Aprovado com Restrição", "Roberto Souza", (hoje - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')),
            # 5. Farinha de Trigo - Aprovado (Enriquecida)
            (fornecedor_ids["Moinho Central do Brasil S/A"], "Farinha de Trigo", "NF-11224", "LOTE-2026-F3", 14.2, None, None, None, None, 0.55, 6.2, "Aprovado", "Ana Lúcia", (hoje - timedelta(days=1, hours=4)).strftime('%Y-%m-%d %H:%M:%S')),
            # 6. Farinha de Milho - Reprovado (Falta Ferro / Abaixo de 4.0 mg)
            (fornecedor_ids["Cooperativa AgroIndustrial Vale"], "Farinha de Milho", "NF-55445", "LOTE-2026-FM8", 13.5, None, None, None, None, None, 2.5, "Reprovado", "Ana Lúcia", (hoje - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'))
        ]
        
        for fid, insumo, nf, lote, umi, pur, afl, capex, ph, cin, fer, status, analista, data in analises_dados:
            cursor.execute("""
                INSERT INTO analises (FornecedorID, Insumo, NotaFiscal, LoteFornecedor, Umidade, Pureza, Aflatoxina, CapacidadeExpansao, PesoHectolitrico, TeorCinzas, TeorFerro, StatusLote, Analista, DataHora)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (fid, insumo, nf, lote, umi, pur, afl, capex, ph, cin, fer, status, analista, data))
            
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro no Seeder: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
