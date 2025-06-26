#!/usr/bin/env python3
"""
Script de Instalação - Google Generative AI (Gemini)
Auto-Editor GUI v3.0

Este script instala a biblioteca necessária para usar o Google Gemini
na funcionalidade de análise de fala por LLM.
"""

import subprocess
import sys
import os

def print_header():
    """Imprime cabeçalho do script"""
    print("=" * 60)
    print("🔧 INSTALAÇÃO - GOOGLE GENERATIVE AI (GEMINI)")
    print("Auto-Editor GUI v3.0")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica a versão do Python"""
    print("🐍 Verificando versão do Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def install_gemini():
    """Instala a biblioteca Google Generative AI"""
    print("\n📦 Instalando Google Generative AI...")
    
    try:
        # Instalar usando pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "google-generativeai"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Google Generative AI instalado com sucesso!")
            return True
        else:
            print("❌ Erro na instalação:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro durante instalação: {e}")
        return False

def test_gemini_installation():
    """Testa se a instalação foi bem-sucedida"""
    print("\n🧪 Testando instalação...")
    
    try:
        import google.generativeai as genai
        print("✅ Biblioteca importada com sucesso!")
        
        # Testar configuração básica
        genai.configure(api_key="test_key")
        print("✅ Configuração básica funcionando!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def show_usage_instructions():
    """Mostra instruções de uso"""
    print("\n📖 INSTRUÇÕES DE USO:")
    print("-" * 30)
    print("1. Obtenha uma API Key do Google AI Studio:")
    print("   https://makersuite.google.com/app/apikey")
    print()
    print("2. Configure a API Key na aplicação:")
    print("   - Aba 'Configurações'")
    print("   - Seção 'Gerenciamento de APIs'")
    print("   - Campo 'Google Gemini API Key'")
    print()
    print("3. Teste a conexão:")
    print("   - Clique em '🧪 Testar Gemini'")
    print()
    print("4. Use na análise de fala:")
    print("   - Aba 'Correção de Fala (IA)'")
    print("   - Seção 'Análise Inteligente por LLM'")
    print("   - Clique em '🤖 2. Analisar Erros com LLM'")
    print()

def main():
    """Função principal"""
    print_header()
    
    # Verificar Python
    if not check_python_version():
        print("\n❌ Instalação cancelada. Atualize o Python.")
        return
    
    # Instalar Gemini
    if not install_gemini():
        print("\n❌ Falha na instalação do Google Generative AI.")
        return
    
    # Testar instalação
    if not test_gemini_installation():
        print("\n❌ Falha no teste da instalação.")
        return
    
    print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    
    show_usage_instructions()
    
    print("🚀 Para iniciar a aplicação:")
    print("   python3 auto_editor_gui.py")
    print("=" * 60)

if __name__ == "__main__":
    main() 