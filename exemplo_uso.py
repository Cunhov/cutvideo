#!/usr/bin/env python3
"""
Exemplo de uso da Auto-Editor GUI com Correção de Fala por IA

Este script demonstra como usar a aplicação programaticamente
e como configurar a nova funcionalidade de correção de fala por IA.
"""

import tkinter as tk
from auto_editor_gui import SimpleAutoEditorGUI

def exemplo_basico():
    """Exemplo básico de uso da aplicação"""
    print("🎬 Iniciando Auto-Editor GUI com Correção de Fala por IA...")
    
    # Criar e executar a aplicação
    root = tk.Tk()
    app = SimpleAutoEditorGUI(root)
    root.mainloop()

def exemplo_configuracao_whisper():
    """Exemplo de como configurar o Whisper programaticamente"""
    print("🎯 Configurando Whisper para correção de fala...")
    
    root = tk.Tk()
    app = SimpleAutoEditorGUI(root)
    
    # Configurar Whisper (se disponível)
    if hasattr(app, 'whisper_model'):
        # Usar modelo mais preciso
        app.whisper_model.set("small")
        
        # Habilitar GPU se disponível
        app.use_gpu.set(True)
        
        # Configurar palavras de preenchimento personalizadas
        app.custom_fillers.set("tipo, né, então, sabe, tipo assim, basicamente, na verdade")
        
        print("✅ Whisper configurado:")
        print(f"   Modelo: {app.whisper_model.get()}")
        print(f"   GPU: {app.use_gpu.get()}")
        print(f"   Palavras personalizadas: {app.custom_fillers.get()}")
    
    root.mainloop()

def exemplo_fluxo_completo():
    """Exemplo de fluxo completo de edição com correção de fala"""
    print("🎬 Fluxo completo de edição com correção de fala por IA:")
    print("1. Selecione um arquivo de vídeo")
    print("2. Configure as opções básicas")
    print("3. Vá para a aba 'Correção de Fala (IA)'")
    print("4. Clique em 'Analisar Fala com Whisper'")
    print("5. Revise a transcrição e marque erros")
    print("6. Volte para 'Configurações' e clique em 'Iniciar Edição'")
    print("7. Acompanhe o progresso no console")
    
    root = tk.Tk()
    app = SimpleAutoEditorGUI(root)
    
    # Configurar para um fluxo típico
    app.cut_type.set("audio")  # Detecção por áudio
    app.output_type.set("mp4")  # Saída MP4
    
    # Configurar Whisper para análise rápida
    if hasattr(app, 'whisper_model'):
        app.whisper_model.set("base")  # Modelo equilibrado
        app.detect_fillers.set(True)   # Detectar palavras de preenchimento
        app.detect_repetitions.set(True)  # Detectar repetições
    
    root.mainloop()

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔧 Verificando dependências...")
    
    # Verificar auto-editor
    try:
        import subprocess
        result = subprocess.run(['auto-editor', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ auto-editor: OK")
        else:
            print("❌ auto-editor: Não encontrado")
    except:
        print("❌ auto-editor: Não encontrado")
    
    # Verificar ffmpeg
    try:
        import shutil
        if shutil.which("ffmpeg"):
            print("✅ ffmpeg: OK")
        else:
            print("❌ ffmpeg: Não encontrado")
    except:
        print("❌ ffmpeg: Não encontrado")
    
    # Verificar Whisper
    try:
        import whisper
        print("✅ whisper: OK")
    except ImportError:
        print("❌ whisper: Não encontrado")
    
    # Verificar tiktoken
    try:
        import tiktoken
        print("✅ tiktoken: OK")
    except ImportError:
        print("❌ tiktoken: Não encontrado")

def main():
    """Função principal com menu de exemplos"""
    print("🎬 Auto-Editor GUI - Exemplos de Uso")
    print("=" * 50)
    print("1. Exemplo básico")
    print("2. Configuração do Whisper")
    print("3. Fluxo completo com correção de fala")
    print("4. Verificar dependências")
    print("5. Sair")
    
    while True:
        try:
            escolha = input("\nEscolha uma opção (1-5): ").strip()
            
            if escolha == "1":
                exemplo_basico()
            elif escolha == "2":
                exemplo_configuracao_whisper()
            elif escolha == "3":
                exemplo_fluxo_completo()
            elif escolha == "4":
                verificar_dependencias()
            elif escolha == "5":
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida. Escolha 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main() 