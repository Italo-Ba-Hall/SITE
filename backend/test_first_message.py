#!/usr/bin/env python3
"""
Teste para verificar se o bot responde ao conteúdo da primeira mensagem
/-HALL-DEV Backend
"""

import asyncio

from llm_service import llm_service
from schemas import ChatMessage, LLMRequest, MessageRole


async def test_first_message_response():
    """Testa se o bot responde ao conteúdo da primeira mensagem"""
    print("🧪 Testando resposta à primeira mensagem...")

    # Simular primeira mensagem do usuário
    first_message = "Preciso de um sistema de automação para minha empresa"

    # Criar contexto com mensagem de boas-vindas
    messages = [
        ChatMessage(
            role=MessageRole.ASSISTANT,
            content="👋 Olá! Que prazer em conhecê-lo!\n\n❓ Para te ajudar melhor, me conte:\n\n• Que tipo de processo você gostaria de melhorar?\n• Qual é o maior desafio que está enfrentando?\n\n💡 Assim posso entender exatamente como posso te ajudar!",
        )
    ]

    # Testar resposta para primeira mensagem específica
    request = LLMRequest(
        session_id="test-first-message",
        message=first_message,
        context={"messages": messages},
    )

    try:
        response = await llm_service.generate_response(request)
        print(f"✅ Resposta do LLM: {response.message}")

        # Verificar se a resposta menciona automação
        if (
            "automação" in response.message.lower()
            or "automatização" in response.message.lower()
        ):
            print("✅ Bot respondeu ao conteúdo da primeira mensagem (automação)")
        else:
            print("⚠️ Bot pode não estar respondendo ao conteúdo específico")

        # Verificar se é conciso
        if len(response.message.split()) < 50:
            print("✅ Resposta é concisa")
        else:
            print("⚠️ Resposta pode estar muito longa")

    except Exception as e:
        print(f"❌ Erro ao testar primeira mensagem: {e!s}")


async def test_generic_first_message():
    """Testa resposta para mensagem genérica"""
    print("\n🧪 Testando resposta para mensagem genérica...")

    # Simular mensagem genérica
    generic_message = "Olá"

    # Criar contexto com mensagem de boas-vindas
    messages = [
        ChatMessage(
            role=MessageRole.ASSISTANT,
            content="👋 Olá! Que prazer em conhecê-lo!\n\n❓ Para te ajudar melhor, me conte:\n\n• Que tipo de processo você gostaria de melhorar?\n• Qual é o maior desafio que está enfrentando?\n\n💡 Assim posso entender exatamente como posso te ajudar!",
        )
    ]

    # Testar resposta para mensagem genérica
    request = LLMRequest(
        session_id="test-generic-message",
        message=generic_message,
        context={"messages": messages},
    )

    try:
        response = await llm_service.generate_response(request)
        print(f"✅ Resposta do LLM: {response.message}")

        # Verificar se faz perguntas estratégicas
        if "?" in response.message:
            print("✅ Bot faz perguntas estratégicas")
        else:
            print("⚠️ Bot pode não estar fazendo perguntas")

    except Exception as e:
        print(f"❌ Erro ao testar mensagem genérica: {e!s}")


async def main():
    """Executa os testes"""
    print("🚀 Testando respostas do bot...\n")

    await test_first_message_response()
    await test_generic_first_message()

    print("\n🎯 Testes concluídos!")


if __name__ == "__main__":
    asyncio.run(main())
