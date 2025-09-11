#!/usr/bin/env python3
"""
Testes para o Sistema de Sugestões Contextuais do OLABOT
========================================================

Este script testa todas as funcionalidades do sistema de sugestões.
Execute com: python test_suggestions.py
"""

import sys
import os
import json
import requests
import time
from typing import Dict, List, Any

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from olasis.prompt_engineering import ChatSuggestions


class SuggestionsTestSuite:
    """Suite de testes para o sistema de sugestões."""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Registra o resultado de um teste."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def test_suggestions_class(self):
        """Testa a classe ChatSuggestions diretamente."""
        print("\n🔧 Testando classe ChatSuggestions...")
        
        # Teste 1: Sugestões contextuais básicas
        try:
            suggestions = ChatSuggestions.get_contextual_suggestions("general", 4)
            self.log_test(
                "Sugestões contextuais gerais",
                len(suggestions) == 4 and all(isinstance(s, str) for s in suggestions),
                f"Retornou {len(suggestions)} sugestões"
            )
        except Exception as e:
            self.log_test("Sugestões contextuais gerais", False, str(e))
        
        # Teste 2: Sugestões por área
        try:
            suggestions = ChatSuggestions.get_suggestions_by_field("tecnologia", 3)
            self.log_test(
                "Sugestões por área (tecnologia)",
                len(suggestions) == 3 and all(isinstance(s, str) for s in suggestions),
                f"Retornou {len(suggestions)} sugestões"
            )
        except Exception as e:
            self.log_test("Sugestões por área (tecnologia)", False, str(e))
        
        # Teste 3: Sugestões adaptativas
        try:
            history = ["O que é machine learning?", "Como funcionam redes neurais?"]
            suggestions = ChatSuggestions.get_adaptive_suggestions(history, 4)
            self.log_test(
                "Sugestões adaptativas",
                len(suggestions) == 4 and all(isinstance(s, str) for s in suggestions),
                f"Retornou {len(suggestions)} sugestões baseadas no histórico"
            )
        except Exception as e:
            self.log_test("Sugestões adaptativas", False, str(e))
    
    def test_api_endpoints(self):
        """Testa os endpoints da API."""
        print("\n🌐 Testando endpoints da API...")
        
        # Teste 1: Endpoint básico
        try:
            response = requests.get(f"{self.base_url}/api/chat/suggestions", timeout=5)
            data = response.json()
            
            self.log_test(
                "Endpoint básico (/api/chat/suggestions)",
                response.status_code == 200 and "suggestions" in data,
                f"Status: {response.status_code}, Sugestões: {len(data.get('suggestions', []))}"
            )
        except Exception as e:
            self.log_test("Endpoint básico", False, str(e))
        
        # Teste 2: Endpoint com parâmetros de contexto
        try:
            response = requests.get(
                f"{self.base_url}/api/chat/suggestions?context=advanced&count=3",
                timeout=5
            )
            data = response.json()
            
            self.log_test(
                "Endpoint com contexto avançado",
                response.status_code == 200 and len(data.get("suggestions", [])) == 3,
                f"Contexto: {data.get('context')}, Count: {len(data.get('suggestions', []))}"
            )
        except Exception as e:
            self.log_test("Endpoint com contexto", False, str(e))
        
        # Teste 3: Endpoint com área específica
        try:
            response = requests.get(
                f"{self.base_url}/api/chat/suggestions?field=medicina&count=2",
                timeout=5
            )
            data = response.json()
            
            self.log_test(
                "Endpoint com campo específico",
                response.status_code == 200 and len(data.get("suggestions", [])) == 2,
                f"Campo: {data.get('field')}, Count: {len(data.get('suggestions', []))}"
            )
        except Exception as e:
            self.log_test("Endpoint com campo", False, str(e))
        
        # Teste 4: Combinação de parâmetros
        try:
            response = requests.get(
                f"{self.base_url}/api/chat/suggestions?context=beginner&field=tecnologia&count=5",
                timeout=5
            )
            data = response.json()
            
            self.log_test(
                "Endpoint com múltiplos parâmetros",
                response.status_code == 200 and data.get("suggestions"),
                f"Parâmetros combinados funcionando"
            )
        except Exception as e:
            self.log_test("Endpoint com múltiplos parâmetros", False, str(e))
    
    def test_performance(self):
        """Testa a performance das sugestões."""
        print("\n⚡ Testando performance...")
        
        # Teste de velocidade da API
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/chat/suggestions", timeout=5)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # em ms
            
            self.log_test(
                "Tempo de resposta da API",
                response_time < 1000,  # Menos de 1 segundo
                f"Tempo: {response_time:.2f}ms"
            )
        except Exception as e:
            self.log_test("Tempo de resposta da API", False, str(e))
        
        # Teste de velocidade da classe
        try:
            start_time = time.time()
            for _ in range(100):
                ChatSuggestions.get_contextual_suggestions("general", 4)
            end_time = time.time()
            
            avg_time = ((end_time - start_time) / 100) * 1000  # em ms
            
            self.log_test(
                "Performance da classe ChatSuggestions",
                avg_time < 10,  # Menos de 10ms por chamada
                f"Tempo médio: {avg_time:.2f}ms por chamada"
            )
        except Exception as e:
            self.log_test("Performance da classe", False, str(e))
    
    def test_data_quality(self):
        """Testa a qualidade dos dados das sugestões."""
        print("\n📊 Testando qualidade dos dados...")
        
        # Teste 1: Verificar se todas as categorias têm sugestões
        try:
            all_contexts = ["general", "beginner", "intermediate", "advanced", 
                          "search_focused", "methodology_focused"]
            
            missing_contexts = []
            for context in all_contexts:
                suggestions = ChatSuggestions.get_contextual_suggestions(context, 1)
                if not suggestions:
                    missing_contexts.append(context)
            
            self.log_test(
                "Cobertura de contextos",
                len(missing_contexts) == 0,
                f"Contextos sem sugestões: {missing_contexts}" if missing_contexts else "Todos os contextos têm sugestões"
            )
        except Exception as e:
            self.log_test("Cobertura de contextos", False, str(e))
        
        # Teste 2: Verificar se todas as áreas têm sugestões
        try:
            all_fields = ["medicina", "tecnologia", "meio_ambiente", "educacao"]
            
            missing_fields = []
            for field in all_fields:
                suggestions = ChatSuggestions.get_suggestions_by_field(field, 1)
                if not suggestions:
                    missing_fields.append(field)
            
            self.log_test(
                "Cobertura de áreas",
                len(missing_fields) == 0,
                f"Áreas sem sugestões: {missing_fields}" if missing_fields else "Todas as áreas têm sugestões"
            )
        except Exception as e:
            self.log_test("Cobertura de áreas", False, str(e))
        
        # Teste 3: Verificar unicidade das sugestões
        try:
            suggestions = ChatSuggestions.get_contextual_suggestions("general", 10)
            unique_suggestions = set(suggestions)
            
            self.log_test(
                "Unicidade das sugestões",
                len(suggestions) == len(unique_suggestions),
                f"Sugestões: {len(suggestions)}, Únicas: {len(unique_suggestions)}"
            )
        except Exception as e:
            self.log_test("Unicidade das sugestões", False, str(e))
    
    def test_error_handling(self):
        """Testa o tratamento de erros."""
        print("\n🛡️ Testando tratamento de erros...")
        
        # Teste 1: Contexto inválido
        try:
            suggestions = ChatSuggestions.get_contextual_suggestions("contexto_inexistente", 4)
            self.log_test(
                "Contexto inválido",
                len(suggestions) > 0,  # Deve retornar sugestões padrão
                "Retorna sugestões padrão para contexto inválido"
            )
        except Exception as e:
            self.log_test("Contexto inválido", False, str(e))
        
        # Teste 2: Área inválida
        try:
            suggestions = ChatSuggestions.get_suggestions_by_field("area_inexistente", 4)
            self.log_test(
                "Área inválida",
                len(suggestions) > 0,  # Deve retornar sugestões padrão
                "Retorna sugestões padrão para área inválida"
            )
        except Exception as e:
            self.log_test("Área inválida", False, str(e))
        
        # Teste 3: Limite zero ou negativo
        try:
            suggestions = ChatSuggestions.get_contextual_suggestions("general", 0)
            self.log_test(
                "Limite zero",
                len(suggestions) == 0,
                "Retorna lista vazia para limite 0"
            )
        except Exception as e:
            self.log_test("Limite zero", False, str(e))
    
    def run_all_tests(self):
        """Executa todos os testes."""
        print("🚀 Iniciando suite de testes do Sistema de Sugestões\n")
        
        self.test_suggestions_class()
        self.test_api_endpoints()
        self.test_performance()
        self.test_data_quality()
        self.test_error_handling()
        
        # Resumo dos resultados
        print("\n" + "="*60)
        print("📋 RESUMO DOS TESTES")
        print("="*60)
        
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        
        print(f"Total: {total} testes")
        print(f"Passou: {passed} testes")
        print(f"Falhou: {total - passed} testes")
        print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
        else:
            print(f"\n⚠️  {total - passed} TESTE(S) FALHARAM")
            print("\nTestes que falharam:")
            for result in self.results:
                if not result["passed"]:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        return passed == total


def main():
    """Função principal para executar os testes."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Testes do Sistema de Sugestões OLABOT")
    parser.add_argument("--url", default="http://localhost:5001", 
                       help="URL base da aplicação (padrão: http://localhost:5001)")
    
    args = parser.parse_args()
    
    # Verificar se a aplicação está rodando
    try:
        response = requests.get(args.url, timeout=5)
        print(f"✅ Aplicação rodando em {args.url}")
    except requests.exceptions.RequestException:
        print(f"❌ Erro: Aplicação não está rodando em {args.url}")
        print("   Execute: PORT=5001 python app.py")
        return False
    
    # Executar testes
    test_suite = SuggestionsTestSuite(args.url)
    success = test_suite.run_all_tests()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
