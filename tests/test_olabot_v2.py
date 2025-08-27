#!/usr/bin/env python3
"""
Script de Teste para OLABOT v2 - Sistema de Engenharia de Prompt
===============================================================

Este script testa todas as funcionalidades do novo sistema OLABOT
incluindo engenharia de prompt, detecção de contexto e otimização de respostas.

Uso:
    python test_olabot.py
"""

import os
import sys
import time
from typing import Dict, List

# Adicionar diretório pai ao path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_functionality():
    """Testa funcionalidades básicas do OLABOT."""
    print("🧪 Testando Funcionalidades Básicas...")
    
    try:
        from olasis.chatbot_v2 import OlaBot
        
        # Inicializar sem API key para teste de fallback
        bot = OlaBot(api_key=None, enable_prompt_engineering=True)
        
        # Teste de disponibilidade
        print(f"   ✅ Disponibilidade: {bot.is_available}")
        
        # Teste de resposta de fallback
        response = bot.ask("O que é inteligência artificial?")
        assert len(response) > 50, "Resposta muito curta"
        print(f"   ✅ Resposta de fallback: {len(response)} caracteres")
        
        # Teste de estatísticas
        stats = bot.get_session_stats()
        assert "total_queries" in stats, "Estatísticas incompletas"
        print(f"   ✅ Estatísticas: {stats['total_queries']} consultas")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_prompt_engineering():
    """Testa sistema de engenharia de prompt."""
    print("🧪 Testando Engenharia de Prompt...")
    
    try:
        from olasis.prompt_engineering import PromptBuilder, ResponseOptimizer
        
        # Teste do construtor de prompts
        builder = PromptBuilder()
        
        # Teste de detecção de contexto
        contexts = [
            ("Como buscar artigos sobre IA?", "search"),
            ("O que é machine learning?", "concept"),
            ("Qual metodologia usar?", "methodology"),
            ("Estou começando minha pesquisa", "general")
        ]
        
        for message, expected in contexts:
            detected = builder.detect_context_type(message)
            print(f"   ✅ '{message[:30]}...' → {detected}")
        
        # Teste de construção de prompt
        prompt = builder.build_contextual_prompt(
            user_message="Como fazer uma revisão sistemática?",
            context_type="methodology"
        )
        assert "OLABOT" in prompt, "Prompt não contém identidade"
        assert "metodologia" in prompt.lower(), "Prompt não contém contexto apropriado"
        print(f"   ✅ Prompt construído: {len(prompt)} caracteres")
        
        # Teste do otimizador de respostas
        optimizer = ResponseOptimizer()
        
        test_response = "**Isso** é um *teste* com ### markdown"
        cleaned = optimizer.format_response(test_response)
        assert "**" not in cleaned, "Markdown não removido"
        print(f"   ✅ Limpeza de markdown: '{test_response}' → '{cleaned}'")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_context_detection():
    """Testa detecção automática de contexto."""
    print("🧪 Testando Detecção de Contexto...")
    
    try:
        from olasis.prompt_engineering import PromptBuilder
        
        builder = PromptBuilder()
        
        test_cases = [
            # Busca
            ("Onde encontrar artigos sobre diabetes?", "search"),
            ("Como procurar estudos de sustentabilidade?", "search"),
            ("Preciso buscar literatura sobre AI", "search"),
            
            # Metodologia
            ("Como fazer análise qualitativa?", "methodology"),
            ("Qual procedimento usar para coleta de dados?", "methodology"),
            ("Que metodologia é melhor para meu estudo?", "methodology"),
            
            # Conceito
            ("O que significa revisão sistemática?", "concept"),
            ("Defina inteligência artificial", "concept"),
            ("Explique o conceito de big data", "concept"),
            
            # Geral
            ("Estou começando meu doutorado", "general"),
            ("Preciso de ajuda com minha tese", "general")
        ]
        
        correct_detections = 0
        for message, expected in test_cases:
            detected = builder.detect_context_type(message)
            is_correct = detected == expected
            status = "✅" if is_correct else "❌"
            print(f"   {status} '{message[:40]}...' → {detected} (esperado: {expected})")
            if is_correct:
                correct_detections += 1
        
        accuracy = (correct_detections / len(test_cases)) * 100
        print(f"   📊 Precisão da detecção: {accuracy:.1f}% ({correct_detections}/{len(test_cases)})")
        
        return accuracy > 80  # Pelo menos 80% de precisão
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_response_quality():
    """Testa validação de qualidade das respostas."""
    print("🧪 Testando Validação de Qualidade...")
    
    try:
        from olasis.prompt_engineering import ResponseOptimizer
        
        optimizer = ResponseOptimizer()
        
        test_responses = [
            # Resposta boa
            ("Esta é uma resposta completa e útil sobre pesquisa científica. Recomendo consultar fontes confiáveis e usar métodos apropriados para sua investigação.", True),
            
            # Resposta muito curta
            ("Ok", False),
            
            # Resposta com markdown
            ("**Esta** resposta tem *formatação* ### indevida", False),
            
            # Resposta muito longa (simulada)
            ("x" * 3000, False),
            
            # Resposta sem conteúdo português
            ("This is an English response without Portuguese content", False)
        ]
        
        passed_tests = 0
        for response, should_pass in test_responses:
            validation = optimizer.validate_response_quality(response)
            overall_quality = all(validation.values())
            
            status = "✅" if (overall_quality == should_pass) else "❌"
            print(f"   {status} Qualidade: {validation}")
            
            if overall_quality == should_pass:
                passed_tests += 1
        
        success_rate = (passed_tests / len(test_responses)) * 100
        print(f"   📊 Taxa de sucesso: {success_rate:.1f}%")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_integration():
    """Testa integração com sistema existente."""
    print("🧪 Testando Integração...")
    
    try:
        # Teste de importação compatível
        from olasis import Chatbot, OlaBot
        
        # Testar que Chatbot ainda funciona (compatibilidade)
        old_bot = Chatbot(api_key=None)
        response = old_bot.ask("Teste")
        print(f"   ✅ Compatibilidade Chatbot: {len(response)} caracteres")
        
        # Testar novo OlaBot
        new_bot = OlaBot(api_key=None)
        response = new_bot.ask("Teste")
        print(f"   ✅ Novo OlaBot: {len(response)} caracteres")
        
        # Verificar que são diferentes (novo tem mais funcionalidades)
        assert hasattr(new_bot, 'get_session_stats'), "OlaBot sem métodos avançados"
        assert hasattr(new_bot, 'set_temperature'), "OlaBot sem configuração"
        print(f"   ✅ Funcionalidades avançadas disponíveis")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def performance_test():
    """Teste de performance básico."""
    print("🧪 Testando Performance...")
    
    try:
        from olasis.chatbot_v2 import OlaBot
        from olasis.prompt_engineering import PromptBuilder
        
        bot = OlaBot(api_key=None, enable_prompt_engineering=True)
        builder = PromptBuilder()
        
        # Teste de múltiplas consultas
        start_time = time.time()
        
        for i in range(10):
            message = f"Teste de performance {i}"
            context = builder.detect_context_type(message)
            response = bot.ask(message)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   ✅ 10 consultas em {duration:.2f} segundos")
        print(f"   ✅ Média: {duration/10:.3f} segundos por consulta")
        
        # Verificar estatísticas
        stats = bot.get_session_stats()
        print(f"   ✅ Total de consultas: {stats['total_queries']}")
        print(f"   ✅ Taxa de sucesso: {stats['success_rate']:.1f}%")
        
        return duration < 10  # Menos de 10 segundos para 10 consultas
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🚀 INICIANDO TESTES DO OLABOT v2")
    print("=" * 50)
    
    tests = [
        ("Funcionalidades Básicas", test_basic_functionality),
        ("Engenharia de Prompt", test_prompt_engineering),
        ("Detecção de Contexto", test_context_detection),
        ("Qualidade das Respostas", test_response_quality),
        ("Integração", test_integration),
        ("Performance", performance_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"   Resultado: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"   ❌ ERRO CRÍTICO: {e}")
    
    # Relatório final
    print(f"\n{'='*50}")
    print("📊 RELATÓRIO FINAL")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 RESUMO: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
        return 0
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
