#!/usr/bin/env python3
"""
Script para instalar psutil - Monitoramento de Recursos
=======================================================

Este script instala a biblioteca psutil necessária para monitoramento
de uso de memória e recursos do sistema.

Uso:
    python3 install_psutil.py
"""

import subprocess
import sys
import os

def install_psutil():
    """Instala a biblioteca psutil"""
    print("🔧 Instalando psutil para monitoramento de recursos...")
    
    try:
        # Tentar instalar via pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "psutil"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ psutil instalado com sucesso!")
            print("📊 Agora você pode monitorar o uso de memória em tempo real")
            return True
        else:
            print(f"❌ Erro ao instalar psutil: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante instalação: {str(e)}")
        return False

def verify_installation():
    """Verifica se psutil foi instalado corretamente"""
    try:
        import psutil
        print("✅ psutil está funcionando corretamente")
        print(f"📊 Versão instalada: {psutil.__version__}")
        return True
    except ImportError:
        print("❌ psutil não foi instalado corretamente")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 INSTALADOR PSUTIL - MONITORAMENTO DE RECURSOS")
    print("=" * 60)
    print()
    
    # Verificar se já está instalado
    try:
        import psutil
        print("✅ psutil já está instalado!")
        print(f"📊 Versão: {psutil.__version__}")
        return
    except ImportError:
        pass
    
    # Instalar psutil
    if install_psutil():
        # Verificar instalação
        if verify_installation():
            print()
            print("🎉 Instalação concluída com sucesso!")
            print("📋 Agora você pode:")
            print("   • Monitorar uso de memória em tempo real")
            print("   • Ver logs detalhados de consumo de recursos")
            print("   • Identificar gargalos de memória")
            print()
            print("🚀 Execute a aplicação principal:")
            print("   python3 auto_editor_gui.py")
        else:
            print("❌ Falha na verificação da instalação")
    else:
        print("❌ Falha na instalação do psutil")

if __name__ == "__main__":
    main() 