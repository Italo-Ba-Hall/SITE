#!/usr/bin/env python3
"""
Teste Rápido de Performance e Funcionalidades
/-HALL-DEV Backend
"""

import asyncio
import time
from datetime import datetime, timedelta
from chat_manager import chat_manager
from llm_service import llm_service
from database import db_manager

async def test_timeout_system():
    """Testa o sistema de timeout e avisos de inatividade"""
    print("🧪 Testando sistema de timeout...")
    
    # Criar sessão
    session = chat_manager.create_session()
    session_id = session.session_id
    print(f"✅ Sessão criada: {session_id}")
    
    # Simular mensagem inicial
    chat_manager.add_message(session_id, "user", "Olá, preciso de ajuda")
    print("✅ Mensagem inicial adicionada")
    
    # Verificar aviso de inatividade (deve retornar None inicialmente)
    warning = chat_manager.check_inactivity_warning(session_id)
    print(f"⚠️ Aviso de inatividade: {warning is not None}")
    
    # Simular tempo passado (modificar updated_at para 11 minutos atrás)
    session.updated_at = datetime.now() - timedelta(minutes=11)
    
    # Verificar aviso de inatividade novamente
    warning = chat_manager.check_inactivity_warning(session_id)
    if warning:
        print(f"⚠️ Aviso de inatividade: {warning[:100]}...")
    else:
        print("❌ Aviso de inatividade não foi gerado")
    
    # Simular tempo passado (modificar updated_at para 16 minutos atrás)
    session.updated_at = datetime.now() - timedelta(minutes=16)
    
    # Verificar se sessão expirou
    expired_session = chat_manager.get_session(session_id)
    if expired_session is None:
        print("✅ Sessão expirou corretamente")
    else:
        print("❌ Sessão não expirou quando deveria")
    
    print("🎯 Teste de timeout concluído!\n")

async def test_conversation_summary():
    """Testa o sistema de resumo de conversa"""
    print("🧪 Testando sistema de resumo de conversa...")
    
    # Criar sessão
    session = chat_manager.create_session()
    session_id = session.session_id
    
    # Adicionar algumas mensagens
    chat_manager.add_message(session_id, "user", "Preciso de um sistema de automação")
    chat_manager.add_message(session_id, "assistant", "Entendo! Que tipo de processo você gostaria de automatizar?")
    chat_manager.add_message(session_id, "user", "Processos manuais repetitivos")
    chat_manager.add_message(session_id, "assistant", "Perfeito! Posso ajudar com RPA. Qual é seu nome?")
    
    # Finalizar sessão sem email (deve salvar apenas resumo)
    ended_session = chat_manager.end_session(session_id, "test")
    
    if ended_session:
        print("✅ Sessão finalizada com sucesso")
        
        # Verificar se resumo foi salvo
        summary = db_manager.get_conversation_summary(session_id)
        if summary:
            print(f"✅ Resumo salvo: {summary['summary'][:100]}...")
        else:
            print("❌ Resumo não foi salvo")
    else:
        print("❌ Erro ao finalizar sessão")
    
    print("🎯 Teste de resumo concluído!\n")

async def test_lead_with_email():
    """Testa o sistema de lead com email"""
    print("🧪 Testando sistema de lead com email...")
    
    # Criar sessão
    session = chat_manager.create_session()
    session_id = session.session_id
    
    # Adicionar perfil de usuário com email
    chat_manager.update_user_profile(session_id, {
        "name": "João Silva",
        "email": "joao@exemplo.com",
        "company": "Empresa Teste",
        "role": "Gerente"
    })
    
    # Adicionar mensagens
    chat_manager.add_message(session_id, "user", "Preciso de um dashboard de BI")
    chat_manager.add_message(session_id, "assistant", "Ótimo! Que tipo de dados você gostaria de visualizar?")
    chat_manager.add_message(session_id, "user", "Dados de vendas e performance")
    
    # Finalizar sessão com email (deve salvar lead completo)
    ended_session = chat_manager.end_session(session_id, "test_with_email")
    
    if ended_session:
        print("✅ Sessão finalizada com sucesso")
        
        # Verificar se lead foi salvo
        lead = db_manager.get_lead(session_id)
        if lead:
            print(f"✅ Lead salvo: {lead['name']} - {lead['email']}")
            print(f"📊 Score de qualificação: {lead['qualification_score']}")
        else:
            print("❌ Lead não foi salvo")
    else:
        print("❌ Erro ao finalizar sessão")
    
    print("🎯 Teste de lead concluído!\n")

async def test_llm_personality():
    """Testa a nova personalidade do LLM"""
    print("🧪 Testando nova personalidade do LLM...")
    
    from schemas import LLMRequest, ChatMessage, MessageRole
    
    # Criar contexto de conversa
    messages = [
        ChatMessage(
            role=MessageRole.ASSISTANT,
            content="👋 Olá! Que prazer em conhecê-lo!\n\nSou o assistente da /-HALL-DEV, especialista em soluções tecnológicas.\n\n❓ Para te ajudar melhor, me conte:\n\n• Que tipo de processo você gostaria de melhorar?\n• Qual é o maior desafio que está enfrentando?\n\n💡 Assim posso entender exatamente como posso te ajudar!"
        )
    ]
    
    # Testar resposta para mensagem do usuário
    request = LLMRequest(
        session_id="test-session",
        message="Preciso de ajuda com automação",
        context={"messages": messages}
    )
    
    try:
        response = await llm_service.generate_response(request)
        print(f"✅ Resposta do LLM: {response.message[:200]}...")
        
        # Verificar se a resposta é concisa e faz perguntas
        if "?" in response.message and len(response.message) < 500:
            print("✅ Resposta é concisa e faz perguntas")
        else:
            print("⚠️ Resposta pode não estar seguindo o padrão conciso")
            
    except Exception as e:
        print(f"❌ Erro ao testar LLM: {str(e)}")
    
    print("🎯 Teste de personalidade concluído!\n")

async def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes de funcionalidades...\n")
    
    start_time = time.time()
    
    # Executar testes
    await test_timeout_system()
    await test_conversation_summary()
    await test_lead_with_email()
    await test_llm_personality()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Todos os testes concluídos em {duration:.2f} segundos!")
    print("🎯 Sistema pronto para uso!")

if __name__ == "__main__":
    asyncio.run(main()) 