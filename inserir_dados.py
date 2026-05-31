# inserir_dados.py

import sys
from utils.seeder import popular_banco

if __name__ == "__main__":
    print("=" * 45)
    print("QualiHub - Carga Rápida de Dados de Teste")
    print("=" * 45)
    
    # Executa o seeder
    sucesso = popular_banco(limpar_tabelas=True)
    
    if sucesso:
        print("\n✅ Banco de dados limpo e populado com sucesso!")
        print("  -> Fornecedores criados.")
        print("  -> Motoristas e veículos cadastrados.")
        print("  -> Agendamentos registrados.")
        print("  -> Laudos de análises físico-químicas gerados.")
        print("\nVocê já pode abrir o site e visualizar os dados operacionais!")
    else:
        print("\n❌ Falha ao popular o banco de dados. Verifique a conexão com o SQLite.")
        sys.exit(1)
    
    print("=" * 45)