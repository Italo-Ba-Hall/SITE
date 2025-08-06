#!/usr/bin/env python3
"""
Script para configurar a API Key do Groq
/-HALL-DEV Backend
"""

import os
import getpass

def setup_api_key():
    """Configura a API key do Groq"""
    
    print("🔑 Configuração da API Key do Groq")
    print("=" * 40)
    
    # Verificar se já existe
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'GROQ_API_KEY=' in content:
                print("⚠️  API Key já configurada no arquivo .env")
                response = input("Deseja sobrescrever? (s/N): ").lower()
                if response != 's':
                    print("❌ Configuração cancelada")
                    return
    
    print("\n📋 Para obter sua API Key:")
    print("1. Acesse: https://console.groq.com/")
    print("2. Faça login ou crie uma conta")
    print("3. Vá para 'API Keys'")
    print("4. Clique em 'Create API Key'")
    print("5. Copie a chave (formato: gsk_...)")
    
    print("\n🔐 Digite sua API Key (será ocultada):")
    api_key = getpass.getpass("API Key: ").strip()
    
    if not api_key:
        print("❌ API Key não fornecida")
        return
    
    if not api_key.startswith('gsk_'):
        print("⚠️  Aviso: API Key deve começar com 'gsk_'")
        response = input("Continuar mesmo assim? (s/N): ").lower()
        if response != 's':
            print("❌ Configuração cancelada")
            return
    
    # Criar arquivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(f'GROQ_API_KEY={api_key}\n')
    
    print("\n✅ API Key configurada com sucesso!")
    print("📁 Arquivo .env criado/atualizado")
    
    # Testar configuração
    print("\n🧪 Testando configuração...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        if 'GROQ_API_KEY' in os.environ:
            print("✅ Variável de ambiente carregada")
            
            # Testar se a chave é válida
            import groq
            try:
                client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
                print("✅ Cliente Groq criado com sucesso")
                print("✅ API Key válida!")
            except Exception as e:
                print(f"⚠️  Erro ao criar cliente Groq: {str(e)}")
                print("💡 Verifique se a API Key está correta")
        else:
            print("❌ Variável de ambiente não encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao testar configuração: {str(e)}")

if __name__ == "__main__":
    setup_api_key() 