#!/usr/bin/env python3
"""
Exemplo de Uso Avançado - Auto-Editor GUI v3.0
Demonstração das novas funcionalidades de gerenciamento de APIs e análise por LLM

Este script mostra como usar as funcionalidades avançadas da aplicação:
- Gerenciamento de APIs (OpenAI e Google Gemini)
- Análise de fala por LLM
- Configuração persistente
- Seleção de modelos
"""

import json
import os
import sys

def print_header():
    """Imprime cabeçalho do exemplo"""
    print("=" * 70)
    print("🚀 EXEMPLO DE USO AVANÇADO - AUTO-EDITOR GUI v3.0")
    print("Gerenciamento de APIs e Análise por LLM")
    print("=" * 70)
    print()

def demonstrate_api_management():
    """Demonstra o sistema de gerenciamento de APIs"""
    print("🔑 GERENCIAMENTO DE APIS")
    print("-" * 40)
    
    # Exemplo de configuração
    config_example = {
        "openai": "sk-...",  # Sua API Key da OpenAI
        "gemini": "AIza...",  # Sua API Key do Google Gemini
        "last_provider": "openai",
        "last_model": "gpt-4o"
    }
    
    print("1. Configuração de API Keys:")
    print("   - Aba 'Configurações'")
    print("   - Seção 'Gerenciamento de APIs'")
    print("   - Campos para OpenAI e Google Gemini")
    print()
    
    print("2. Salvamento de configurações:")
    print("   - Clique em '💾 Salvar Chaves'")
    print("   - Configurações salvas em api_config.json")
    print("   - Carregamento automático na próxima execução")
    print()
    
    print("3. Teste de conectividade:")
    print("   - Clique em '🧪 Testar OpenAI'")
    print("   - Clique em '🧪 Testar Gemini'")
    print("   - Verificação automática de modelos disponíveis")
    print()

def demonstrate_llm_selection():
    """Demonstra a seleção de LLM"""
    print("🧠 SELEÇÃO DE LLM")
    print("-" * 40)
    
    print("1. Provedores disponíveis:")
    print("   - OpenAI (GPT-4o, GPT-4, GPT-3.5-turbo)")
    print("   - Google Gemini (gemini-1.5-pro, gemini-1.0-pro)")
    print()
    
    print("2. Seleção de modelo:")
    print("   - Radio buttons para escolher provedor")
    print("   - Combobox com modelos disponíveis")
    print("   - Seleção automática de modelo padrão")
    print()
    
    print("3. Configuração persistente:")
    print("   - Última seleção salva automaticamente")
    print("   - Restauração na próxima execução")
    print("   - Status de conexão em tempo real")
    print()

def demonstrate_speech_analysis():
    """Demonstra a análise de fala por LLM"""
    print("🗣️ ANÁLISE DE FALA POR LLM")
    print("-" * 40)
    
    print("1. Fluxo de trabalho:")
    print("   - Passo 1: Transcrição com Whisper")
    print("   - Passo 2: Análise de erros por LLM")
    print("   - Passo 3: Revisão e aplicação de correções")
    print()
    
    print("2. Tipos de erros detectados:")
    print("   - Palavras de preenchimento (um, ah, tipo, né)")
    print("   - Repetições desnecessárias")
    print("   - Gaguejos e hesitações")
    print("   - Pausas longas")
    print("   - Erros gramaticais")
    print("   - Conteúdo irrelevante")
    print()
    
    print("3. Interface de sugestões:")
    print("   - Lista categorizada de sugestões")
    print("   - Botões para aplicar/rejeitar")
    print("   - Marcação visual na transcrição")
    print("   - Estatísticas em tempo real")
    print()

def demonstrate_advanced_features():
    """Demonstra funcionalidades avançadas"""
    print("⚡ FUNCIONALIDADES AVANÇADAS")
    print("-" * 40)
    
    print("1. Otimizações de memória:")
    print("   - Processamento em lotes")
    print("   - Limpeza automática de recursos")
    print("   - Monitoramento em tempo real")
    print("   - Botão de limpeza manual")
    print()
    
    print("2. Configuração persistente:")
    print("   - API Keys salvas automaticamente")
    print("   - Preferências de LLM mantidas")
    print("   - Últimas configurações restauradas")
    print()
    
    print("3. Tratamento de erros:")
    print("   - Validação de API Keys")
    print("   - Teste de conectividade")
    print("   - Fallback para modo local")
    print("   - Logs detalhados de erros")
    print()

def show_workflow_example():
    """Mostra exemplo de fluxo de trabalho completo"""
    print("📋 EXEMPLO DE FLUXO DE TRABALHO")
    print("-" * 40)
    
    print("1. Configuração inicial:")
    print("   python3 auto_editor_gui.py")
    print("   → Aba 'Configurações'")
    print("   → Inserir API Keys")
    print("   → Testar conexões")
    print("   → Salvar configurações")
    print()
    
    print("2. Correção de fala:")
    print("   → Aba 'Correção de Fala (IA)'")
    print("   → Selecionar arquivo de vídeo")
    print("   → Clique '🎤 1. Analisar Fala com Whisper'")
    print("   → Aguardar transcrição")
    print("   → Clique '🤖 2. Analisar Erros com LLM'")
    print("   → Revisar sugestões")
    print("   → Aplicar correções desejadas")
    print()
    
    print("3. Reorganização semântica:")
    print("   → Aba 'Reorganização por IA'")
    print("   → Descrever objetivo do vídeo")
    print("   → Clique '🧠 Analisar Estrutura Narrativa'")
    print("   → Revisar sugestões de reordenação")
    print("   → Aprovar ou descartar mudanças")
    print("   → Clique '🎬 Renderizar Vídeo Final'")
    print()
    
    print("4. Monitoramento:")
    print("   → Aba 'Console' para logs detalhados")
    print("   → Monitoramento de memória")
    print("   → Limpeza manual se necessário")
    print()

def show_api_examples():
    """Mostra exemplos de uso das APIs"""
    print("🔌 EXEMPLOS DE USO DAS APIS")
    print("-" * 40)
    
    print("1. OpenAI GPT-4o:")
    print("   - Análise mais precisa e contextual")
    print("   - Melhor compreensão de nuances")
    print("   - Respostas mais detalhadas")
    print("   - Ideal para análise complexa")
    print()
    
    print("2. Google Gemini:")
    print("   - Alternativa econômica")
    print("   - Boa performance para análise básica")
    print("   - Menor latência")
    print("   - Ideal para processamento em lote")
    print()
    
    print("3. Seleção de modelo:")
    print("   - GPT-4o: Análise avançada")
    print("   - GPT-4: Análise equilibrada")
    print("   - GPT-3.5-turbo: Análise rápida")
    print("   - Gemini-1.5-pro: Alternativa robusta")
    print("   - Gemini-1.0-pro: Alternativa básica")
    print()

def main():
    """Função principal"""
    print_header()
    
    demonstrate_api_management()
    demonstrate_llm_selection()
    demonstrate_speech_analysis()
    demonstrate_advanced_features()
    show_workflow_example()
    show_api_examples()
    
    print("🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print("Agora você pode usar todas as funcionalidades avançadas da aplicação.")
    print("Execute: python3 auto_editor_gui.py")
    print("=" * 70)

if __name__ == "__main__":
    main() 