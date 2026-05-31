# utils/db.py

import sqlite3
import pandas as pd
import os

DB_NAME = "fornecedores.db"

def get_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    """
    Inicializa todas as tabelas do sistema se elas não existirem.
    Centraliza a criação do schema do banco de dados.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Tabela de Fornecedores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NomeEmpresa TEXT NOT NULL,
            CNPJ TEXT UNIQUE NOT NULL,
            Endereco TEXT,
            Email TEXT,
            Telefone TEXT
        );
        """)
        
        # 2. Tabela de Motoristas
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
        
        # 3. Tabela de Veículos
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
        
        # 4. Tabela de Agendamentos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FornecedorCNPJ TEXT NOT NULL,
            TipoInsumo TEXT NOT NULL,
            QuantidadeEsperada REAL NOT NULL,
            PlacaCaminhao TEXT NOT NULL,
            NomeMotorista TEXT,
            NotaFiscal TEXT UNIQUE,
            DataAgendada TEXT NOT NULL,
            Status TEXT NOT NULL,
            DataCadastro TEXT NOT NULL,
            FOREIGN KEY (FornecedorCNPJ) REFERENCES fornecedores (CNPJ)
        );
        """)

        # 5. Tabela de Análises
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analises (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FornecedorID INTEGER NOT NULL,
            Insumo TEXT NOT NULL,
            NotaFiscal TEXT NOT NULL,
            LoteFornecedor TEXT NOT NULL,
            Umidade REAL NOT NULL,
            Pureza REAL,
            Aflatoxina REAL,
            CapacidadeExpansao REAL,
            PesoHectolitrico REAL,
            TeorCinzas REAL,
            TeorFerro REAL,
            StatusLote TEXT NOT NULL,
            Analista TEXT NOT NULL,
            DataHora TEXT NOT NULL,
            FOREIGN KEY (FornecedorID) REFERENCES fornecedores (ID)
        );
        """)

        # Código de migração de banco para compatibilidade se o banco já existir
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analises';")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(analises);")
            columns = [col[1] for col in cursor.fetchall()]
            if "Insumo" not in columns:
                cursor.execute("ALTER TABLE analises ADD COLUMN Insumo TEXT NOT NULL DEFAULT 'Milho em Grão';")
            if "NotaFiscal" not in columns:
                cursor.execute("ALTER TABLE analises ADD COLUMN NotaFiscal TEXT DEFAULT '';")
            if "CapacidadeExpansao" not in columns:
                cursor.execute("ALTER TABLE analises ADD COLUMN CapacidadeExpansao REAL;")
            if "PesoHectolitrico" not in columns:
                cursor.execute("ALTER TABLE analises ADD COLUMN PesoHectolitrico REAL;")
            if "TeorCinzas" not in columns:
                cursor.execute("ALTER TABLE analises ADD COLUMN TeorCinzas REAL;")
            if "TeorFerro" not in columns:
                cursor.execute("ALTER TABLE analises ADD COLUMN TeorFerro REAL;")
        
        conn.commit()

def executar_query(query, params=()):
    """
    Executa uma consulta SELECT e retorna os resultados como um DataFrame do Pandas.
    Garante o fechamento correto da conexão.
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

def executar_dml(query, params=()):
    """
    Executa uma instrução DML (INSERT, UPDATE, DELETE) e retorna o ID do último registro inserido.
    Lança exceções do SQLite para controle detalhado na camada de interface.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
