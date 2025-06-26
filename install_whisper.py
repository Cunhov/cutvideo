#!/usr/bin/env python3
"""
Script de instalação do Whisper para Auto-Editor GUI
Instala Whisper e suas dependências para a funcionalidade de correção de fala por IA
"""

import subprocess
import sys
import os

def install_whisper():
    """Instala Whisper e suas dependências"""
    print("🎯 Instalando Whisper para correção de fala por IA...")
    print("=" * 60)
    
    # Verificar Python
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ é necessário")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    
    # Instalar tiktoken primeiro
    print("\n📦 Instalando tiktoken...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tiktoken"])
        print("✅ tiktoken instalado com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar tiktoken")
        return False
    
    # Instalar Whisper
    print("\n📦 Instalando Whisper...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "git+https://github.com/openai/whisper.git"
        ])
        print("✅ Whisper instalado com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar Whisper")
        return False
    
    # Verificar instalação
    print("\n🔍 Verificando instalação...")
    try:
        import whisper
        print("✅ Whisper importado com sucesso")
        
        # Testar carregamento de modelo pequeno
        print("📥 Baixando modelo 'tiny' para teste...")
        model = whisper.load_model("tiny")
        print("✅ Modelo carregado com sucesso")
        
    except ImportError as e:
        print(f"❌ Erro ao importar Whisper: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Whisper instalado com sucesso!")
    print("🎯 Funcionalidade de correção de fala por IA disponível!")
    print("\nPara usar:")
    print("1. Execute: python3 auto_editor_gui.py")
    print("2. Vá para a aba 'Correção de Fala (IA)'")
    print("3. Clique em 'Analisar Fala com Whisper'")
    
    return True

def main():
    """Função principal"""
    print("🎯 Auto-Editor GUI - Instalação do Whisper")
    print("=" * 60)
    
    # Verificar se já está instalado
    try:
        import whisper
        print("✅ Whisper já está instalado!")
        response = input("Deseja reinstalar? (s/n): ").lower().strip()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("👋 Instalação cancelada.")
            return
    except ImportError:
        pass
    
    # Instalar
    if install_whisper():
        print("\n🚀 Instalação concluída! Execute a aplicação agora.")
    else:
        print("\n❌ Falha na instalação. Verifique os erros acima.")

if __name__ == "__main__":
    main() 