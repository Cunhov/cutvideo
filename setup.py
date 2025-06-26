#!/usr/bin/env python3
"""
Script de Setup Completo - Auto-Editor GUI v3.0
Com suporte a OpenAI Whisper, GPT-4o e Google Gemini

Este script instala todas as dependências necessárias para a aplicação
Auto-Editor GUI com funcionalidades avançadas de IA.
"""

import subprocess
import sys
import os
import shutil

def print_header():
    """Imprime cabeçalho do script"""
    print("=" * 70)
    print("🚀 SETUP COMPLETO - AUTO-EDITOR GUI v3.0")
    print("Com OpenAI Whisper, GPT-4o e Google Gemini")
    print("=" * 70)
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

def check_system_dependencies():
    """Verifica dependências do sistema"""
    print("\n🔧 Verificando dependências do sistema...")
    
    missing = []
    
    # Verificar ffmpeg
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
        print("❌ ffmpeg não encontrado")
    else:
        print("✅ ffmpeg encontrado")
    
    # Verificar auto-editor
    if not shutil.which("auto-editor"):
        missing.append("auto-editor")
        print("❌ auto-editor não encontrado")
    else:
        print("✅ auto-editor encontrado")
    
    if missing:
        print(f"\n⚠️ Dependências ausentes: {', '.join(missing)}")
        print("Execute os seguintes comandos:")
        print("   pip install auto-editor")
        print("   brew install ffmpeg  # macOS")
        print("   sudo apt install ffmpeg  # Ubuntu/Debian")
        return False
    
    return True

def install_python_dependencies():
    """Instala dependências Python"""
    print("\n📦 Instalando dependências Python...")
    
    dependencies = [
        "openai",
        "psutil",
        "google-generativeai"
    ]
    
    for dep in dependencies:
        print(f"   Instalando {dep}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ {dep} instalado")
            else:
                print(f"   ❌ Erro ao instalar {dep}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro ao instalar {dep}: {e}")
            return False
    
    return True

def install_whisper():
    """Instala Whisper"""
    print("\n🗣️ Instalando OpenAI Whisper...")
    
    try:
        # Instalar Whisper
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "git+https://github.com/openai/whisper.git"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Whisper instalado com sucesso!")
        else:
            print("❌ Erro na instalação do Whisper:")
            print(result.stderr)
            return False
        
        # Instalar tiktoken
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "tiktoken"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ tiktoken instalado com sucesso!")
        else:
            print("❌ Erro na instalação do tiktoken:")
            print(result.stderr)
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante instalação: {e}")
        return False

def test_installations():
    """Testa todas as instalações"""
    print("\n🧪 Testando instalações...")
    
    tests = [
        ("openai", "import openai"),
        ("whisper", "import whisper"),
        ("psutil", "import psutil"),
        ("google.generativeai", "import google.generativeai as genai")
    ]
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {name} - OK")
        except ImportError as e:
            print(f"❌ {name} - Erro: {e}")
            return False
        except Exception as e:
            print(f"❌ {name} - Erro: {e}")
            return False
    
    return True

def create_config_file():
    """Cria arquivo de configuração inicial"""
    print("\n⚙️ Criando arquivo de configuração...")
    
    config = {
        "openai": "",
        "gemini": "",
        "last_provider": "openai",
        "last_model": "gpt-4o"
    }
    
    try:
        import json
        with open("api_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✅ Arquivo de configuração criado: api_config.json")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar configuração: {e}")
        return False

def show_next_steps():
    """Mostra próximos passos"""
    print("\n📖 PRÓXIMOS PASSOS:")
    print("-" * 30)
    print("1. Configure suas API Keys:")
    print("   - OpenAI: https://platform.openai.com/api-keys")
    print("   - Google Gemini: https://makersuite.google.com/app/apikey")
    print()
    print("2. Execute a aplicação:")
    print("   python3 auto_editor_gui.py")
    print()
    print("3. Configure as APIs na aba 'Configurações'")
    print()
    print("4. Teste as conexões:")
    print("   - Clique em '🧪 Testar OpenAI'")
    print("   - Clique em '🧪 Testar Gemini'")
    print()
    print("5. Comece a usar:")
    print("   - Selecione um vídeo")
    print("   - Execute transcrição com Whisper")
    print("   - Use análise por LLM")
    print("   - Aproveite a reorganização semântica!")
    print()

def show_features():
    """Mostra funcionalidades disponíveis"""
    print("\n🎯 FUNCIONALIDADES DISPONÍVEIS:")
    print("-" * 40)
    print("🗣️ Correção de Fala por IA:")
    print("   • Transcrição com Whisper (API/Local)")
    print("   • Análise de erros por LLM (GPT-4o/Gemini)")
    print("   • Detecção automática de problemas")
    print("   • Interface intuitiva para correções")
    print()
    print("🧠 Reorganização Semântica:")
    print("   • Análise de estrutura narrativa")
    print("   • Sugestões de reordenação de clipes")
    print("   • Identificação de conteúdo desnecessário")
    print("   • Renderização avançada")
    print()
    print("⚡ Otimizações de Performance:")
    print("   • Processamento em lotes")
    print("   • Monitoramento de memória")
    print("   • Limpeza automática de recursos")
    print("   • Interface responsiva")
    print()

def main():
    """Função principal"""
    print_header()
    
    # Verificar Python
    if not check_python_version():
        print("\n❌ Setup cancelado. Atualize o Python.")
        return
    
    # Verificar dependências do sistema
    if not check_system_dependencies():
        print("\n⚠️ Algumas dependências do sistema estão ausentes.")
        print("Continue com a instalação das dependências Python...")
    
    # Instalar dependências Python
    if not install_python_dependencies():
        print("\n❌ Falha na instalação das dependências Python.")
        return
    
    # Instalar Whisper
    if not install_whisper():
        print("\n❌ Falha na instalação do Whisper.")
        return
    
    # Testar instalações
    if not test_installations():
        print("\n❌ Falha nos testes de instalação.")
        return
    
    # Criar arquivo de configuração
    if not create_config_file():
        print("\n⚠️ Erro ao criar arquivo de configuração.")
    
    print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    
    show_features()
    show_next_steps()
    
    print("🚀 Para iniciar a aplicação:")
    print("   python3 auto_editor_gui.py")
    print("=" * 70)

if __name__ == "__main__":
    main() 