#!/usr/bin/env python3
"""
Auto-Editor GUI - Interface gráfica simplificada para auto-editor
Versão simplificada e intuitiva com Correção de Fala por IA
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import threading
import queue
import os
import shutil
import datetime
import tempfile
import json
from typing import Optional, List, Dict, Tuple
import psutil

# Importações para Whisper (opcional)
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

# Importações para OpenAI (opcional)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

# Importações para Google Generative AI (opcional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

class AutoEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Editor GUI v3.0 - Edição Inteligente com IA")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        self.root.configure(bg="#e5e3de")
        
        # Configurações de API
        self.api_keys = self.load_api_keys()
        self.selected_llm_provider = tk.StringVar(value="openai")
        self.selected_llm_model = tk.StringVar(value="gpt-4o")
        self.available_models = {}
        
        # Configurações de Whisper
        self.whisper_mode = tk.StringVar(value="api")
        self.whisper_model = tk.StringVar(value="base")
        self.use_gpu = tk.BooleanVar()
        
        # Configurações de análise de fala
        self.detect_fillers = tk.BooleanVar(value=True)
        self.detect_repetitions = tk.BooleanVar(value=True)
        self.custom_fillers = tk.StringVar(value="tipo, né, sabe, então")
        
        # Variáveis de estado
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.cut_type = tk.StringVar(value="audio")
        self.is_running = False
        self.process = None
        self.output_queue = queue.Queue()
        
        # Variáveis para Whisper
        self.whisper_result = None
        self.error_segments = []
        self.marked_segments = []
        
        # Variáveis para Reorganização Semântica
        self.speech_clips = []  # Clipes de fala extraídos
        self.semantic_suggestions = None  # Sugestões do LLM
        self.final_clip_order = []  # Ordem final aprovada pelo usuário
        self.semantic_analysis_completed = False
        
        # Variáveis para análise de fala por LLM
        self.llm_speech_analysis = None
        self.llm_suggestions = []
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar widgets
        self.create_widgets()
        
        # Verificar dependências
        self.check_dependencies()
        
        # Iniciar monitoramento de saída
        self.monitor_output()
        
        # Configurar fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configura estilos para widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores e estilos
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Section.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 10))
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Notebook com rolagem
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Criar abas com rolagem
        self.tabs = {}
        for tab_name in ["Configurações", "Correção de Fala (IA)", "Reorganização por IA", "Console"]:
            frame = self.create_scrollable_tab(tab_name)
            self.tabs[tab_name] = frame

        # Crie todas as abas e widgets antes de checar dependências
        self.create_config_tab(self.tabs["Configurações"])
        self.create_speech_correction_tab(self.tabs["Correção de Fala (IA)"])
        self.create_semantic_reorganization_tab(self.tabs["Reorganização por IA"])
        self.create_console_tab(self.tabs["Console"])
    
    def create_scrollable_tab(self, tab_name):
        outer_frame = ttk.Frame(self.notebook)
        self.notebook.add(outer_frame, text=tab_name)
        canvas = tk.Canvas(outer_frame, borderwidth=0, background="#e5e3de")
        vscroll = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner_frame.bind("<Configure>", _on_frame_configure)
        return inner_frame
    
    def create_config_tab(self, parent):
        """Cria a aba de configurações com modos dinâmicos"""
        config_frame = ttk.Frame(parent, padding="20")
        config_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Seletor de Modo Principal
        mode_label = ttk.Label(config_frame, text="Escolha o Modo de Edição", style='Section.TLabel')
        mode_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.edit_mode = tk.StringVar(value="auto_magic")
        mode_frame = ttk.Frame(config_frame)
        mode_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 20))
        ttk.Radiobutton(mode_frame, text="✨ Edição Automágica (com IA Completa)", variable=self.edit_mode, value="auto_magic", command=self.update_mode_visibility).pack(side=tk.LEFT, padx=(0, 30))
        ttk.Radiobutton(mode_frame, text="✂️ Edição Simples (Apenas Cortes de Silêncio)", variable=self.edit_mode, value="simple", command=self.update_mode_visibility).pack(side=tk.LEFT)

        # 2. Controles do modo Automágico
        self.magic_controls = ttk.LabelFrame(config_frame, text="✨ Edição Automágica (com IA Completa)", padding="15")
        self.magic_controls.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.magic_controls.columnconfigure(1, weight=1)
        # Slider Estilo de Corte
        ttk.Label(self.magic_controls, text="Estilo de Corte (Silêncio e Pausas):", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.magic_cut_style = tk.IntVar(value=3)
        cut_style_slider = ttk.Scale(self.magic_controls, from_=1, to=5, variable=self.magic_cut_style, orient=tk.HORIZONTAL)
        cut_style_slider.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        ttk.Label(self.magic_controls, text="Mais Seco").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(self.magic_controls, text="Mais Suave").grid(row=1, column=1, sticky=tk.E)
        # Slider Nível de Concisão
        ttk.Label(self.magic_controls, text="Nível de Concisão da IA (Conteúdo):", style='Section.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.magic_conciseness = tk.IntVar(value=3)
        conciseness_slider = ttk.Scale(self.magic_controls, from_=1, to=5, variable=self.magic_conciseness, orient=tk.HORIZONTAL)
        conciseness_slider.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        ttk.Label(self.magic_controls, text="Mais Enxuto").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(self.magic_controls, text="Mais Encorpado").grid(row=3, column=1, sticky=tk.E)
        # Checkbox J-Cut
        self.magic_jcut_enabled = tk.BooleanVar(value=False)
        jcut_check = ttk.Checkbutton(self.magic_controls, text="Habilitar J-Cuts nas transições", variable=self.magic_jcut_enabled, command=self.update_jcut_sliders)
        jcut_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        # Slider Duração J-Cut
        ttk.Label(self.magic_controls, text="Duração do J-Cut (segundos):").grid(row=5, column=0, sticky=tk.W)
        self.magic_jcut_duration = tk.DoubleVar(value=0.5)
        self.magic_jcut_slider = ttk.Scale(self.magic_controls, from_=0.2, to=1.5, variable=self.magic_jcut_duration, orient=tk.HORIZONTAL, state='disabled')
        self.magic_jcut_slider.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        # Botão de ação
        self.magic_start_button = ttk.Button(self.magic_controls, text="✨ Iniciar Edição Automágica ✨", command=self.start_auto_magic_edit, style='Accent.TButton')
        self.magic_start_button.grid(row=6, column=0, columnspan=2, pady=(20, 0))

        # 3. Controles do modo Simples
        self.simple_controls = ttk.LabelFrame(config_frame, text="✂️ Edição Simples (Apenas Cortes de Silêncio)", padding="15")
        self.simple_controls.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.simple_controls.columnconfigure(1, weight=1)
        # Slider Estilo de Corte
        ttk.Label(self.simple_controls, text="Estilo de Corte (Silêncio e Pausas):", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.simple_cut_style = tk.IntVar(value=3)
        simple_cut_slider = ttk.Scale(self.simple_controls, from_=1, to=5, variable=self.simple_cut_style, orient=tk.HORIZONTAL)
        simple_cut_slider.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        ttk.Label(self.simple_controls, text="Mais Seco").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(self.simple_controls, text="Mais Suave").grid(row=1, column=1, sticky=tk.E)
        # Checkbox J-Cut
        self.simple_jcut_enabled = tk.BooleanVar(value=False)
        simple_jcut_check = ttk.Checkbutton(self.simple_controls, text="Habilitar J-Cuts nas transições", variable=self.simple_jcut_enabled, command=self.update_jcut_sliders)
        simple_jcut_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        # Slider Duração J-Cut
        ttk.Label(self.simple_controls, text="Duração do J-Cut (segundos):").grid(row=3, column=0, sticky=tk.W)
        self.simple_jcut_duration = tk.DoubleVar(value=0.5)
        self.simple_jcut_slider = ttk.Scale(self.simple_controls, from_=0.2, to=1.5, variable=self.simple_jcut_duration, orient=tk.HORIZONTAL, state='disabled')
        self.simple_jcut_slider.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        # Botão de ação
        self.simple_start_button = ttk.Button(self.simple_controls, text="🎬 Iniciar Edição Simples", command=self.start_simple_edit, style='Accent.TButton')
        self.simple_start_button.grid(row=4, column=0, columnspan=2, pady=(20, 0))

        # 4. Componentes Compartilhados
        file_frame = ttk.LabelFrame(config_frame, text="📁 Arquivos", padding="15")
        file_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        file_frame.columnconfigure(1, weight=1)
        ttk.Label(file_frame, text="Arquivo de Vídeo:", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        input_frame = ttk.Frame(file_frame)
        input_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        ttk.Entry(input_frame, textvariable=self.input_file, font=('Arial', 10)).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(input_frame, text="Escolher Vídeo", command=self.choose_input_file).grid(row=0, column=1)
        ttk.Label(file_frame, text="Arquivo de Saída:", style='Section.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        output_frame = ttk.Frame(file_frame)
        output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        output_frame.columnconfigure(0, weight=1)
        ttk.Entry(output_frame, textvariable=self.output_file, font=('Arial', 10)).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Escolher Local", command=self.choose_output_file).grid(row=0, column=1)

        # 5. Indicador de Status Detalhado
        self.config_status_label = ttk.Label(config_frame, text="Pronto para editar", style='Info.TLabel', foreground='blue')
        self.config_status_label.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Widget oculto para comando (evita erro de atributo)
        if not hasattr(self, 'command_text'):
            self.command_text = tk.Text(config_frame, height=1, width=1)
            self.command_text.grid_forget()

        # Inicializar visibilidade
        self.update_mode_visibility()

        # Botão de ação principal para Automágica
        self.magic_action_btn = ttk.Button(self.magic_controls, text="Executar Edição Automágica", command=self.start_auto_magic_edit, style='Action.TButton')
        self.magic_action_btn.grid(row=10, column=0, columnspan=2, pady=(20, 0), sticky=(tk.W, tk.E))

        # Botão de ação principal para Simples
        self.simple_action_btn = ttk.Button(self.simple_controls, text="Executar Edição Simples", command=self.start_simple_edit, style='Action.TButton')
        self.simple_action_btn.grid(row=10, column=0, columnspan=2, pady=(20, 0), sticky=(tk.W, tk.E))

    def update_mode_visibility(self):
        """Atualiza a visibilidade dos controles conforme o modo selecionado"""
        if self.edit_mode.get() == "auto_magic":
            self.magic_controls.grid()
            self.simple_controls.grid_remove()
        else:
            self.magic_controls.grid_remove()
            self.simple_controls.grid()
        self.update_jcut_sliders()

    def update_jcut_sliders(self):
        """Habilita/desabilita sliders de J-Cut conforme checkbox"""
        if self.edit_mode.get() == "auto_magic":
            state = 'normal' if self.magic_jcut_enabled.get() else 'disabled'
            self.magic_jcut_slider.config(state=state)
        else:
            state = 'normal' if self.simple_jcut_enabled.get() else 'disabled'
            self.simple_jcut_slider.config(state=state)

    def create_speech_correction_tab(self, parent):
        """Cria a aba de correção de fala por IA"""
        speech_frame = ttk.Frame(parent, padding="20")
        speech_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(speech_frame, text="Correção de Fala por IA - Whisper + LLM", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Verificar se Whisper está disponível
        if not WHISPER_AVAILABLE:
            warning_frame = ttk.Frame(speech_frame)
            warning_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
            ttk.Label(warning_frame, text="⚠️ Biblioteca Whisper não instalada", style='Section.TLabel', foreground='red').pack()
            ttk.Label(warning_frame, text="Execute: python3 setup.py para instalar whisper", style='Info.TLabel').pack()
            return
        
        # Seção 1: Análise de Fala
        analysis_frame = ttk.LabelFrame(speech_frame, text="🎤 Análise de Fala", padding="15")
        analysis_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        analysis_frame.columnconfigure(0, weight=1)
        
        self.analyze_button = ttk.Button(analysis_frame, text="🎤 1. Analisar Fala com Whisper", command=self.start_speech_analysis, style='Accent.TButton')
        self.analyze_button.grid(row=0, column=0, pady=(0, 10))
        
        self.analysis_status = ttk.Label(analysis_frame, text="Aguardando análise...", style='Info.TLabel', foreground='gray')
        self.analysis_status.grid(row=1, column=0, pady=(0, 10))
        
        # Seção 2: Análise por LLM
        llm_analysis_frame = ttk.LabelFrame(speech_frame, text="🧠 Análise Inteligente por LLM", padding="15")
        llm_analysis_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        llm_analysis_frame.columnconfigure(0, weight=1)
        
        ttk.Label(llm_analysis_frame, text="Após a transcrição, use o LLM para detectar erros automaticamente:", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.llm_analyze_button = ttk.Button(llm_analysis_frame, text="🤖 2. Analisar Erros com LLM", command=self.start_llm_analysis, style='Accent.TButton', state='disabled')
        self.llm_analyze_button.grid(row=1, column=0, pady=(0, 10))
        
        self.llm_analysis_status = ttk.Label(llm_analysis_frame, text="Aguardando transcrição...", style='Info.TLabel', foreground='gray')
        self.llm_analysis_status.grid(row=2, column=0, pady=(0, 10))
        
        # Seção 3: Transcrição e Correções
        transcription_frame = ttk.LabelFrame(speech_frame, text="📝 Transcrição e Correções", padding="15")
        transcription_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        transcription_frame.columnconfigure(0, weight=1)
        transcription_frame.rowconfigure(1, weight=1)
        
        # Controles de transcrição
        controls_frame = ttk.Frame(transcription_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="🔍 Marcar Seleção", command=self.mark_selection_for_removal).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="❌ Desmarcar Seleção", command=self.unmark_selection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="🧹 Limpar Todas as Marcas", command=self.clear_all_marks).pack(side=tk.LEFT, padx=(0, 10))
        
        # Área de transcrição
        transcription_area_frame = ttk.Frame(transcription_frame)
        transcription_area_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        transcription_area_frame.columnconfigure(0, weight=1)
        transcription_area_frame.rowconfigure(0, weight=1)
        
        self.transcription_text = scrolledtext.ScrolledText(transcription_area_frame, font=('Arial', 10), wrap=tk.WORD)
        self.transcription_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para cores
        self.transcription_text.tag_configure("error", background="yellow", foreground="black")
        self.transcription_text.tag_configure("marked", background="red", foreground="white")
        self.transcription_text.tag_configure("llm_suggestion", background="orange", foreground="black")
        
        # Seção 4: Sugestões do LLM
        suggestions_frame = ttk.LabelFrame(speech_frame, text="💡 Sugestões do LLM", padding="15")
        suggestions_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        suggestions_frame.columnconfigure(0, weight=1)
        
        # Lista de sugestões
        self.suggestions_listbox = tk.Listbox(suggestions_frame, font=('Arial', 9), height=6)
        suggestions_scrollbar = ttk.Scrollbar(suggestions_frame, orient=tk.VERTICAL, command=self.suggestions_listbox.yview)
        self.suggestions_listbox.configure(yscrollcommand=suggestions_scrollbar.set)
        self.suggestions_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        suggestions_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Botões de ação para sugestões
        suggestion_buttons_frame = ttk.Frame(suggestions_frame)
        suggestion_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(suggestion_buttons_frame, text="✅ Aplicar Selecionada", command=self.apply_selected_suggestion).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(suggestion_buttons_frame, text="✅ Aplicar Todas", command=self.apply_all_suggestions).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(suggestion_buttons_frame, text="❌ Rejeitar Selecionada", command=self.reject_selected_suggestion).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(suggestion_buttons_frame, text="❌ Rejeitar Todas", command=self.reject_all_suggestions).pack(side=tk.LEFT)
        
        # Seção 5: Estatísticas
        stats_frame = ttk.LabelFrame(speech_frame, text="📊 Estatísticas", padding="15")
        stats_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.cuts_count_label = ttk.Label(stats_frame, text="Cortes marcados: 0", style='Info.TLabel')
        self.cuts_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.llm_suggestions_count = ttk.Label(stats_frame, text="Sugestões do LLM: 0", style='Info.TLabel')
        self.llm_suggestions_count.pack(side=tk.LEFT, padx=(0, 20))
        
        self.applied_suggestions_count = ttk.Label(stats_frame, text="Sugestões aplicadas: 0", style='Info.TLabel')
        self.applied_suggestions_count.pack(side=tk.LEFT)
        
        # Configurar grid weights
        speech_frame.columnconfigure(0, weight=1)
        speech_frame.rowconfigure(3, weight=1)
    
    def create_console_tab(self, parent):
        console_frame = ttk.Frame(parent, padding="20")
        console_frame.pack(fill=tk.BOTH, expand=True)
        # Título do console
        console_title = ttk.Label(console_frame, text="Console de Saída - Logs em Tempo Real", style='Section.TLabel')
        console_title.grid(row=0, column=0, pady=(0, 15))

        # Frame para controles do console
        console_controls = ttk.Frame(console_frame)
        console_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Botões de controle
        ttk.Button(console_controls, text="💾 Salvar Log", command=self.save_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(console_controls, text="🗑️ Limpar Console", command=self.clear_console).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(console_controls, text="🧹 Limpar Recursos", command=self.manual_cleanup).pack(side=tk.LEFT, padx=(0, 10))

        # Label com informações de status
        self.status_label = ttk.Label(console_controls, text="Pronto para editar", style='Info.TLabel')
        self.status_label.pack(side=tk.RIGHT)

        # Console de texto (ocupando todo o espaço restante)
        self.console_text = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, font=('Courier', 10), bg='black', fg='white')
        self.console_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Mensagem inicial
        self.log_message("Console inicializado - Pronto para uso", "INFO")
        self.log_message("Use esta aba para acompanhar o progresso da edição", "INFO")
        self.log_message("=" * 60, "INFO")
    
    def create_file_section(self, parent):
        """Cria a seção de seleção de arquivos"""
        file_frame = ttk.LabelFrame(parent, text="Arquivo de Vídeo", padding="15")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        file_frame.columnconfigure(1, weight=1)
        
        # Arquivo de entrada
        ttk.Label(file_frame, text="Vídeo para editar:", style='Section.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        input_frame = ttk.Frame(file_frame)
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_file, state='readonly', font=('Arial', 10))
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(input_frame, text="Escolher Vídeo", command=self.browse_input_file, 
                  style='Accent.TButton').grid(row=0, column=1)
        
        # Arquivo de saída
        ttk.Label(file_frame, text="Nome do arquivo de saída:", style='Section.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        output_frame = ttk.Frame(file_frame)
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_file, font=('Arial', 10))
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="Escolher Local", command=self.browse_output_file).grid(
            row=0, column=1)
        
        # Vincular eventos
        self.input_file.trace('w', self.update_output_suggestion)
        self.output_file.trace('w', self.update_command)
    
    def create_edit_section(self, parent):
        """Cria a seção de configurações de edição"""
        edit_frame = ttk.LabelFrame(parent, text="Configurações de Edição", padding="15")
        edit_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        edit_frame.columnconfigure(1, weight=1)
        
        # Tipo de saída
        ttk.Label(edit_frame, text="Tipo de saída:", style='Section.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.output_type = tk.StringVar(value="mp4")
        output_combo = ttk.Combobox(edit_frame, textvariable=self.output_type, state='readonly', font=('Arial', 10))
        output_combo['values'] = ['mp4', 'avi', 'mov', 'mkv']
        output_combo.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Sensibilidade do silêncio
        ttk.Label(edit_frame, text="Sensibilidade do silêncio (automática):", style='Section.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        sensitivity_frame = ttk.Frame(edit_frame)
        sensitivity_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        sensitivity_frame.columnconfigure(1, weight=1)
        
        self.sensitivity = tk.DoubleVar(value=0.04)
        sensitivity_scale = ttk.Scale(sensitivity_frame, from_=0.01, to=0.1, 
                                    variable=self.sensitivity, orient=tk.HORIZONTAL, state='disabled')
        sensitivity_scale.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.sensitivity_label = ttk.Label(sensitivity_frame, text="Automático", style='Info.TLabel')
        self.sensitivity_label.grid(row=0, column=2)
        
        # Explicação
        ttk.Label(edit_frame, text="O auto-editor detecta automaticamente o silêncio", 
                 style='Info.TLabel', foreground='gray').grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 15))
        
        # Tipo de corte
        ttk.Label(edit_frame, text="Tipo de corte:", style='Section.TLabel').grid(
            row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        self.cut_type = tk.StringVar(value="audio")
        cut_frame = ttk.Frame(edit_frame)
        cut_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Radiobutton(cut_frame, text="Por Áudio (recomendado)", variable=self.cut_type, 
                       value="audio").grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Radiobutton(cut_frame, text="Por Movimento", variable=self.cut_type, 
                       value="motion").grid(row=0, column=1, sticky=tk.W)
        
        # Vincular eventos
        self.sensitivity.trace('w', self.update_sensitivity_label)
        self.output_type.trace('w', self.update_command)
        self.cut_type.trace('w', self.update_command)
    
    def create_execution_section(self, parent):
        """Cria a seção de execução"""
        exec_frame = ttk.LabelFrame(parent, text="Execução", padding="15")
        exec_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        exec_frame.columnconfigure(0, weight=1)
        
        # Comando gerado
        ttk.Label(exec_frame, text="Comando que será executado:", style='Section.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.command_text = tk.Text(exec_frame, height=3, wrap=tk.WORD, state='disabled', 
                                   font=('Courier', 9))
        self.command_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(exec_frame, variable=self.progress_var, 
                                           mode='indeterminate')
        self.progress_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Botões de ação
        button_frame = ttk.Frame(exec_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="🎬 Iniciar Edição", 
                                     command=self.start_editing, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Parar", 
                                    command=self.stop_editing, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ Limpar Console", 
                                     command=self.clear_console)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão para abrir console
        ttk.Button(button_frame, text="📺 Abrir Console", 
                  command=self.open_console_tab).pack(side=tk.LEFT)
    
    def log_message(self, message, level="INFO"):
        """Registra uma mensagem no console com timestamp e nível"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        # Definir cores baseadas no nível
        if level == "ERROR":
            self.console_text.tag_config("error", foreground="red")
            self.console_text.insert(tk.END, formatted_message, "error")
        elif level == "WARNING":
            self.console_text.tag_config("warning", foreground="yellow")
            self.console_text.insert(tk.END, formatted_message, "warning")
        elif level == "SUCCESS":
            self.console_text.tag_config("success", foreground="green")
            self.console_text.insert(tk.END, formatted_message, "success")
        else:
            self.console_text.insert(tk.END, formatted_message)
        
        self.console_text.see(tk.END)
    
    def clear_console(self):
        """Limpa o console"""
        self.console_text.delete(1.0, tk.END)
        self.log_message("Console limpo", "INFO")
    
    def save_log(self):
        """Salva o log do console em um arquivo"""
        if not self.console_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Aviso", "Console vazio. Nada para salvar.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Salvar Log Como",
            defaultextension=".log",
            filetypes=[("Arquivos de Log", "*.log"), ("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.console_text.get(1.0, tk.END))
                self.log_message(f"Log salvo em: {filename}", "SUCCESS")
            except Exception as e:
                self.log_message(f"Erro ao salvar log: {str(e)}", "ERROR")
    
    def browse_input_file(self):
        """Abre diálogo para selecionar arquivo de entrada"""
        filetypes = [
            ("Arquivos de Vídeo", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("Todos os Arquivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Selecionar Vídeo para Editar",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file.set(filename)
            self.log_message(f"Arquivo selecionado: {filename}", "INFO")
    
    def browse_output_file(self):
        """Abre diálogo para selecionar arquivo de saída"""
        if not self.input_file.get():
            messagebox.showwarning("Aviso", "Selecione primeiro um arquivo de entrada.")
            return
        
        filetypes = [
            ("Arquivos MP4", "*.mp4"),
            ("Arquivos AVI", "*.avi"),
            ("Arquivos MOV", "*.mov"),
            ("Arquivos MKV", "*.mkv"),
            ("Todos os Arquivos", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="Salvar Vídeo Editado Como",
            filetypes=filetypes,
            defaultextension=f".{self.output_type.get()}"
        )
        
        if filename:
            self.output_file.set(filename)
            self.log_message(f"Arquivo de saída definido: {filename}", "INFO")
    
    def update_output_suggestion(self, *args):
        """Atualiza sugestão de nome de saída"""
        if self.input_file.get() and not self.output_file.get():
            base_name = os.path.splitext(os.path.basename(self.input_file.get()))[0]
            output_path = os.path.join(os.path.dirname(self.input_file.get()), 
                                     f"{base_name}_editado.{self.output_type.get()}")
            self.output_file.set(output_path)
    
    def update_sensitivity_label(self, *args):
        """Atualiza o label da sensibilidade"""
        self.sensitivity_label.config(text="Automático")
        self.update_command()
    
    def build_command(self) -> str:
        """Constrói o comando auto-editor"""
        if not self.input_file.get():
            return ""
        
        base_cmd = f"auto-editor {self.input_file.get()}"
        
        # Adicionar cortes de correção de fala
        speech_cuts = self.get_all_cuts_for_auto_editor()
        
        # Se há reorganização semântica, usar nova lógica
        if self.semantic_analysis_completed and self.final_clip_order:
            return self.build_semantic_reorganization_command(base_cmd)
        
        # Lógica original para correção de fala apenas
        if speech_cuts:
            cut_args = []
            for start, end in speech_cuts:
                cut_args.append(f"--cut-out {start},{end}")
            base_cmd += " " + " ".join(cut_args)
        
        # Adicionar tipo de saída
        base_cmd += f" --output {self.output_file.get()}"
        
        return base_cmd
    
    def build_semantic_reorganization_command(self, base_cmd):
        """Constrói comando para reorganização semântica"""
        # Etapa 1: Exportar clipes individuais
        output_dir = os.path.dirname(self.output_file.get())
        clips_dir = os.path.join(output_dir, "temp_clips")
        
        # Criar diretório temporário
        os.makedirs(clips_dir, exist_ok=True)
        
        # Gerar argumentos --add-in para cada clipe na nova ordem
        add_in_args = []
        for clip in self.final_clip_order:
            add_in_args.append(f"--add-in {clip['start']},{clip['end']}")
        
        # Comando para exportar clipes
        export_cmd = f"{base_cmd} {' '.join(add_in_args)} --export clip-sequence --output {clips_dir}"
        
        return export_cmd
    
    def run_auto_editor(self, command):
        """Executa o auto-editor com suporte à reorganização semântica"""
        try:
            self.log_message(f"Executando comando: {command}", "INFO")
            
            # Verificar se é reorganização semântica
            if "--export clip-sequence" in command:
                self.run_semantic_reorganization(command)
            else:
                # Execução normal
                self.run_normal_editing(command)
                
        except Exception as e:
            self.log_message(f"Erro ao executar auto-editor: {str(e)}", "ERROR")
            self.stop_editing()
    
    def run_semantic_reorganization(self, command):
        """Executa reorganização semântica em duas etapas"""
        try:
            # Etapa 1: Exportar clipes individuais
            self.log_message("Etapa 1: Exportando clipes individuais...", "INFO")
            
            self.process = subprocess.Popen(
                command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitorar saída
            self.monitor_semantic_output()
            
        except Exception as e:
            self.log_message(f"Erro na reorganização semântica: {str(e)}", "ERROR")
            self.stop_editing()
    
    def monitor_semantic_output(self):
        """Monitora a saída da reorganização semântica"""
        def monitor():
            try:
                while self.process and self.process.poll() is None:
                    output = self.process.stdout.readline()
                    if output:
                        self.output_queue.put(output.strip())
                        self.log_message(output.strip(), "INFO")
                
                # Verificar se processo terminou com sucesso
                if self.process and self.process.returncode == 0:
                    self.log_message("Etapa 1 concluída! Iniciando junção dos clipes...", "SUCCESS")
                    self.stitch_clips_sequence()
                else:
                    self.log_message("Erro na exportação dos clipes", "ERROR")
                    self.stop_editing()
                    
            except Exception as e:
                self.log_message(f"Erro no monitoramento: {str(e)}", "ERROR")
                self.stop_editing()
        
        # Executar monitoramento em thread separada
        import threading
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stitch_clips_sequence(self):
        """Junta os clipes exportados em um vídeo final"""
        try:
            output_dir = os.path.dirname(self.output_file.get())
            clips_dir = os.path.join(output_dir, "temp_clips")
            
            # Verificar se os clipes foram exportados
            if not os.path.exists(clips_dir):
                raise RuntimeError("Diretório de clipes não encontrado")
            
            # Listar clipes em ordem
            clip_files = []
            for i in range(len(self.final_clip_order)):
                clip_file = os.path.join(clips_dir, f"{i:04d}.mp4")
                if os.path.exists(clip_file):
                    clip_files.append(clip_file)
                else:
                    self.log_message(f"Aviso: Clipe {i:04d}.mp4 não encontrado", "WARNING")
            
            if not clip_files:
                raise RuntimeError("Nenhum clipe encontrado para juntar")
            
            # Criar arquivo de lista para ffmpeg
            filelist_path = os.path.join(output_dir, "filelist.txt")
            with open(filelist_path, 'w', encoding='utf-8') as f:
                for clip_file in clip_files:
                    f.write(f"file '{clip_file}'\n")
            
            # Comando ffmpeg para juntar clipes
            ffmpeg_cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', filelist_path,
                '-c', 'copy',
                self.output_file.get()
            ]
            
            self.log_message("Etapa 2: Juntando clipes com ffmpeg...", "INFO")
            self.log_message(f"Comando ffmpeg: {' '.join(ffmpeg_cmd)}", "INFO")
            
            # Executar ffmpeg
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message("🎉 Reorganização semântica concluída com sucesso!", "SUCCESS")
                self.cleanup_semantic_temp_files(clips_dir, filelist_path)
            else:
                self.log_message(f"Erro no ffmpeg: {result.stderr}", "ERROR")
            
            self.stop_editing()
            
        except Exception as e:
            self.log_message(f"Erro ao juntar clipes: {str(e)}", "ERROR")
            self.stop_editing()
    
    def cleanup_semantic_temp_files(self, clips_dir, filelist_path):
        """Limpa arquivos temporários da reorganização semântica"""
        try:
            # Remover arquivo de lista
            if os.path.exists(filelist_path):
                os.remove(filelist_path)
                self.log_message("Arquivo de lista removido", "INFO")
            
            # Remover diretório de clipes
            if os.path.exists(clips_dir):
                import shutil
                shutil.rmtree(clips_dir)
                self.log_message("Diretório de clipes temporários removido", "INFO")
                
        except Exception as e:
            self.log_message(f"Erro ao limpar arquivos temporários: {str(e)}", "WARNING")
    
    def run_normal_editing(self, command):
        """Executa edição normal (sem reorganização semântica)"""
        self.process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start()
        
        self.log_message("Iniciando edição...", "INFO")
    
    def check_dependencies(self):
        """Verifica se auto-editor e ffmpeg estão instalados"""
        self.log_message("Verificando dependências...", "INFO")
        
        missing = []
        
        if not shutil.which("auto-editor"):
            missing.append("auto-editor")
            self.log_message("❌ auto-editor não encontrado", "ERROR")
        else:
            self.log_message("✅ auto-editor encontrado", "SUCCESS")
        
        if not shutil.which("ffmpeg"):
            missing.append("ffmpeg")
            self.log_message("❌ ffmpeg não encontrado", "ERROR")
        else:
            self.log_message("✅ ffmpeg encontrado", "SUCCESS")
        
        # Verificar Whisper
        if WHISPER_AVAILABLE:
            self.log_message("✅ whisper encontrado", "SUCCESS")
            self.log_message("🎯 Funcionalidade de correção de fala por IA disponível!", "SUCCESS")
        else:
            self.log_message("⚠️ whisper não encontrado", "WARNING")
            self.log_message("📦 Execute: python3 setup.py para instalar whisper", "WARNING")
        
        if missing:
            self.log_message(f"Dependências ausentes: {', '.join(missing)}", "ERROR")
            self.log_message("Execute: python3 setup.py", "WARNING")
            messagebox.showerror(
                "Dependências Ausentes",
                f"Os seguintes programas não foram encontrados:\n{', '.join(missing)}\n\n"
                "Execute: python3 setup.py"
            )
        else:
            self.log_message("Todas as dependências básicas estão instaladas", "SUCCESS")
    
    def start_editing(self):
        """Inicia o processo de edição"""
        if not self.input_file.get():
            messagebox.showerror("Erro", "Selecione um arquivo de vídeo.")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Erro", "Especifique um arquivo de saída.")
            return
        
        command = self.build_command()
        if not command:
            messagebox.showerror("Erro", "Comando inválido.")
            return
        
        # Limpar console e registrar início
        self.console_text.delete(1.0, tk.END)
        self.log_message("=" * 60, "INFO")
        self.log_message("INICIANDO PROCESSO DE EDIÇÃO", "INFO")
        self.log_message("=" * 60, "INFO")
        self.log_message(f"Arquivo de entrada: {self.input_file.get()}", "INFO")
        self.log_message(f"Arquivo de saída: {self.output_file.get()}", "INFO")
        self.log_message(f"Tipo de corte: {self.cut_type.get()}", "INFO")
        self.log_message(f"Detecção de silêncio: Automática", "INFO")
        
        # Informações sobre cortes de fala por IA
        speech_cuts = self.get_all_cuts_for_auto_editor()
        if speech_cuts:
            self.log_message(f"Cortes de fala por IA: {len(speech_cuts)} intervalos", "INFO")
            for i, (start, end) in enumerate(speech_cuts[:5]):  # Mostrar apenas os primeiros 5
                self.log_message(f"  Corte {i+1}: {start:.1f}s - {end:.1f}s", "INFO")
            if len(speech_cuts) > 5:
                self.log_message(f"  ... e mais {len(speech_cuts) - 5} cortes", "INFO")
        else:
            self.log_message("Cortes de fala por IA: Nenhum", "INFO")
        
        self.log_message(f"Comando: {command}", "INFO")
        self.log_message("-" * 60, "INFO")
        
        # Abrir automaticamente a aba do console
        self.notebook.select(1)  # Seleciona a aba do console (índice 1)
        
        # Atualizar interface
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_running = True
        self.status_label.config(text="Editando...")
        
        # Iniciar barra de progresso
        self.progress_bar.start()
        
        # Executar em thread separada
        thread = threading.Thread(target=self.run_auto_editor, args=(command,))
        thread.daemon = True
        thread.start()
    
    def stop_editing(self):
        """Para o processo de edição"""
        if self.process:
            self.log_message("Interrompendo processo...", "WARNING")
            self.process.terminate()
            self.is_running = False
            self.log_message("Processo interrompido pelo usuário", "WARNING")
    
    def monitor_output(self):
        """Monitora a fila de saída e atualiza o console"""
        try:
            while True:
                line = self.output_queue.get_nowait()
                if line == "DONE":
                    # Processo terminou
                    self.start_button.config(state='normal')
                    self.stop_button.config(state='disabled')
                    self.is_running = False
                    self.progress_bar.stop()
                    self.status_label.config(text="Pronto para editar")
                else:
                    # Adicionar linha ao console
                    self.log_message(line, "INFO")
        except queue.Empty:
            pass
        
        # Agendar próxima verificação
        self.root.after(100, self.monitor_output)
    
    def open_console_tab(self):
        """Abre a aba do console"""
        self.notebook.select(1)  # Seleciona a aba do console
        self.log_message("Aba do console aberta manualmente", "INFO")
    
    def start_speech_analysis(self):
        """Inicia a análise de fala com Whisper"""
        if not self.input_file.get():
            messagebox.showerror("Erro", "Selecione um arquivo de vídeo primeiro.")
            return
        
        if not WHISPER_AVAILABLE:
            messagebox.showerror("Erro", "Whisper não está instalado. Execute: python3 setup.py")
            return
        
        # Atualizar interface
        self.analyze_button.config(state='disabled')
        self.analysis_status.config(text="Iniciando análise...", foreground='blue')
        
        # Executar em thread separada
        thread = threading.Thread(target=self.run_speech_analysis)
        thread.daemon = True
        thread.start()
    
    def run_speech_analysis(self):
        """Executa a análise de fala em thread separada"""
        try:
            self.log_message("Iniciando análise de fala com Whisper...", "INFO")
            self.log_memory_usage("início da análise")
            self.analysis_status.config(text="Extraindo áudio...", foreground='blue')
            audio_file = self.extract_audio()
            if not audio_file:
                return
            self.log_memory_usage("após extração de áudio")
            if self.whisper_mode.get() == "api":
                self.analysis_status.config(text="Transcrevendo via API OpenAI...", foreground='blue')
                self.log_message("Transcrevendo via API OpenAI...", "INFO")
                result = self.transcribe_with_openai_api(audio_file)
                self.log_message(f"Resposta da API OpenAI: {result}", "INFO")
                self.whisper_result = result
                self.log_memory_usage("após receber resposta da API")
            else:
                self.analysis_status.config(text="Carregando modelo Whisper...", foreground='blue')
                self.log_message("Carregando modelo Whisper...", "INFO")
                device = "cuda" if self.use_gpu.get() else "cpu"
                model = whisper.load_model(self.whisper_model.get(), device=device)
                self.log_message(f"Modelo {self.whisper_model.get()} carregado em {device}", "INFO")
                self.log_memory_usage("após carregar modelo")
                self.analysis_status.config(text="Transcrevendo com Whisper local...", foreground='blue')
                self.log_message("Iniciando transcrição...", "INFO")
                result = model.transcribe(audio_file, word_timestamps=True)
                self.whisper_result = result
                del model
                import gc
                gc.collect()
                self.log_memory_usage("após transcrição local")
            # Etapa C: Analisar transcrição
            self.analysis_status.config(text="Analisando texto...", foreground='blue')
            self.log_message("Analisando transcrição para detectar erros...", "INFO")
            self.analyze_transcription_for_errors()
            self.log_memory_usage("após análise de erros")
            # Etapa D: Popular GUI
            self.populate_transcription_gui()
            self.log_memory_usage("após popular GUI")
            self.clear_whisper_result()
            self.log_memory_usage("após otimizar resultado")
            try:
                os.remove(audio_file)
                self.log_message("Arquivo temporário removido", "INFO")
            except Exception as e:
                self.log_message(f"Erro ao remover arquivo temporário: {str(e)}", "WARNING")
            # --- NOVO: Pipeline automático LLM ---
            self.analysis_status.config(text="Enviando para LLM...", foreground='blue')
            self.log_message("Iniciando análise automática por LLM...", "INFO")
            # Chamar LLM e aplicar sugestões automaticamente
            self.run_llm_analysis_auto()
            self.analysis_status.config(text="Correção automática concluída!", foreground='green')
            self.log_message("Correção automática concluída!", "SUCCESS")
            self.log_memory_usage("final da análise")
        except Exception as e:
            import traceback
            err_msg = f"Erro na análise de fala: {str(e)}\n{traceback.format_exc()}"
            self.log_message(err_msg, "ERROR")
            self.analysis_status.config(text="Erro na análise", foreground='red')
            self.last_whisper_error.set(str(e))
        finally:
            self.analyze_button.config(state='normal')

    def run_llm_analysis_auto(self):
        """Executa a análise por LLM e aplica todas as sugestões automaticamente"""
        try:
            # Obter transcrição completa
            full_transcription = self.get_full_transcription()
            prompt = self.build_speech_analysis_prompt(full_transcription)
            provider = self.selected_llm_provider.get()
            model = self.selected_llm_model.get()
            response = self.call_llm_api(provider, model, prompt)
            self.process_llm_suggestions(response)
            # Aplicar todas as sugestões automaticamente
            for suggestion in self.llm_suggestions[:]:
                self.mark_llm_suggestion(suggestion)
            self.llm_suggestions.clear()
            self.populate_suggestions_list()
            self.update_suggestions_count()
            # Desabilitar botões de análise LLM e sugestões
            if hasattr(self, 'llm_analyze_button'):
                self.llm_analyze_button.config(state='disabled')
            if hasattr(self, 'apply_all_suggestions'):
                self.apply_all_suggestions = lambda: None
            if hasattr(self, 'apply_selected_suggestion'):
                self.apply_selected_suggestion = lambda: None
        except Exception as e:
            self.log_message(f"Erro na análise automática por LLM: {e}", "ERROR")
    
    def extract_audio(self):
        """Extrai áudio do vídeo usando ffmpeg"""
        try:
            # Criar arquivo temporário
            temp_dir = tempfile.gettempdir()
            audio_file = os.path.join(temp_dir, f"temp_audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
            
            # Comando ffmpeg para extrair áudio
            cmd = [
                'ffmpeg', '-i', self.input_file.get(),
                '-vn', '-c:a', 'libmp3lame', '-q:a', '2',
                '-y', audio_file
            ]
            
            self.log_message(f"Extraindo áudio: {' '.join(cmd)}", "INFO")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message(f"Áudio extraído: {audio_file}", "INFO")
                return audio_file
            else:
                self.log_message(f"Erro ao extrair áudio: {result.stderr}", "ERROR")
                return None
                
        except Exception as e:
            self.log_message(f"Erro ao extrair áudio: {str(e)}", "ERROR")
            return None
    
    def analyze_transcription_for_errors(self):
        """Analisa a transcrição para detectar erros - OTIMIZADO PARA MEMÓRIA"""
        self.error_segments = []
        if not self.whisper_result:
            return
        
        # Verificar se temos words (nova API) ou segments (API antiga)
        words = self.whisper_result.get('words')
        if not words:
            self.log_message("A resposta da API não contém 'words' com timestamps. Verifique se sua conta OpenAI tem acesso a timestamps por palavra.", "ERROR")
            self.analysis_status.config(text="API não retornou timestamps. Verifique seu plano OpenAI.", foreground='red')
            self.last_whisper_error.set("API não retornou timestamps. Verifique seu plano OpenAI.")
            return
        
        self.log_message(f"Analisando {len(words)} palavras para detectar erros...", "INFO")
        
        # Palavras de preenchimento padrão
        default_fillers = {'uh', 'um', 'ah', 'hmm', 'er', 'um', 'uhm'}
        
        # Adicionar palavras personalizadas
        custom_fillers = set(word.strip().lower() for word in self.custom_fillers.get().split(','))
        all_fillers = default_fillers.union(custom_fillers)
        
        # Processar em lotes menores para economizar memória
        batch_size = 200
        errors_found = 0
        
        for i in range(0, len(words), batch_size):
            batch = words[i:i + batch_size]
            
            # Analisar cada palavra no lote
            for j, word_info in enumerate(batch):
                word = word_info['word'].strip().lower()
                start_time = word_info['start']
                end_time = word_info['end']
                
                # Detectar palavras de preenchimento
                if self.detect_fillers.get():
                    if word in all_fillers:
                        self.error_segments.append({
                            'type': 'filler',
                            'text': word_info['word'],  # Usar palavra original
                            'start': start_time,
                            'end': end_time,
                            'segment_text': word_info['word']
                        })
                        errors_found += 1
                
                # Detectar repetições (palavras consecutivas iguais)
                if self.detect_repetitions.get():
                    # Verificar se não é a última palavra do lote
                    if j < len(batch) - 1:
                        next_word = batch[j + 1]['word'].strip().lower()
                        if word == next_word and len(word) > 2:
                            # Marcar ambas as palavras como repetição
                            self.error_segments.append({
                                'type': 'repetition',
                                'text': f"{word_info['word']} {batch[j + 1]['word']}",
                                'start': start_time,
                                'end': batch[j + 1]['end'],
                                'segment_text': f"{word_info['word']} {batch[j + 1]['word']}"
                            })
                            errors_found += 1
                    # Verificar se não é a última palavra geral
                    elif i + j < len(words) - 1:
                        next_word = words[i + j + 1]['word'].strip().lower()
                        if word == next_word and len(word) > 2:
                            self.error_segments.append({
                                'type': 'repetition',
                                'text': f"{word_info['word']} {words[i + j + 1]['word']}",
                                'start': start_time,
                                'end': words[i + j + 1]['end'],
                                'segment_text': f"{word_info['word']} {words[i + j + 1]['word']}"
                            })
                            errors_found += 1
            
            # Forçar garbage collection a cada lote
            if i % (batch_size * 3) == 0:
                import gc
                gc.collect()
                self.log_message(f"Analisadas {i + len(batch)} palavras, {errors_found} erros encontrados...", "INFO")
        
        self.log_message(f"Análise concluída: {errors_found} erros detectados", "SUCCESS")
    
    def populate_transcription_gui(self):
        """Popula a GUI com a transcrição e marca os erros - OTIMIZADO PARA MEMÓRIA"""
        if not self.whisper_result:
            return
        
        # Limpar área de transcrição
        self.transcription_text.delete(1.0, tk.END)
        
        # Verificar se temos words (nova API) ou segments (API antiga)
        words = self.whisper_result.get('words')
        if not words:
            self.log_message("A resposta da API não contém 'words' com timestamps.", "ERROR")
            return
        
        self.log_message(f"Processando {len(words)} palavras...", "INFO")
        
        # Processar e inserir diretamente, sem construir string gigante
        sentence_words = []
        sentence_start = None
        sentences_processed = 0
        
        # Processar em lotes muito menores para economizar memória
        batch_size = 100  # Reduzido de 1000 para 100
        for i in range(0, len(words), batch_size):
            batch = words[i:i + batch_size]
            
            for word_info in batch:
                word = word_info['word']
                
                # Iniciar nova frase se não temos uma
                if sentence_start is None:
                    sentence_start = word_info['start']
                
                sentence_words.append(word)
                
                # Finalizar frase se encontrou pontuação de fim
                if word.strip() in ['.', '!', '?']:
                    # Construir e inserir frase imediatamente
                    sentence_text = ''.join(sentence_words).strip()
                    sentence_end = word_info['end']
                    
                    timestamp = f"[{sentence_start:.1f}s - {sentence_end:.1f}s] "
                    line_text = timestamp + sentence_text + "\n\n"
                    
                    # Inserir diretamente no widget
                    self.transcription_text.insert(tk.END, line_text)
                    
                    # Limpar lista de palavras da frase imediatamente
                    sentence_words.clear()
                    sentence_start = None
                    sentences_processed += 1
                    
                    # Atualizar GUI a cada 10 frases
                    if sentences_processed % 10 == 0:
                        self.transcription_text.see(tk.END)
                        self.transcription_text.update_idletasks()
                        self.log_message(f"Processadas {sentences_processed} frases...", "INFO")
            
            # Forçar garbage collection a cada lote
            if i % (batch_size * 5) == 0:
                import gc
                gc.collect()
        
        # Adicionar última frase se não terminou com pontuação
        if sentence_words:
            sentence_text = ''.join(sentence_words).strip()
            sentence_end = words[-1]['end']
            
            timestamp = f"[{sentence_start:.1f}s - {sentence_end:.1f}s] "
            line_text = timestamp + sentence_text + "\n\n"
            
            self.transcription_text.insert(tk.END, line_text)
            sentences_processed += 1
        
        # Limpar variáveis para liberar memória
        del sentence_words, sentence_start
        import gc
        gc.collect()
        
        self.log_message(f"Transcrição concluída: {sentences_processed} frases processadas", "SUCCESS")
        
        # Extrair clipes de fala para reorganização semântica
        self.extract_speech_clips()
        
        # Marcar erros detectados automaticamente
        self.mark_detected_errors()
        
        # Atualizar contador
        self.update_cuts_count()
    
    def extract_speech_clips(self):
        """Extrai clipes de fala da transcrição para reorganização semântica"""
        if not self.whisper_result or not self.whisper_result.get('words'):
            return
        
        self.log_message("Extraindo clipes de fala para análise semântica...", "INFO")
        
        words = self.whisper_result['words']
        self.speech_clips = []
        clip_id = 1
        
        # Agrupar palavras em clipes baseados em pausas e pontuação
        current_clip_words = []
        current_start = None
        
        for word_info in words:
            word = word_info['word']
            
            # Iniciar novo clipe se não temos um
            if current_start is None:
                current_start = word_info['start']
            
            current_clip_words.append(word)
            
            # Finalizar clipe se encontrou pontuação de fim ou pausa longa
            if word.strip() in ['.', '!', '?']:
                # Verificar se há pausa significativa após pontuação
                if len(words) > words.index(word_info) + 1:
                    next_word = words[words.index(word_info) + 1]
                    pause_duration = next_word['start'] - word_info['end']
                    
                    # Se pausa > 1 segundo, finalizar clipe
                    if pause_duration > 1.0:
                        clip_text = ''.join(current_clip_words).strip()
                        clip_end = word_info['end']
                        
                        self.speech_clips.append({
                            'id': clip_id,
                            'start': current_start,
                            'end': clip_end,
                            'text': clip_text,
                            'duration': clip_end - current_start
                        })
                        
                        clip_id += 1
                        current_clip_words = []
                        current_start = None
        
        # Adicionar último clipe se não terminou com pontuação
        if current_clip_words:
            clip_text = ''.join(current_clip_words).strip()
            clip_end = words[-1]['end']
            
            self.speech_clips.append({
                'id': clip_id,
                'start': current_start,
                'end': clip_end,
                'text': clip_text,
                'duration': clip_end - current_start
            })
        
        self.log_message(f"Extraídos {len(self.speech_clips)} clipes de fala", "SUCCESS")
        
        # Habilitar botão de análise semântica
        self.semantic_analyze_button.config(state='normal')
        self.semantic_status.config(text="Pronto para análise semântica", foreground='green')
        
        # Popular lista de ordem original
        self.populate_original_clips_list()
    
    def populate_original_clips_list(self):
        """Popula a lista de clipes na ordem original"""
        self.original_listbox.delete(0, tk.END)
        
        for clip in self.speech_clips:
            # Formatar texto para exibição
            start_time = f"{clip['start']:.1f}s"
            end_time = f"{clip['end']:.1f}s"
            text_preview = clip['text'][:50] + "..." if len(clip['text']) > 50 else clip['text']
            
            display_text = f"[{start_time} - {end_time}] {text_preview}"
            self.original_listbox.insert(tk.END, display_text)
    
    def mark_detected_errors(self):
        """Marca os erros detectados automaticamente no texto"""
        for error in self.error_segments:
            # Encontrar o texto do erro na transcrição
            text_to_find = error['text']
            start_pos = self.transcription_text.search(text_to_find, 1.0, tk.END)
            
            if start_pos:
                end_pos = f"{start_pos}+{len(text_to_find)}c"
                self.transcription_text.tag_add("error", start_pos, end_pos)
    
    def mark_selection_for_removal(self):
        """Marca a seleção atual para remoção"""
        try:
            selection = self.transcription_text.tag_ranges(tk.SEL)
            if selection:
                start, end = selection
                
                # Obter o texto selecionado
                selected_text = self.transcription_text.get(start, end)
                
                # Encontrar timestamps para a seleção
                timestamps = self.find_timestamps_for_selection(start, end)
                
                if timestamps:
                    segment = {
                        'type': 'manual',
                        'text': selected_text,
                        'start': timestamps['start'],
                        'end': timestamps['end'],
                        'segment_text': selected_text
                    }
                    
                    self.marked_segments.append(segment)
                    self.transcription_text.tag_add("marked", start, end)
                    
                    self.log_message(f"Marcado para remoção: {selected_text[:50]}... ({timestamps['start']:.1f}s - {timestamps['end']:.1f}s)", "INFO")
                    self.update_cuts_count()
                else:
                    messagebox.showwarning("Aviso", "Não foi possível determinar os timestamps para a seleção.")
            else:
                messagebox.showwarning("Aviso", "Selecione um texto primeiro.")
        except Exception as e:
            self.log_message(f"Erro ao marcar seleção: {str(e)}", "ERROR")
    
    def unmark_selection(self):
        """Remove a marcação da seleção atual"""
        try:
            selection = self.transcription_text.tag_ranges(tk.SEL)
            if selection:
                start, end = selection
                selected_text = self.transcription_text.get(start, end)
                
                # Remover da lista de segmentos marcados
                self.marked_segments = [s for s in self.marked_segments if s['text'] != selected_text]
                
                # Remover tag
                self.transcription_text.tag_remove("marked", start, end)
                
                self.log_message(f"Desmarcado: {selected_text[:50]}...", "INFO")
                self.update_cuts_count()
            else:
                messagebox.showwarning("Aviso", "Selecione um texto marcado primeiro.")
        except Exception as e:
            self.log_message(f"Erro ao desmarcar seleção: {str(e)}", "ERROR")
    
    def find_timestamps_for_selection(self, start, end):
        """Encontra os timestamps para uma seleção de texto"""
        try:
            # Obter a linha onde está a seleção
            start_line = self.transcription_text.index(start).split('.')[0]
            end_line = self.transcription_text.index(end).split('.')[0]
            
            # Procurar por timestamps nas linhas
            for line_num in range(int(start_line), int(end_line) + 1):
                line_start = f"{line_num}.0"
                line_end = f"{line_num}.end"
                line_text = self.transcription_text.get(line_start, line_end)
                
                # Extrair timestamp da linha
                if '[' in line_text and ']' in line_text:
                    timestamp_part = line_text[line_text.find('['):line_text.find(']')+1]
                    times = timestamp_part.strip('[]').split(' - ')
                    if len(times) == 2:
                        return {
                            'start': float(times[0].replace('s', '')),
                            'end': float(times[1].replace('s', ''))
                        }
            
            return None
        except Exception as e:
            self.log_message(f"Erro ao encontrar timestamps: {str(e)}", "ERROR")
            return None
    
    def update_cuts_count(self):
        """Atualiza o contador de cortes"""
        total_cuts = len(self.error_segments) + len(self.marked_segments)
        self.cuts_count_label.config(text=f"Cortes marcados: {total_cuts}")
    
    def get_all_cuts_for_auto_editor(self):
        """Retorna todos os cortes para o auto-editor"""
        all_cuts = []
        
        # Adicionar erros detectados automaticamente
        for error in self.error_segments:
            all_cuts.append((error['start'], error['end']))
        
        # Adicionar segmentos marcados manualmente
        for segment in self.marked_segments:
            all_cuts.append((segment['start'], segment['end']))
        
        # Ordenar e mesclar intervalos sobrepostos
        all_cuts.sort(key=lambda x: x[0])
        
        merged_cuts = []
        for cut in all_cuts:
            if not merged_cuts or cut[0] > merged_cuts[-1][1]:
                merged_cuts.append(cut)
            else:
                # Mesclar intervalos sobrepostos
                merged_cuts[-1] = (merged_cuts[-1][0], max(merged_cuts[-1][1], cut[1]))
        
        return merged_cuts
    
    def update_command(self, *args):
        """Atualiza o comando exibido (se o widget existir)"""
        if hasattr(self, 'command_text'):
            self.command_text.config(state='normal')
            self.command_text.delete(1.0, tk.END)
            cmd = self.build_command()
            self.command_text.insert(tk.END, cmd)
            self.command_text.config(state='disabled')
    
    def transcribe_with_openai_api(self, audio_file):
        """Transcreve usando API da OpenAI"""
        if not OPENAI_AVAILABLE:
            raise RuntimeError("Biblioteca openai não instalada")
        
        api_key = self.api_keys.get("openai")
        if not api_key:
            raise RuntimeError("API Key da OpenAI não configurada")
        
        client = openai.OpenAI(api_key=api_key)
        
        with open(audio_file, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
        
        return transcript.model_dump()
    
    def create_whisper_config_section(self, parent):
        config_frame = ttk.LabelFrame(parent, text="Configurações do Whisper", padding="15")
        config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        # Modelo do Whisper
        ttk.Label(config_frame, text="Modelo do Whisper:", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.whisper_model = tk.StringVar(value="base")
        model_combo = ttk.Combobox(config_frame, textvariable=self.whisper_model, state='readonly', font=('Arial', 10))
        model_combo['values'] = ['tiny', 'base', 'small', 'medium', 'large']
        model_combo.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        model_info = ttk.Label(config_frame, text="tiny: mais rápido, base: equilibrado, small: melhor precisão, medium/large: máxima precisão", style='Info.TLabel', foreground='gray')
        model_info.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        self.use_gpu = tk.BooleanVar(value=False)
        gpu_check = ttk.Checkbutton(config_frame, text="Processar em GPU (se disponível)", variable=self.use_gpu)
        gpu_check.grid(row=3, column=0, columnspan=2, sticky=tk.W)

    def create_analysis_config_section(self, parent):
        analysis_frame = ttk.LabelFrame(parent, text="Configurações da Análise", padding="15")
        analysis_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        analysis_frame.columnconfigure(1, weight=1)
        self.detect_repetitions = tk.BooleanVar(value=True)
        ttk.Checkbutton(analysis_frame, text="Detectar e marcar repetições de frases", variable=self.detect_repetitions).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        self.detect_fillers = tk.BooleanVar(value=True)
        ttk.Checkbutton(analysis_frame, text="Detectar e marcar palavras de preenchimento (ex: 'um', 'ah')", variable=self.detect_fillers).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        ttk.Label(analysis_frame, text="Palavras de preenchimento personalizadas (separadas por vírgula):", style='Section.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.custom_fillers = tk.StringVar(value="tipo, né, sabe, então")
        ttk.Entry(analysis_frame, textvariable=self.custom_fillers, font=('Arial', 10)).grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.analyze_button = ttk.Button(analysis_frame, text="🎤 1. Analisar Fala com Whisper", command=self.start_speech_analysis, style='Accent.TButton')
        self.analyze_button.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        self.analysis_status = ttk.Label(analysis_frame, text="Aguardando análise...", style='Info.TLabel', foreground='gray')
        self.analysis_status.grid(row=5, column=0, columnspan=2, pady=(5, 0))

    def create_transcription_section(self, parent):
        trans_frame = ttk.LabelFrame(parent, text="Transcrição Interativa", padding="15")
        trans_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        trans_frame.columnconfigure(0, weight=1)
        trans_frame.rowconfigure(1, weight=1)
        controls_frame = ttk.Frame(trans_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(controls_frame, text="🔴 Marcar Seleção para Remover", command=self.mark_selection_for_removal).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="🔄 Desmarcar Seleção", command=self.unmark_selection).pack(side=tk.LEFT, padx=(0, 10))
        self.cuts_count_label = ttk.Label(controls_frame, text="Cortes marcados: 0", style='Info.TLabel')
        self.cuts_count_label.pack(side=tk.RIGHT)
        self.transcription_text = scrolledtext.ScrolledText(trans_frame, wrap=tk.WORD, font=('Courier', 10), bg='white', fg='black')
        self.transcription_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.transcription_text.tag_configure("error", background="yellow")
        self.transcription_text.tag_configure("marked", background="red", foreground="white")
        self.transcription_text.tag_configure("selected", background="lightblue")
        self.whisper_result = None
        self.error_segments = []
        self.marked_segments = []
        self.current_selection = None

    def create_semantic_reorganization_tab(self, parent):
        """Cria a aba de reorganização semântica por IA"""
        semantic_frame = ttk.Frame(parent, padding="20")
        semantic_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(semantic_frame, text="Reorganização Semântica por IA - GPT-4o", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Verificar se OpenAI está disponível
        if not OPENAI_AVAILABLE:
            warning_frame = ttk.Frame(semantic_frame)
            warning_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
            ttk.Label(warning_frame, text="⚠️ Biblioteca OpenAI não instalada", style='Section.TLabel', foreground='red').pack()
            ttk.Label(warning_frame, text="Execute: pip install openai", style='Info.TLabel').pack()
            return
        
        # Seção 1: Campo de Objetivo
        objective_frame = ttk.LabelFrame(semantic_frame, text="Objetivo do Vídeo", padding="15")
        objective_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        objective_frame.columnconfigure(0, weight=1)
        
        ttk.Label(objective_frame, text="Qual é o objetivo deste vídeo?", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.video_objective = tk.StringVar(value="Criar um conteúdo claro e impactante")
        objective_text = tk.Text(objective_frame, height=4, wrap=tk.WORD, font=('Arial', 10))
        objective_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        objective_text.insert(1.0, self.video_objective.get())
        
        # Exemplos de objetivos
        examples_frame = ttk.Frame(objective_frame)
        examples_frame.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        ttk.Label(examples_frame, text="Exemplos:", style='Info.TLabel', foreground='gray').pack(anchor=tk.W)
        ttk.Label(examples_frame, text="• 'Criar um tutorial para iniciantes'", style='Info.TLabel', foreground='gray').pack(anchor=tk.W)
        ttk.Label(examples_frame, text="• 'Fazer uma análise de produto concisa'", style='Info.TLabel', foreground='gray').pack(anchor=tk.W)
        ttk.Label(examples_frame, text="• 'Contar uma história impactante'", style='Info.TLabel', foreground='gray').pack(anchor=tk.W)
        
        # Seção 2: Botão de Análise
        analysis_frame = ttk.LabelFrame(semantic_frame, text="Análise Semântica", padding="15")
        analysis_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        analysis_frame.columnconfigure(0, weight=1)
        
        self.semantic_analyze_button = ttk.Button(analysis_frame, text="🧠 2. Analisar Estrutura da Narrativa", 
                                                command=self.start_semantic_analysis, style='Accent.TButton', state='disabled')
        self.semantic_analyze_button.grid(row=0, column=0, pady=(0, 10))
        
        self.semantic_status = ttk.Label(analysis_frame, text="Aguardando transcrição do Whisper...", style='Info.TLabel', foreground='gray')
        self.semantic_status.grid(row=1, column=0, pady=(0, 10))
        
        # Seção 3: Visualização das Sugestões
        suggestions_frame = ttk.LabelFrame(semantic_frame, text="Sugestões da IA", padding="15")
        suggestions_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        suggestions_frame.columnconfigure(0, weight=1)
        suggestions_frame.columnconfigure(1, weight=1)
        
        # Coluna 1: Ordem Original
        original_frame = ttk.Frame(suggestions_frame)
        original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        original_frame.columnconfigure(0, weight=1)
        original_frame.rowconfigure(1, weight=1)
        
        ttk.Label(original_frame, text="Ordem Original", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.original_listbox = tk.Listbox(original_frame, font=('Arial', 9), selectmode=tk.SINGLE)
        original_scrollbar = ttk.Scrollbar(original_frame, orient=tk.VERTICAL, command=self.original_listbox.yview)
        self.original_listbox.configure(yscrollcommand=original_scrollbar.set)
        self.original_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        original_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Coluna 2: Sugestão da IA
        suggestion_frame = ttk.Frame(suggestions_frame)
        suggestion_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        suggestion_frame.columnconfigure(0, weight=1)
        suggestion_frame.rowconfigure(1, weight=1)
        
        ttk.Label(suggestion_frame, text="Sugestão da IA", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.suggestion_listbox = tk.Listbox(suggestion_frame, font=('Arial', 9), selectmode=tk.SINGLE)
        suggestion_scrollbar = ttk.Scrollbar(suggestion_frame, orient=tk.VERTICAL, command=self.suggestion_listbox.yview)
        self.suggestion_listbox.configure(yscrollcommand=suggestion_scrollbar.set)
        self.suggestion_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        suggestion_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Seção 4: Clipes Excluídos
        deleted_frame = ttk.LabelFrame(semantic_frame, text="Clipes com Sugestão de Exclusão", padding="15")
        deleted_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        deleted_frame.columnconfigure(0, weight=1)
        
        self.deleted_listbox = tk.Listbox(deleted_frame, font=('Arial', 9), selectmode=tk.SINGLE, height=4)
        deleted_scrollbar = ttk.Scrollbar(deleted_frame, orient=tk.VERTICAL, command=self.deleted_listbox.yview)
        self.deleted_listbox.configure(yscrollcommand=deleted_scrollbar.set)
        self.deleted_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        deleted_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Botão para restaurar clipe excluído
        restore_button = ttk.Button(deleted_frame, text="🔄 Restaurar Clipe Selecionado", command=self.restore_deleted_clip)
        restore_button.grid(row=1, column=0, pady=(10, 0))
        
        # Seção 5: Botões de Ação Final
        action_frame = ttk.Frame(semantic_frame)
        action_frame.grid(row=5, column=0, columnspan=2, pady=(0, 20))
        
        self.accept_button = ttk.Button(action_frame, text="✅ Aceitar Sugestão", command=self.accept_semantic_suggestions, 
                                       style='Accent.TButton', state='disabled')
        self.accept_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.discard_button = ttk.Button(action_frame, text="❌ Descartar Tudo", command=self.discard_semantic_suggestions, 
                                        state='disabled')
        self.discard_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status final
        self.semantic_final_status = ttk.Label(semantic_frame, text="", style='Info.TLabel')
        self.semantic_final_status.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        # Configurar grid weights para expandir
        semantic_frame.columnconfigure(0, weight=1)
        semantic_frame.rowconfigure(3, weight=1)

    def on_closing(self):
        """Limpa recursos antes de fechar a aplicação"""
        try:
            # Parar processo em execução
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.log_message("Processo auto-editor finalizado", "INFO")
            
            # Limpar recursos do Whisper
            if hasattr(self, 'whisper_result'):
                del self.whisper_result
            if hasattr(self, 'error_segments'):
                del self.error_segments
            if hasattr(self, 'marked_segments'):
                del self.marked_segments
            
            # Limpar arquivos temporários
            self.cleanup_temp_files()
            
            # Otimizar memória
            self.optimize_memory_usage()
            
            self.log_message("Recursos liberados. Fechando aplicação...", "INFO")
            
        except Exception as e:
            print(f"Erro ao limpar recursos: {str(e)}")
        
        finally:
            # Fechar a janela
            self.root.destroy()

    def cleanup_temp_files(self):
        """Limpa arquivos temporários criados durante a execução"""
        try:
            temp_dir = tempfile.gettempdir()
            pattern = "temp_audio_*.mp3"
            
            import glob
            temp_files = glob.glob(os.path.join(temp_dir, pattern))
            
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        self.log_message(f"Arquivo temporário removido: {os.path.basename(temp_file)}", "INFO")
                except Exception as e:
                    self.log_message(f"Erro ao remover arquivo temporário {temp_file}: {str(e)}", "WARNING")
                    
        except Exception as e:
            self.log_message(f"Erro ao limpar arquivos temporários: {str(e)}", "WARNING")
    
    def optimize_memory_usage(self):
        """Otimiza o uso de memória"""
        try:
            # Forçar garbage collection
            import gc
            gc.collect()
            
            # Limpar cache de widgets se necessário
            if hasattr(self, 'transcription_text'):
                # Limpar tags antigas
                for tag in self.transcription_text.tag_names():
                    if tag not in ['sel', 'error', 'marked']:
                        self.transcription_text.tag_delete(tag)
            
            self.log_message("Otimização de memória executada", "INFO")
            
        except Exception as e:
            self.log_message(f"Erro na otimização de memória: {str(e)}", "WARNING")

    def clear_whisper_result(self):
        """Limpa o resultado do Whisper da memória para economizar RAM"""
        if hasattr(self, 'whisper_result') and self.whisper_result:
            # Extrair apenas os dados essenciais antes de limpar
            if 'words' in self.whisper_result:
                # Manter apenas os timestamps essenciais para os erros
                essential_data = {
                    'words': self.whisper_result['words'],
                    'duration': self.whisper_result.get('duration', 0)
                }
                self.whisper_result = essential_data
            
            # Forçar garbage collection
            import gc
            gc.collect()
            
            self.log_message("Resultado do Whisper otimizado na memória", "INFO")
    
    def get_memory_usage(self):
        """Retorna o uso atual de memória em MB"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0
    
    def log_memory_usage(self, stage=""):
        """Registra o uso atual de memória"""
        try:
            memory_mb = self.get_memory_usage()
            self.log_message(f"Uso de memória {stage}: {memory_mb:.1f} MB", "INFO")
        except Exception as e:
            self.log_message(f"Erro ao verificar memória: {str(e)}", "WARNING")
    
    def manual_cleanup(self):
        """Limpa recursos manualmente"""
        self.log_message("Limpando recursos manualmente...", "INFO")
        self.log_memory_usage("antes da limpeza")
        
        self.clear_console()
        self.cleanup_temp_files()
        self.optimize_memory_usage()
        self.clear_whisper_result()
        
        self.log_memory_usage("após limpeza")
        self.log_message("Recursos limpos com sucesso!", "SUCCESS")

    def start_semantic_analysis(self):
        """Inicia a análise semântica em thread separada"""
        if not self.speech_clips:
            messagebox.showwarning("Aviso", "Nenhum clipe de fala disponível. Execute a transcrição primeiro.")
            return
        
        # Desabilitar botão durante análise
        self.semantic_analyze_button.config(state='disabled')
        self.semantic_status.config(text="Iniciando análise semântica...", foreground='blue')
        
        # Executar em thread separada
        import threading
        analysis_thread = threading.Thread(target=self.run_semantic_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def run_semantic_analysis(self):
        """Executa a análise semântica em thread separada"""
        try:
            self.log_message("Iniciando análise semântica com GPT-4o...", "INFO")
            self.semantic_status.config(text="Enviando para IA...", foreground='blue')
            
            # Obter objetivo do vídeo
            objective = self.get_video_objective()
            
            # Preparar dados para o LLM
            clips_data = self.prepare_clips_for_llm()
            
            # Construir prompt para o LLM
            prompt = self.build_semantic_analysis_prompt(objective, clips_data)
            
            # Chamar API da OpenAI
            self.log_message("Enviando dados para GPT-4o...", "INFO")
            response = self.call_gpt4o_api(prompt)
            
            # Processar resposta
            self.log_message("Processando sugestões da IA...", "INFO")
            self.process_semantic_response(response)
            
            # Atualizar interface
            self.semantic_status.config(text="Sugestões recebidas!", foreground='green')
            self.log_message("Análise semântica concluída com sucesso!", "SUCCESS")
            
            # Habilitar botões de ação
            self.accept_button.config(state='normal')
            self.discard_button.config(state='normal')
            
        except Exception as e:
            import traceback
            err_msg = f"Erro na análise semântica: {str(e)}\n{traceback.format_exc()}"
            self.log_message(err_msg, "ERROR")
            self.semantic_status.config(text="Erro na análise", foreground='red')
        finally:
            self.semantic_analyze_button.config(state='normal')
    
    def get_video_objective(self):
        """Obtém o objetivo do vídeo da interface"""
        # Buscar o widget de texto na interface
        for widget in self.tabs["Reorganização por IA"].winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and "Objetivo" in child.cget("text"):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, tk.Text):
                                return grandchild.get(1.0, tk.END).strip()
        return "Criar um conteúdo claro e impactante"
    
    def prepare_clips_for_llm(self):
        """Prepara os clipes de fala para envio ao LLM"""
        clips_data = []
        for clip in self.speech_clips:
            clips_data.append({
                'id': clip['id'],
                'start': clip['start'],
                'end': clip['end'],
                'text': clip['text'],
                'duration': clip['duration']
            })
        return clips_data
    
    def build_semantic_analysis_prompt(self, objective, clips_data):
        """Constrói o prompt para análise semântica"""
        import json
        
        clips_json = json.dumps(clips_data, ensure_ascii=False, indent=2)
        
        prompt = f"""Você é um editor de vídeo e roteirista especialista. Sua tarefa é analisar os clipes de fala transcritos de um vídeo e propor uma nova estrutura para torná-lo mais eficaz, com base no objetivo do usuário.

Objetivo do usuário: "{objective}"

Aqui estão os clipes de fala em sua ordem original, em formato JSON:
{clips_json}

Suas instruções:
1. Reordene os clipes para criar a melhor narrativa possível que atenda ao objetivo do usuário. Você pode mover clipes de lugar para melhorar o fluxo ou criar mais impacto.
2. Identifique clipes que são redundantes, irrelevantes, ou que atrapalham o ritmo. Recomende a exclusão destes.
3. Sua resposta DEVE ser um único objeto JSON, sem nenhum texto adicional antes ou depois.
4. O JSON deve ter duas chaves: 'new_order' e 'deleted_clips'.
   - 'new_order' deve ser uma lista de objetos, contendo apenas o 'id' dos clipes na nova sequência proposta.
   - 'deleted_clips' deve ser uma lista de objetos, onde cada objeto contém o 'id' do clipe a ser excluído e uma chave 'reason' com uma justificativa curta (em português) para a exclusão.

Exemplo de formato de resposta esperado:
{{
  "new_order": [
    {{"id": 5}},
    {{"id": 1}},
    {{"id": 3}}
  ],
  "deleted_clips": [
    {{"id": 2, "reason": "Redundante, a mesma ideia é explicada melhor no clipe 3."}},
    {{"id": 4, "reason": "Tangencial e não contribui para o objetivo principal do vídeo."}}
  ]
}}

Analise cuidadosamente cada clipe e forneça uma estrutura que maximize o impacto e a clareza do vídeo."""
        
        return prompt
    
    def call_gpt4o_api(self, prompt):
        """Chama a API do GPT-4o"""
        if not OPENAI_AVAILABLE:
            raise RuntimeError("Biblioteca openai não instalada")
        
        if not self.api_key.get():
            raise RuntimeError("API Key da OpenAI não informada")
        
        client = openai.OpenAI(api_key=self.api_key.get())
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em edição de vídeo e narrativa. Responda apenas com JSON válido, sem texto adicional."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    def process_semantic_response(self, response):
        """Processa a resposta do LLM e atualiza a interface"""
        import json
        
        try:
            # Parse da resposta JSON
            suggestions = json.loads(response)
            
            # Validar estrutura da resposta
            if 'new_order' not in suggestions or 'deleted_clips' not in suggestions:
                raise ValueError("Resposta da IA não contém estrutura esperada")
            
            self.semantic_suggestions = suggestions
            
            # Popular lista de sugestões
            self.populate_suggestion_list()
            
            # Popular lista de clipes excluídos
            self.populate_deleted_clips_list()
            
            self.log_message(f"Processadas {len(suggestions['new_order'])} sugestões de reordenação e {len(suggestions['deleted_clips'])} exclusões", "SUCCESS")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Resposta da IA não é JSON válido: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro ao processar resposta da IA: {str(e)}")
    
    def populate_suggestion_list(self):
        """Popula a lista de sugestões da IA"""
        self.suggestion_listbox.delete(0, tk.END)
        
        if not self.semantic_suggestions:
            return
        
        for suggestion in self.semantic_suggestions['new_order']:
            clip_id = suggestion['id']
            clip = next((c for c in self.speech_clips if c['id'] == clip_id), None)
            
            if clip:
                start_time = f"{clip['start']:.1f}s"
                end_time = f"{clip['end']:.1f}s"
                text_preview = clip['text'][:50] + "..." if len(clip['text']) > 50 else clip['text']
                
                display_text = f"[{start_time} - {end_time}] {text_preview}"
                self.suggestion_listbox.insert(tk.END, display_text)
    
    def populate_deleted_clips_list(self):
        """Popula a lista de clipes excluídos"""
        self.deleted_listbox.delete(0, tk.END)
        
        if not self.semantic_suggestions:
            return
        
        for deleted in self.semantic_suggestions['deleted_clips']:
            clip_id = deleted['id']
            reason = deleted['reason']
            clip = next((c for c in self.speech_clips if c['id'] == clip_id), None)
            
            if clip:
                start_time = f"{clip['start']:.1f}s"
                end_time = f"{clip['end']:.1f}s"
                text_preview = clip['text'][:30] + "..." if len(clip['text']) > 30 else clip['text']
                
                display_text = f"[{start_time} - {end_time}] {text_preview} - Motivo: {reason}"
                self.deleted_listbox.insert(tk.END, display_text)

    def accept_semantic_suggestions(self):
        """Aceita as sugestões da IA e prepara para renderização"""
        if not self.semantic_suggestions:
            messagebox.showwarning("Aviso", "Nenhuma sugestão disponível para aceitar.")
            return
        
        # Criar ordem final baseada nas sugestões
        self.final_clip_order = []
        
        for suggestion in self.semantic_suggestions['new_order']:
            clip_id = suggestion['id']
            clip = next((c for c in self.speech_clips if c['id'] == clip_id), None)
            if clip:
                self.final_clip_order.append(clip)
        
        self.semantic_analysis_completed = True
        
        # Atualizar status
        self.semantic_final_status.config(text=f"✅ Sugestões aceitas! {len(self.final_clip_order)} clipes na nova ordem.", foreground='green')
        
        # Desabilitar botões
        self.accept_button.config(state='disabled')
        self.discard_button.config(state='disabled')
        
        self.log_message(f"Sugestões aceitas: {len(self.final_clip_order)} clipes na nova ordem", "SUCCESS")
        
        # Habilitar edição na aba principal
        self.enable_final_editing()
    
    def discard_semantic_suggestions(self):
        """Descarta as sugestões da IA e volta à ordem original"""
        self.semantic_suggestions = None
        self.final_clip_order = []
        self.semantic_analysis_completed = False
        
        # Limpar listas
        self.suggestion_listbox.delete(0, tk.END)
        self.deleted_listbox.delete(0, tk.END)
        
        # Atualizar status
        self.semantic_final_status.config(text="❌ Sugestões descartadas. Mantendo ordem original.", foreground='red')
        
        # Desabilitar botões
        self.accept_button.config(state='disabled')
        self.discard_button.config(state='disabled')
        
        self.log_message("Sugestões descartadas. Mantendo ordem original.", "INFO")
    
    def restore_deleted_clip(self):
        """Restaura um clipe excluído para a lista de sugestões"""
        selection = self.deleted_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um clipe para restaurar.")
            return
        
        if not self.semantic_suggestions:
            return
        
        # Obter clipe selecionado
        deleted_index = selection[0]
        deleted_clip = self.semantic_suggestions['deleted_clips'][deleted_index]
        clip_id = deleted_clip['id']
        
        # Remover da lista de excluídos
        self.semantic_suggestions['deleted_clips'].pop(deleted_index)
        
        # Adicionar ao final da nova ordem
        self.semantic_suggestions['new_order'].append({'id': clip_id})
        
        # Atualizar listas
        self.populate_suggestion_list()
        self.populate_deleted_clips_list()
        
        self.log_message(f"Clipe {clip_id} restaurado", "INFO")
    
    def enable_final_editing(self):
        """Habilita a edição final na aba principal"""
        # Atualizar comando do auto-editor para incluir reorganização
        self.update_command()
        
        # Mostrar mensagem na aba principal
        self.log_message("🎬 Reorganização semântica concluída! Agora você pode executar a edição final.", "SUCCESS")
    
    def build_semantic_reorganization_command(self, base_cmd):
        """Constrói comando para reorganização semântica"""
        # Etapa 1: Exportar clipes individuais
        output_dir = os.path.dirname(self.output_file.get())
        clips_dir = os.path.join(output_dir, "temp_clips")
        
        # Criar diretório temporário
        os.makedirs(clips_dir, exist_ok=True)
        
        # Gerar argumentos --add-in para cada clipe na nova ordem
        add_in_args = []
        for clip in self.final_clip_order:
            add_in_args.append(f"--add-in {clip['start']},{clip['end']}")
        
        # Comando para exportar clipes
        export_cmd = f"{base_cmd} {' '.join(add_in_args)} --export clip-sequence --output {clips_dir}"
        
        return export_cmd
    
    def run_auto_editor(self, command):
        """Executa o auto-editor com suporte à reorganização semântica"""
        try:
            self.log_message(f"Executando comando: {command}", "INFO")
            
            # Verificar se é reorganização semântica
            if "--export clip-sequence" in command:
                self.run_semantic_reorganization(command)
            else:
                # Execução normal
                self.run_normal_editing(command)
                
        except Exception as e:
            self.log_message(f"Erro ao executar auto-editor: {str(e)}", "ERROR")
            self.stop_editing()
    
    def run_semantic_reorganization(self, command):
        """Executa reorganização semântica em duas etapas"""
        try:
            # Etapa 1: Exportar clipes individuais
            self.log_message("Etapa 1: Exportando clipes individuais...", "INFO")
            
            self.process = subprocess.Popen(
                command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitorar saída
            self.monitor_semantic_output()
            
        except Exception as e:
            self.log_message(f"Erro na reorganização semântica: {str(e)}", "ERROR")
            self.stop_editing()
    
    def monitor_semantic_output(self):
        """Monitora a saída da reorganização semântica"""
        def monitor():
            try:
                while self.process and self.process.poll() is None:
                    output = self.process.stdout.readline()
                    if output:
                        self.output_queue.put(output.strip())
                        self.log_message(output.strip(), "INFO")
                
                # Verificar se processo terminou com sucesso
                if self.process and self.process.returncode == 0:
                    self.log_message("Etapa 1 concluída! Iniciando junção dos clipes...", "SUCCESS")
                    self.stitch_clips_sequence()
                else:
                    self.log_message("Erro na exportação dos clipes", "ERROR")
                    self.stop_editing()
                    
            except Exception as e:
                self.log_message(f"Erro no monitoramento: {str(e)}", "ERROR")
                self.stop_editing()
        
        # Executar monitoramento em thread separada
        import threading
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stitch_clips_sequence(self):
        """Junta os clipes exportados em um vídeo final"""
        try:
            output_dir = os.path.dirname(self.output_file.get())
            clips_dir = os.path.join(output_dir, "temp_clips")
            
            # Verificar se os clipes foram exportados
            if not os.path.exists(clips_dir):
                raise RuntimeError("Diretório de clipes não encontrado")
            
            # Listar clipes em ordem
            clip_files = []
            for i in range(len(self.final_clip_order)):
                clip_file = os.path.join(clips_dir, f"{i:04d}.mp4")
                if os.path.exists(clip_file):
                    clip_files.append(clip_file)
                else:
                    self.log_message(f"Aviso: Clipe {i:04d}.mp4 não encontrado", "WARNING")
            
            if not clip_files:
                raise RuntimeError("Nenhum clipe encontrado para juntar")
            
            # Criar arquivo de lista para ffmpeg
            filelist_path = os.path.join(output_dir, "filelist.txt")
            with open(filelist_path, 'w', encoding='utf-8') as f:
                for clip_file in clip_files:
                    f.write(f"file '{clip_file}'\n")
            
            # Comando ffmpeg para juntar clipes
            ffmpeg_cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', filelist_path,
                '-c', 'copy',
                self.output_file.get()
            ]
            
            self.log_message("Etapa 2: Juntando clipes com ffmpeg...", "INFO")
            self.log_message(f"Comando ffmpeg: {' '.join(ffmpeg_cmd)}", "INFO")
            
            # Executar ffmpeg
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message("🎉 Reorganização semântica concluída com sucesso!", "SUCCESS")
                self.cleanup_semantic_temp_files(clips_dir, filelist_path)
            else:
                self.log_message(f"Erro no ffmpeg: {result.stderr}", "ERROR")
            
            self.stop_editing()
            
        except Exception as e:
            self.log_message(f"Erro ao juntar clipes: {str(e)}", "ERROR")
            self.stop_editing()
    
    def cleanup_semantic_temp_files(self, clips_dir, filelist_path):
        """Limpa arquivos temporários da reorganização semântica"""
        try:
            # Remover arquivo de lista
            if os.path.exists(filelist_path):
                os.remove(filelist_path)
                self.log_message("Arquivo de lista removido", "INFO")
            
            # Remover diretório de clipes
            if os.path.exists(clips_dir):
                import shutil
                shutil.rmtree(clips_dir)
                self.log_message("Diretório de clipes temporários removido", "INFO")
                
        except Exception as e:
            self.log_message(f"Erro ao limpar arquivos temporários: {str(e)}", "WARNING")
    
    def run_normal_editing(self, command):
        """Executa edição normal (sem reorganização semântica)"""
        self.process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start()
        
        self.log_message("Iniciando edição...", "INFO")
    
    def check_dependencies(self):
        """Verifica se auto-editor e ffmpeg estão instalados"""
        self.log_message("Verificando dependências...", "INFO")
        
        missing = []
        
        if not shutil.which("auto-editor"):
            missing.append("auto-editor")
            self.log_message("❌ auto-editor não encontrado", "ERROR")
        else:
            self.log_message("✅ auto-editor encontrado", "SUCCESS")
        
        if not shutil.which("ffmpeg"):
            missing.append("ffmpeg")
            self.log_message("❌ ffmpeg não encontrado", "ERROR")
        else:
            self.log_message("✅ ffmpeg encontrado", "SUCCESS")
        
        # Verificar Whisper
        if WHISPER_AVAILABLE:
            self.log_message("✅ whisper encontrado", "SUCCESS")
            self.log_message("🎯 Funcionalidade de correção de fala por IA disponível!", "SUCCESS")
        else:
            self.log_message("⚠️ whisper não encontrado", "WARNING")
            self.log_message("📦 Execute: python3 setup.py para instalar whisper", "WARNING")
        
        if missing:
            self.log_message(f"Dependências ausentes: {', '.join(missing)}", "ERROR")
            self.log_message("Execute: python3 setup.py", "WARNING")
            messagebox.showerror(
                "Dependências Ausentes",
                f"Os seguintes programas não foram encontrados:\n{', '.join(missing)}\n\n"
                "Execute: python3 setup.py"
            )
        else:
            self.log_message("Todas as dependências básicas estão instaladas", "SUCCESS")
    
    def start_editing(self):
        """Inicia o processo de edição"""
        if not self.input_file.get():
            messagebox.showerror("Erro", "Selecione um arquivo de vídeo.")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Erro", "Especifique um arquivo de saída.")
            return
        
        command = self.build_command()
        if not command:
            messagebox.showerror("Erro", "Comando inválido.")
            return
        
        # Limpar console e registrar início
        self.console_text.delete(1.0, tk.END)
        self.log_message("=" * 60, "INFO")
        self.log_message("INICIANDO PROCESSO DE EDIÇÃO", "INFO")
        self.log_message("=" * 60, "INFO")
        self.log_message(f"Arquivo de entrada: {self.input_file.get()}", "INFO")
        self.log_message(f"Arquivo de saída: {self.output_file.get()}", "INFO")
        self.log_message(f"Tipo de corte: {self.cut_type.get()}", "INFO")
        self.log_message(f"Detecção de silêncio: Automática", "INFO")
        
        # Informações sobre cortes de fala por IA
        speech_cuts = self.get_all_cuts_for_auto_editor()
        if speech_cuts:
            self.log_message(f"Cortes de fala por IA: {len(speech_cuts)} intervalos", "INFO")
            for i, (start, end) in enumerate(speech_cuts[:5]):  # Mostrar apenas os primeiros 5
                self.log_message(f"  Corte {i+1}: {start:.1f}s - {end:.1f}s", "INFO")
            if len(speech_cuts) > 5:
                self.log_message(f"  ... e mais {len(speech_cuts) - 5} cortes", "INFO")
        else:
            self.log_message("Cortes de fala por IA: Nenhum", "INFO")
        
        self.log_message(f"Comando: {command}", "INFO")
        self.log_message("-" * 60, "INFO")
        
        # Abrir automaticamente a aba do console
        self.notebook.select(1)  # Seleciona a aba do console (índice 1)
        
        # Atualizar interface
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_running = True
        self.status_label.config(text="Editando...")
        
        # Iniciar barra de progresso
        self.progress_bar.start()
        
        # Executar em thread separada
        thread = threading.Thread(target=self.run_auto_editor, args=(command,))
        thread.daemon = True
        thread.start()
    
    def stop_editing(self):
        """Para o processo de edição"""
        if self.process:
            self.log_message("Interrompendo processo...", "WARNING")
            self.process.terminate()
            self.is_running = False
            self.log_message("Processo interrompido pelo usuário", "WARNING")
    
    def monitor_output(self):
        """Monitora a fila de saída e atualiza o console"""
        try:
            while True:
                line = self.output_queue.get_nowait()
                if line == "DONE":
                    # Processo terminou
                    self.start_button.config(state='normal')
                    self.stop_button.config(state='disabled')
                    self.is_running = False
                    self.progress_bar.stop()
                    self.status_label.config(text="Pronto para editar")
                else:
                    # Adicionar linha ao console
                    self.log_message(line, "INFO")
        except queue.Empty:
            pass
        
        # Agendar próxima verificação
        self.root.after(100, self.monitor_output)
    
    def open_console_tab(self):
        """Abre a aba do console"""
        self.notebook.select(1)  # Seleciona a aba do console
        self.log_message("Aba do console aberta manualmente", "INFO")
    
    def start_speech_analysis(self):
        """Inicia a análise de fala com Whisper"""
        if not self.input_file.get():
            messagebox.showerror("Erro", "Selecione um arquivo de vídeo primeiro.")
            return
        
        if not WHISPER_AVAILABLE:
            messagebox.showerror("Erro", "Whisper não está instalado. Execute: python3 setup.py")
            return
        
        # Atualizar interface
        self.analyze_button.config(state='disabled')
        self.analysis_status.config(text="Iniciando análise...", foreground='blue')
        
        # Executar em thread separada
        thread = threading.Thread(target=self.run_speech_analysis)
        thread.daemon = True
        thread.start()
    
    def run_speech_analysis(self):
        """Executa a análise de fala em thread separada"""
        try:
            self.log_message("Iniciando análise de fala com Whisper...", "INFO")
            self.log_memory_usage("início da análise")
            self.analysis_status.config(text="Extraindo áudio...", foreground='blue')
            audio_file = self.extract_audio()
            if not audio_file:
                return
            self.log_memory_usage("após extração de áudio")
            if self.whisper_mode.get() == "api":
                self.analysis_status.config(text="Transcrevendo via API OpenAI...", foreground='blue')
                self.log_message("Transcrevendo via API OpenAI...", "INFO")
                result = self.transcribe_with_openai_api(audio_file)
                self.log_message(f"Resposta da API OpenAI: {result}", "INFO")
                self.whisper_result = result
                self.log_memory_usage("após receber resposta da API")
            else:
                self.analysis_status.config(text="Carregando modelo Whisper...", foreground='blue')
                self.log_message("Carregando modelo Whisper...", "INFO")
                device = "cuda" if self.use_gpu.get() else "cpu"
                model = whisper.load_model(self.whisper_model.get(), device=device)
                self.log_message(f"Modelo {self.whisper_model.get()} carregado em {device}", "INFO")
                self.log_memory_usage("após carregar modelo")
                self.analysis_status.config(text="Transcrevendo com Whisper local...", foreground='blue')
                self.log_message("Iniciando transcrição...", "INFO")
                result = model.transcribe(audio_file, word_timestamps=True)
                self.whisper_result = result
                del model
                import gc
                gc.collect()
                self.log_memory_usage("após transcrição local")
            # Etapa C: Analisar transcrição
            self.analysis_status.config(text="Analisando texto...", foreground='blue')
            self.log_message("Analisando transcrição para detectar erros...", "INFO")
            self.analyze_transcription_for_errors()
            self.log_memory_usage("após análise de erros")
            # Etapa D: Popular GUI
            self.populate_transcription_gui()
            self.log_memory_usage("após popular GUI")
            self.clear_whisper_result()
            self.log_memory_usage("após otimizar resultado")
            try:
                os.remove(audio_file)
                self.log_message("Arquivo temporário removido", "INFO")
            except Exception as e:
                self.log_message(f"Erro ao remover arquivo temporário: {str(e)}", "WARNING")
            # --- NOVO: Pipeline automático LLM ---
            self.analysis_status.config(text="Enviando para LLM...", foreground='blue')
            self.log_message("Iniciando análise automática por LLM...", "INFO")
            # Chamar LLM e aplicar sugestões automaticamente
            self.run_llm_analysis_auto()
            self.analysis_status.config(text="Correção automática concluída!", foreground='green')
            self.log_message("Correção automática concluída!", "SUCCESS")
            self.log_memory_usage("final da análise")
        except Exception as e:
            import traceback
            err_msg = f"Erro na análise de fala: {str(e)}\n{traceback.format_exc()}"
            self.log_message(err_msg, "ERROR")
            self.analysis_status.config(text="Erro na análise", foreground='red')
            self.last_whisper_error.set(str(e))
        finally:
            self.analyze_button.config(state='normal')

    def run_llm_analysis_auto(self):
        """Executa a análise por LLM e aplica todas as sugestões automaticamente"""
        try:
            # Obter transcrição completa
            full_transcription = self.get_full_transcription()
            prompt = self.build_speech_analysis_prompt(full_transcription)
            provider = self.selected_llm_provider.get()
            model = self.selected_llm_model.get()
            response = self.call_llm_api(provider, model, prompt)
            self.process_llm_suggestions(response)
            # Aplicar todas as sugestões automaticamente
            for suggestion in self.llm_suggestions[:]:
                self.mark_llm_suggestion(suggestion)
            self.llm_suggestions.clear()
            self.populate_suggestions_list()
            self.update_suggestions_count()
            # Desabilitar botões de análise LLM e sugestões
            if hasattr(self, 'llm_analyze_button'):
                self.llm_analyze_button.config(state='disabled')
            if hasattr(self, 'apply_all_suggestions'):
                self.apply_all_suggestions = lambda: None
            if hasattr(self, 'apply_selected_suggestion'):
                self.apply_selected_suggestion = lambda: None
        except Exception as e:
            self.log_message(f"Erro na análise automática por LLM: {e}", "ERROR")
    
    def extract_audio(self):
        """Extrai áudio do vídeo usando ffmpeg"""
        try:
            # Criar arquivo temporário
            temp_dir = tempfile.gettempdir()
            audio_file = os.path.join(temp_dir, f"temp_audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
            
            # Comando ffmpeg para extrair áudio
            cmd = [
                'ffmpeg', '-i', self.input_file.get(),
                '-vn', '-c:a', 'libmp3lame', '-q:a', '2',
                '-y', audio_file
            ]
            
            self.log_message(f"Extraindo áudio: {' '.join(cmd)}", "INFO")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message(f"Áudio extraído: {audio_file}", "INFO")
                return audio_file
            else:
                self.log_message(f"Erro ao extrair áudio: {result.stderr}", "ERROR")
                return None
                
        except Exception as e:
            self.log_message(f"Erro ao extrair áudio: {str(e)}", "ERROR")
            return None
    
    def analyze_transcription_for_errors(self):
        """Analisa a transcrição para detectar erros - OTIMIZADO PARA MEMÓRIA"""
        self.error_segments = []
        if not self.whisper_result:
            return
        
        # Verificar se temos words (nova API) ou segments (API antiga)
        words = self.whisper_result.get('words')
        if not words:
            self.log_message("A resposta da API não contém 'words' com timestamps. Verifique se sua conta OpenAI tem acesso a timestamps por palavra.", "ERROR")
            self.analysis_status.config(text="API não retornou timestamps. Verifique seu plano OpenAI.", foreground='red')
            self.last_whisper_error.set("API não retornou timestamps. Verifique seu plano OpenAI.")
            return
        
        self.log_message(f"Analisando {len(words)} palavras para detectar erros...", "INFO")
        
        # Palavras de preenchimento padrão
        default_fillers = {'uh', 'um', 'ah', 'hmm', 'er', 'um', 'uhm'}
        
        # Adicionar palavras personalizadas
        custom_fillers = set(word.strip().lower() for word in self.custom_fillers.get().split(','))
        all_fillers = default_fillers.union(custom_fillers)
        
        # Processar em lotes menores para economizar memória
        batch_size = 200
        errors_found = 0
        
        for i in range(0, len(words), batch_size):
            batch = words[i:i + batch_size]
            
            # Analisar cada palavra no lote
            for j, word_info in enumerate(batch):
                word = word_info['word'].strip().lower()
                start_time = word_info['start']
                end_time = word_info['end']
                
                # Detectar palavras de preenchimento
                if self.detect_fillers.get():
                    if word in all_fillers:
                        self.error_segments.append({
                            'type': 'filler',
                            'text': word_info['word'],  # Usar palavra original
                            'start': start_time,
                            'end': end_time,
                            'segment_text': word_info['word']
                        })
                        errors_found += 1
                
                # Detectar repetições (palavras consecutivas iguais)
                if self.detect_repetitions.get():
                    # Verificar se não é a última palavra do lote
                    if j < len(batch) - 1:
                        next_word = batch[j + 1]['word'].strip().lower()
                        if word == next_word and len(word) > 2:
                            # Marcar ambas as palavras como repetição
                            self.error_segments.append({
                                'type': 'repetition',
                                'text': f"{word_info['word']} {batch[j + 1]['word']}",
                                'start': start_time,
                                'end': batch[j + 1]['end'],
                                'segment_text': f"{word_info['word']} {batch[j + 1]['word']}"
                            })
                            errors_found += 1
                    # Verificar se não é a última palavra geral
                    elif i + j < len(words) - 1:
                        next_word = words[i + j + 1]['word'].strip().lower()
                        if word == next_word and len(word) > 2:
                            self.error_segments.append({
                                'type': 'repetition',
                                'text': f"{word_info['word']} {words[i + j + 1]['word']}",
                                'start': start_time,
                                'end': words[i + j + 1]['end'],
                                'segment_text': f"{word_info['word']} {words[i + j + 1]['word']}"
                            })
                            errors_found += 1
            
            # Forçar garbage collection a cada lote
            if i % (batch_size * 3) == 0:
                import gc
                gc.collect()
                self.log_message(f"Analisadas {i + len(batch)} palavras, {errors_found} erros encontrados...", "INFO")
        
        self.log_message(f"Análise concluída: {errors_found} erros detectados", "SUCCESS")
    
    def populate_transcription_gui(self):
        """Popula a GUI com a transcrição e marca os erros - OTIMIZADO PARA MEMÓRIA"""
        if not self.whisper_result:
            return
        
        # Limpar área de transcrição
        self.transcription_text.delete(1.0, tk.END)
        
        # Verificar se temos words (nova API) ou segments (API antiga)
        words = self.whisper_result.get('words')
        if not words:
            self.log_message("A resposta da API não contém 'words' com timestamps.", "ERROR")
            return
        
        self.log_message(f"Processando {len(words)} palavras...", "INFO")
        
        # Processar e inserir diretamente, sem construir string gigante
        sentence_words = []
        sentence_start = None
        sentences_processed = 0
        
        # Processar em lotes muito menores para economizar memória
        batch_size = 100  # Reduzido de 1000 para 100
        for i in range(0, len(words), batch_size):
            batch = words[i:i + batch_size]
            
            for word_info in batch:
                word = word_info['word']
                
                # Iniciar nova frase se não temos uma
                if sentence_start is None:
                    sentence_start = word_info['start']
                
                sentence_words.append(word)
                
                # Finalizar frase se encontrou pontuação de fim
                if word.strip() in ['.', '!', '?']:
                    # Construir e inserir frase imediatamente
                    sentence_text = ''.join(sentence_words).strip()
                    sentence_end = word_info['end']
                    
                    timestamp = f"[{sentence_start:.1f}s - {sentence_end:.1f}s] "
                    line_text = timestamp + sentence_text + "\n\n"
                    
                    # Inserir diretamente no widget
                    self.transcription_text.insert(tk.END, line_text)
                    
                    # Limpar lista de palavras da frase imediatamente
                    sentence_words.clear()
                    sentence_start = None
                    sentences_processed += 1
                    
                    # Atualizar GUI a cada 10 frases
                    if sentences_processed % 10 == 0:
                        self.transcription_text.see(tk.END)
                        self.transcription_text.update_idletasks()
                        self.log_message(f"Processadas {sentences_processed} frases...", "INFO")
            
            # Forçar garbage collection a cada lote
            if i % (batch_size * 5) == 0:
                import gc
                gc.collect()
        
        # Adicionar última frase se não terminou com pontuação
        if sentence_words:
            sentence_text = ''.join(sentence_words).strip()
            sentence_end = words[-1]['end']
            
            timestamp = f"[{sentence_start:.1f}s - {sentence_end:.1f}s] "
            line_text = timestamp + sentence_text + "\n\n"
            
            self.transcription_text.insert(tk.END, line_text)
            sentences_processed += 1
        
        # Limpar variáveis para liberar memória
        del sentence_words, sentence_start
        import gc
        gc.collect()
        
        self.log_message(f"Transcrição concluída: {sentences_processed} frases processadas", "SUCCESS")
        
        # Extrair clipes de fala para reorganização semântica
        self.extract_speech_clips()
        
        # Marcar erros detectados automaticamente
        self.mark_detected_errors()
        
        # Atualizar contador
        self.update_cuts_count()
    
    def extract_speech_clips(self):
        """Extrai clipes de fala da transcrição para reorganização semântica"""
        if not self.whisper_result or not self.whisper_result.get('words'):
            return
        
        self.log_message("Extraindo clipes de fala para análise semântica...", "INFO")
        
        words = self.whisper_result['words']
        self.speech_clips = []
        clip_id = 1
        
        # Agrupar palavras em clipes baseados em pausas e pontuação
        current_clip_words = []
        current_start = None
        
        for word_info in words:
            word = word_info['word']
            
            # Iniciar novo clipe se não temos um
            if current_start is None:
                current_start = word_info['start']
            
            current_clip_words.append(word)
            
            # Finalizar clipe se encontrou pontuação de fim ou pausa longa
            if word.strip() in ['.', '!', '?']:
                # Verificar se há pausa significativa após pontuação
                if len(words) > words.index(word_info) + 1:
                    next_word = words[words.index(word_info) + 1]
                    pause_duration = next_word['start'] - word_info['end']
                    
                    # Se pausa > 1 segundo, finalizar clipe
                    if pause_duration > 1.0:
                        clip_text = ''.join(current_clip_words).strip()
                        clip_end = word_info['end']
                        
                        self.speech_clips.append({
                            'id': clip_id,
                            'start': current_start,
                            'end': clip_end,
                            'text': clip_text,
                            'duration': clip_end - current_start
                        })
                        
                        clip_id += 1
                        current_clip_words = []
                        current_start = None
        
        # Adicionar último clipe se não terminou com pontuação
        if current_clip_words:
            clip_text = ''.join(current_clip_words).strip()
            clip_end = words[-1]['end']
            
            self.speech_clips.append({
                'id': clip_id,
                'start': current_start,
                'end': clip_end,
                'text': clip_text,
                'duration': clip_end - current_start
            })
        
        self.log_message(f"Extraídos {len(self.speech_clips)} clipes de fala", "SUCCESS")
        
        # Habilitar botão de análise semântica
        self.semantic_analyze_button.config(state='normal')
        self.semantic_status.config(text="Pronto para análise semântica", foreground='green')
        
        # Popular lista de ordem original
        self.populate_original_clips_list()
    
    def populate_original_clips_list(self):
        """Popula a lista de clipes na ordem original"""
        self.original_listbox.delete(0, tk.END)
        
        for clip in self.speech_clips:
            # Formatar texto para exibição
            start_time = f"{clip['start']:.1f}s"
            end_time = f"{clip['end']:.1f}s"
            text_preview = clip['text'][:50] + "..." if len(clip['text']) > 50 else clip['text']
            
            display_text = f"[{start_time} - {end_time}] {text_preview}"
            self.original_listbox.insert(tk.END, display_text)
    
    def mark_detected_errors(self):
        """Marca os erros detectados automaticamente no texto"""
        for error in self.error_segments:
            # Encontrar o texto do erro na transcrição
            text_to_find = error['text']
            start_pos = self.transcription_text.search(text_to_find, 1.0, tk.END)
            
            if start_pos:
                end_pos = f"{start_pos}+{len(text_to_find)}c"
                self.transcription_text.tag_add("error", start_pos, end_pos)
    
    def mark_selection_for_removal(self):
        """Marca a seleção atual para remoção"""
        try:
            selection = self.transcription_text.tag_ranges(tk.SEL)
            if selection:
                start, end = selection
                
                # Obter o texto selecionado
                selected_text = self.transcription_text.get(start, end)
                
                # Encontrar timestamps para a seleção
                timestamps = self.find_timestamps_for_selection(start, end)
                
                if timestamps:
                    segment = {
                        'type': 'manual',
                        'text': selected_text,
                        'start': timestamps['start'],
                        'end': timestamps['end'],
                        'segment_text': selected_text
                    }
                    
                    self.marked_segments.append(segment)
                    self.transcription_text.tag_add("marked", start, end)
                    
                    self.log_message(f"Marcado para remoção: {selected_text[:50]}... ({timestamps['start']:.1f}s - {timestamps['end']:.1f}s)", "INFO")
                    self.update_cuts_count()
                else:
                    messagebox.showwarning("Aviso", "Não foi possível determinar os timestamps para a seleção.")
            else:
                messagebox.showwarning("Aviso", "Selecione um texto primeiro.")
        except Exception as e:
            self.log_message(f"Erro ao marcar seleção: {str(e)}", "ERROR")
    
    def unmark_selection(self):
        """Remove a marcação da seleção atual"""
        try:
            selection = self.transcription_text.tag_ranges(tk.SEL)
            if selection:
                start, end = selection
                selected_text = self.transcription_text.get(start, end)
                
                # Remover da lista de segmentos marcados
                self.marked_segments = [s for s in self.marked_segments if s['text'] != selected_text]
                
                # Remover tag
                self.transcription_text.tag_remove("marked", start, end)
                
                self.log_message(f"Desmarcado: {selected_text[:50]}...", "INFO")
                self.update_cuts_count()
            else:
                messagebox.showwarning("Aviso", "Selecione um texto marcado primeiro.")
        except Exception as e:
            self.log_message(f"Erro ao desmarcar seleção: {str(e)}", "ERROR")
    
    def find_timestamps_for_selection(self, start, end):
        """Encontra os timestamps para uma seleção de texto"""
        try:
            # Obter a linha onde está a seleção
            start_line = self.transcription_text.index(start).split('.')[0]
            end_line = self.transcription_text.index(end).split('.')[0]
            
            # Procurar por timestamps nas linhas
            for line_num in range(int(start_line), int(end_line) + 1):
                line_start = f"{line_num}.0"
                line_end = f"{line_num}.end"
                line_text = self.transcription_text.get(line_start, line_end)
                
                # Extrair timestamp da linha
                if '[' in line_text and ']' in line_text:
                    timestamp_part = line_text[line_text.find('['):line_text.find(']')+1]
                    times = timestamp_part.strip('[]').split(' - ')
                    if len(times) == 2:
                        return {
                            'start': float(times[0].replace('s', '')),
                            'end': float(times[1].replace('s', ''))
                        }
            
            return None
        except Exception as e:
            self.log_message(f"Erro ao encontrar timestamps: {str(e)}", "ERROR")
            return None
    
    def update_cuts_count(self):
        """Atualiza o contador de cortes"""
        total_cuts = len(self.error_segments) + len(self.marked_segments)
        self.cuts_count_label.config(text=f"Cortes marcados: {total_cuts}")
    
    def get_all_cuts_for_auto_editor(self):
        """Retorna todos os cortes para o auto-editor"""
        all_cuts = []
        
        # Adicionar erros detectados automaticamente
        for error in self.error_segments:
            all_cuts.append((error['start'], error['end']))
        
        # Adicionar segmentos marcados manualmente
        for segment in self.marked_segments:
            all_cuts.append((segment['start'], segment['end']))
        
        # Ordenar e mesclar intervalos sobrepostos
        all_cuts.sort(key=lambda x: x[0])
        
        merged_cuts = []
        for cut in all_cuts:
            if not merged_cuts or cut[0] > merged_cuts[-1][1]:
                merged_cuts.append(cut)
            else:
                # Mesclar intervalos sobrepostos
                merged_cuts[-1] = (merged_cuts[-1][0], max(merged_cuts[-1][1], cut[1]))
        
        return merged_cuts

    def start_llm_analysis(self):
        """Inicia a análise de erros por LLM"""
        if not self.whisper_result:
            messagebox.showwarning("Aviso", "Execute a transcrição com Whisper primeiro.")
            return
        
        # Verificar se há LLM configurado
        provider = self.selected_llm_provider.get()
        if not self.api_keys.get(provider):
            messagebox.showerror("Erro", f"API Key do {provider.upper()} não configurada.")
            return
        
        # Desabilitar botão durante análise
        self.llm_analyze_button.config(state='disabled')
        self.llm_analysis_status.config(text="Iniciando análise por LLM...", foreground='blue')
        
        # Executar em thread separada
        import threading
        analysis_thread = threading.Thread(target=self.run_llm_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def run_llm_analysis(self):
        """Executa a análise por LLM em thread separada"""
        try:
            self.log_message("Iniciando análise de erros por LLM...", "INFO")
            self.llm_analysis_status.config(text="Analisando transcrição...", foreground='blue')
            
            # Obter transcrição completa
            full_transcription = self.get_full_transcription()
            
            # Construir prompt para análise
            prompt = self.build_speech_analysis_prompt(full_transcription)
            
            # Chamar LLM
            provider = self.selected_llm_provider.get()
            model = self.selected_llm_model.get()
            
            self.log_message(f"Enviando para {provider} ({model})...", "INFO")
            response = self.call_llm_api(provider, model, prompt)
            
            # Processar resposta
            self.log_message("Processando sugestões do LLM...", "INFO")
            self.process_llm_suggestions(response)
            
            # Atualizar interface
            self.llm_analysis_status.config(text="Análise concluída! Revise as sugestões.", foreground='green')
            self.log_message("Análise por LLM concluída com sucesso!", "SUCCESS")
            
        except Exception as e:
            import traceback
            err_msg = f"Erro na análise por LLM: {str(e)}\n{traceback.format_exc()}"
            self.log_message(err_msg, "ERROR")
            self.llm_analysis_status.config(text="Erro na análise", foreground='red')
        finally:
            self.llm_analyze_button.config(state='normal')
    
    def get_full_transcription(self):
        """Obtém a transcrição completa do texto"""
        return self.transcription_text.get(1.0, tk.END).strip()
    
    def build_speech_analysis_prompt(self, transcription):
        """Constrói o prompt para análise de fala"""
        prompt = f"""Você é um especialista em edição de vídeo e análise de fala. Sua tarefa é analisar a transcrição de um vídeo e identificar erros que devem ser corrigidos.

Transcrição do vídeo:
{transcription}

Identifique os seguintes tipos de erros:
1. **Palavras de preenchimento**: "um", "ah", "tipo", "né", "sabe", "então", etc.
2. **Repetições desnecessárias**: palavras ou frases repetidas
3. **Gaguejos e hesitações**: frases incompletas ou confusas
4. **Pausas longas**: silêncios desnecessários
5. **Erros gramaticais**: que afetam a clareza
6. **Conteúdo irrelevante**: que não contribui para o objetivo do vídeo

Para cada erro encontrado, forneça:
- **Tipo**: categoria do erro
- **Texto**: trecho exato da transcrição
- **Motivo**: justificativa para a correção
- **Sugestão**: como corrigir (opcional)

Sua resposta DEVE ser um JSON válido com a seguinte estrutura:
{{
  "suggestions": [
    {{
      "type": "filler_word",
      "text": "um, então",
      "start_time": "15.2",
      "end_time": "15.8",
      "reason": "Palavra de preenchimento desnecessária",
      "suggestion": "Remover completamente"
    }},
    {{
      "type": "repetition",
      "text": "vamos falar sobre vamos falar sobre",
      "start_time": "30.1",
      "end_time": "31.5",
      "reason": "Repetição desnecessária da mesma frase",
      "suggestion": "Manter apenas uma ocorrência"
    }}
  ]
}}

Analise cuidadosamente e forneça apenas sugestões relevantes que realmente melhorarão a qualidade do vídeo."""
        
        return prompt
    
    def call_llm_api(self, provider, model, prompt):
        """Chama a API do LLM selecionado"""
        if provider == "openai":
            return self.call_openai_api(model, prompt)
        elif provider == "gemini":
            return self.call_gemini_api(model, prompt)
        else:
            raise ValueError(f"Provedor não suportado: {provider}")
    
    def call_openai_api(self, model, prompt):
        """Chama a API da OpenAI"""
        if not OPENAI_AVAILABLE:
            raise RuntimeError("Biblioteca openai não instalada")
        
        api_key = self.api_keys.get("openai")
        if not api_key:
            raise RuntimeError("API Key da OpenAI não configurada")
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em edição de vídeo e análise de fala. Responda apenas com JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    def call_gemini_api(self, model, prompt):
        """Chama a API do Google Gemini"""
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Biblioteca google.generativeai não instalada")
        
        api_key = self.api_keys.get("gemini")
        if not api_key:
            raise RuntimeError("API Key do Google Gemini não configurada")
        
        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(model)
        
        response = model_instance.generate_content(prompt)
        return response.text
    
    def process_llm_suggestions(self, response):
        """Processa as sugestões do LLM"""
        import json
        
        try:
            # Parse da resposta JSON
            data = json.loads(response)
            
            if 'suggestions' not in data:
                raise ValueError("Resposta do LLM não contém 'suggestions'")
            
            self.llm_suggestions = data['suggestions']
            
            # Popular lista de sugestões
            self.populate_suggestions_list()
            
            # Atualizar contador
            self.update_suggestions_count()
            
            self.log_message(f"Processadas {len(self.llm_suggestions)} sugestões do LLM", "SUCCESS")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Resposta do LLM não é JSON válido: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro ao processar sugestões do LLM: {str(e)}")
    
    def populate_suggestions_list(self):
        """Popula a lista de sugestões do LLM"""
        self.suggestions_listbox.delete(0, tk.END)
        
        for i, suggestion in enumerate(self.llm_suggestions, 1):
            display_text = f"{i}. [{suggestion['type']}] {suggestion['text'][:50]}..."
            self.suggestions_listbox.insert(tk.END, display_text)
    
    def apply_selected_suggestion(self):
        """Aplica a sugestão selecionada"""
        selection = self.suggestions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma sugestão para aplicar.")
            return
        
        index = selection[0]
        suggestion = self.llm_suggestions[index]
        
        # Marcar o texto na transcrição
        self.mark_llm_suggestion(suggestion)
        
        # Mover para lista de aplicadas
        self.llm_suggestions.pop(index)
        self.populate_suggestions_list()
        self.update_suggestions_count()
        
        self.log_message(f"Sugestão aplicada: {suggestion['text'][:30]}...", "SUCCESS")
    
    def apply_all_suggestions(self):
        """Aplica todas as sugestões do LLM"""
        if not self.llm_suggestions:
            messagebox.showwarning("Aviso", "Nenhuma sugestão disponível.")
            return
        
        count = len(self.llm_suggestions)
        for suggestion in self.llm_suggestions[:]:  # Cópia da lista
            self.mark_llm_suggestion(suggestion)
        
        self.llm_suggestions.clear()
        self.populate_suggestions_list()
        self.update_suggestions_count()
        
        self.log_message(f"Todas as {count} sugestões aplicadas!", "SUCCESS")
    
    def reject_selected_suggestion(self):
        """Rejeita a sugestão selecionada"""
        selection = self.suggestions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma sugestão para rejeitar.")
            return
        
        index = selection[0]
        suggestion = self.llm_suggestions.pop(index)
        self.populate_suggestions_list()
        self.update_suggestions_count()
        
        self.log_message(f"Sugestão rejeitada: {suggestion['text'][:30]}...", "INFO")
    
    def reject_all_suggestions(self):
        """Rejeita todas as sugestões do LLM"""
        if not self.llm_suggestions:
            messagebox.showwarning("Aviso", "Nenhuma sugestão disponível.")
            return
        
        count = len(self.llm_suggestions)
        self.llm_suggestions.clear()
        self.populate_suggestions_list()
        self.update_suggestions_count()
        
        self.log_message(f"Todas as {count} sugestões rejeitadas!", "INFO")
    
    def mark_llm_suggestion(self, suggestion):
        """Marca uma sugestão do LLM na transcrição"""
        text_to_find = suggestion['text']
        start_pos = self.transcription_text.search(text_to_find, 1.0, tk.END)
        
        if start_pos:
            end_pos = f"{start_pos}+{len(text_to_find)}c"
            self.transcription_text.tag_add("llm_suggestion", start_pos, end_pos)
            
            # Adicionar à lista de segmentos marcados
            segment = {
                'type': 'llm_suggestion',
                'text': text_to_find,
                'start': float(suggestion.get('start_time', 0)),
                'end': float(suggestion.get('end_time', 0)),
                'reason': suggestion.get('reason', 'Sugestão do LLM')
            }
            self.marked_segments.append(segment)
            self.update_cuts_count()
    
    def clear_all_marks(self):
        """Limpa todas as marcações"""
        self.transcription_text.tag_remove("error", 1.0, tk.END)
        self.transcription_text.tag_remove("marked", 1.0, tk.END)
        self.transcription_text.tag_remove("llm_suggestion", 1.0, tk.END)
        
        self.error_segments.clear()
        self.marked_segments.clear()
        self.llm_suggestions.clear()
        
        self.populate_suggestions_list()
        self.update_cuts_count()
        self.update_suggestions_count()
        
        self.log_message("Todas as marcações removidas", "INFO")
    
    def update_suggestions_count(self):
        """Atualiza os contadores de sugestões"""
        total_suggestions = len(self.llm_suggestions)
        applied_suggestions = len([s for s in self.marked_segments if s['type'] == 'llm_suggestion'])
        
        self.llm_suggestions_count.config(text=f"Sugestões do LLM: {total_suggestions}")
        self.applied_suggestions_count.config(text=f"Sugestões aplicadas: {applied_suggestions}")

    def load_saved_config(self):
        """Carrega configurações salvas"""
        # Carregar API keys
        self.api_keys["openai"] = self.openai_key_entry.get()
        self.api_keys["gemini"] = self.gemini_key_entry.get()
        
        # Configurar provedor e modelo salvos
        saved_provider = self.api_keys.get("last_provider", "openai")
        saved_model = self.api_keys.get("last_model", "gpt-4o")
        
        self.selected_llm_provider.set(saved_provider)
        self.selected_llm_model.set(saved_model)
        
        # Atualizar lista de modelos
        self.update_model_list(saved_provider)
    
    def save_api_keys(self):
        """Salva as chaves de API"""
        # Atualizar dicionário de chaves
        self.api_keys["openai"] = self.openai_key_entry.get()
        self.api_keys["gemini"] = self.gemini_key_entry.get()
        self.api_keys["last_provider"] = self.selected_llm_provider.get()
        self.api_keys["last_model"] = self.selected_llm_model.get()
        
        # Salvar no arquivo
        config_file = "api_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.api_keys, f, indent=2, ensure_ascii=False)
            self.log_message("Configurações de API salvas com sucesso!", "SUCCESS")
        except Exception as e:
            self.log_message(f"Erro ao salvar configurações: {e}", "ERROR")
    
    def test_api_connection(self, provider):
        """Testa a conexão com a API selecionada"""
        try:
            # Atualizar chave no dicionário
            if provider == "openai":
                self.api_keys["openai"] = self.openai_key_entry.get()
            else:
                self.api_keys["gemini"] = self.gemini_key_entry.get()
            
            if provider == "openai":
                if not self.api_keys.get("openai"):
                    messagebox.showerror("Erro", "API Key da OpenAI não configurada")
                    return False
                
                client = openai.OpenAI(api_key=self.api_keys["openai"])
                response = client.models.list()
                self.available_models["openai"] = [model.id for model in response.data if "gpt" in model.id]
                self.log_message(f"OpenAI conectada! Modelos disponíveis: {len(self.available_models['openai'])}", "SUCCESS")
                self.connection_status.config(text="Status: OpenAI conectado", foreground='green')
                return True
                
            elif provider == "gemini":
                if not self.api_keys.get("gemini"):
                    messagebox.showerror("Erro", "API Key do Google Gemini não configurada")
                    return False
                
                genai.configure(api_key=self.api_keys["gemini"])
                models = genai.list_models()
                self.available_models["gemini"] = [model.name for model in models if "gemini" in model.name]
                self.log_message(f"Google Gemini conectado! Modelos disponíveis: {len(self.available_models['gemini'])}", "SUCCESS")
                self.connection_status.config(text="Status: Gemini conectado", foreground='green')
                return True
                
        except Exception as e:
            self.log_message(f"Erro ao conectar com {provider}: {str(e)}", "ERROR")
            self.connection_status.config(text=f"Status: Erro ao conectar com {provider}", foreground='red')
            return False
    
    def update_model_list(self, provider):
        """Atualiza a lista de modelos disponíveis"""
        if provider in self.available_models:
            models = self.available_models[provider]
            self.model_combobox['values'] = models
            
            # Selecionar modelo padrão
            if provider == "openai":
                default_model = "gpt-4o" if "gpt-4o" in models else models[0] if models else ""
            else:  # gemini
                default_model = "models/gemini-1.5-pro" if "models/gemini-1.5-pro" in models else models[0] if models else ""
            
            self.selected_llm_model.set(default_model)
        else:
            self.model_combobox['values'] = []
            self.selected_llm_model.set("")
    
    def choose_input_file(self):
        """Abre diálogo para selecionar arquivo de entrada"""
        filetypes = [
            ("Vídeos", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("Áudios", "*.mp3 *.wav *.m4a *.aac *.ogg *.flac"),
            ("Todos os arquivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo de vídeo/áudio",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file.set(filename)
            # Sugerir nome de saída
            base_name = os.path.splitext(filename)[0]
            self.output_file.set(f"{base_name}_edited.mp4")
            self.update_command()
    
    def choose_output_file(self):
        """Abre diálogo para selecionar arquivo de saída"""
        filetypes = [
            ("Vídeo MP4", "*.mp4"),
            ("Vídeo AVI", "*.avi"),
            ("Vídeo MOV", "*.mov"),
            ("Todos os arquivos", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="Salvar arquivo editado como",
            filetypes=filetypes,
            defaultextension=".mp4"
        )
        
        if filename:
            self.output_file.set(filename)
            self.update_command()
    
    def log_message(self, message, level="INFO"):
        """Adiciona mensagem ao console com timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Cores por nível
        colors = {
            "INFO": "black",
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red"
        }
        
        color = colors.get(level, "black")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Adicionar ao console
        self.console_text.insert(tk.END, formatted_message)
        self.console_text.see(tk.END)
        
        # Configurar cor
        start_pos = f"{self.console_text.index(tk.END).split('.')[0]}.0"
        end_pos = self.console_text.index(tk.END)
        self.console_text.tag_add(level, start_pos, end_pos)
        self.console_text.tag_config(level, foreground=color)
        
        # Forçar atualização
        self.console_text.update_idletasks()
    
    def log_memory_usage(self, stage=""):
        """Registra uso de memória"""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.log_message(f"Uso de memória {stage}: {memory_mb:.1f} MB", "INFO")
        except Exception as e:
            self.log_message(f"Erro ao registrar memória: {e}", "WARNING")
    
    def clear_whisper_result(self):
        """Limpa o resultado do Whisper da memória"""
        if self.whisper_result:
            # Manter apenas informações essenciais
            essential_data = {
                'words': self.whisper_result.get('words', []),
                'text': self.whisper_result.get('text', '')
            }
            self.whisper_result = essential_data
            
            # Forçar garbage collection
            import gc
            gc.collect()
            
            self.log_message("Resultado do Whisper otimizado na memória", "INFO")
    
    def load_api_keys(self):
        """Carrega as chaves de API salvas"""
        config_file = "api_config.json"
        default_config = {
            "openai": "",
            "gemini": "",
            "last_provider": "openai",
            "last_model": "gpt-4o"
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Garantir que todas as chaves existam
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    return config
            else:
                return default_config
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return default_config

    def start_simple_edit(self):
        """Executa o pipeline do modo Edição Simples"""
        import threading
        def worker():
            try:
                self.config_status_label.config(text="Analisando clipes de fala...", foreground='blue')
                self.log_message("Executando auto-editor para análise de silêncio...", "INFO")
                video = self.input_file.get()
                output = self.output_file.get()
                cut_style = self.simple_cut_style.get()
                # Mapear cut_style para parâmetros
                margin = round(0.1 + (cut_style-1)*0.1, 2)  # 0.1 a 0.5
                threshold = round(0.04 + (cut_style-1)*0.01, 2)  # 0.04 a 0.08
                # 1. Análise dos clipes
                json_path = tempfile.mktemp(suffix="_ae.json")
                cmd = ["auto-editor", video, "-m", str(margin), "--edit", "audio", "--silent-threshold", str(threshold), "--export", "json", "-o", json_path]
                self.log_message(f"Comando: {' '.join(map(str,cmd))}", "INFO")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.config_status_label.config(text="Erro ao analisar clipes de fala.", foreground='red')
                    self.log_message(result.stderr, "ERROR")
                    return
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                playlist = []
                for clip in data.get('chunks', []):
                    playlist.append({'start': clip['start'], 'end': clip['end']})
                self.log_message(f"Playlist com {len(playlist)} clipes gerada.", "SUCCESS")
                # 2. Renderização
                if self.simple_jcut_enabled.get():
                    self.config_status_label.config(text="Renderizando com J-Cut...", foreground='blue')
                    self.engine_jcut(playlist, self.simple_jcut_duration.get(), video, output)
                else:
                    self.config_status_label.config(text="Renderizando vídeo final...", foreground='blue')
                    # Montar comando auto-editor para renderização direta
                    addins = []
                    for clip in playlist:
                        addins.extend(["--add-in", f"{clip['start']}-{clip['end']}"])
                    cmd2 = ["auto-editor", video, "--edit", "all/e"] + addins + ["-o", output]
                    self.log_message(f"Comando: {' '.join(map(str,cmd2))}", "INFO")
                    result2 = subprocess.run(cmd2, capture_output=True, text=True)
                    if result2.returncode != 0:
                        self.config_status_label.config(text="Erro na renderização.", foreground='red')
                        self.log_message(result2.stderr, "ERROR")
                        return
                self.config_status_label.config(text="Edição Simples concluída!", foreground='green')
                self.log_message("Edição Simples finalizada com sucesso!", "SUCCESS")
            except Exception as e:
                self.config_status_label.config(text=f"Erro: {e}", foreground='red')
                self.log_message(str(e), "ERROR")
        threading.Thread(target=worker, daemon=True).start()

    def engine_jcut(self, playlist, jcut_duration, input_video, output_video):
        """Engine modular de J-Cut: sobrepõe áudio entre clipes usando ffmpeg avançado"""
        import tempfile, shutil
        import os
        import subprocess
        temp_dir = tempfile.mkdtemp(prefix="jcut_")
        temp_clips = []
        try:
            self.log_message(f"Iniciando engine J-Cut com {len(playlist)} clipes...", "INFO")
            jd = float(jcut_duration)
            # 4.1. Loop principal de geração de clipes com transição
            for i in range(len(playlist)-1):
                start_i = playlist[i]['start']
                end_i = playlist[i]['end']
                start_next = playlist[i+1]['start']
                # Calcula limites para trims
                end_i_menos_jd = max(start_i, end_i - jd)
                start_next_mais_jd = start_next + jd
                out_path = os.path.join(temp_dir, f"temp_clip_{i:03d}.mp4")
                filter_complex = (
                    f"[0:v]trim=start={start_i}:end={end_i},setpts=PTS-STARTPTS[v_out]; "
                    f"[0:a]atrim=start={start_i}:end={end_i_menos_jd},asetpts=PTS-STARTPTS[a_part1]; "
                    f"[0:a]atrim=start={start_next}:end={start_next_mais_jd},asetpts=PTS-STARTPTS[a_part2]; "
                    f"[a_part1][a_part2]concat=n=2:v=0:a=1[a_out]"
                )
                cmd = [
                    "ffmpeg", "-y", "-i", input_video,
                    "-filter_complex", filter_complex,
                    "-map", "[v_out]", "-map", "[a_out]",
                    "-c:v", "libx264", "-c:a", "aac", out_path
                ]
                self.log_message(f"J-Cut ffmpeg: {' '.join(map(str,cmd))}", "INFO")
                subprocess.run(cmd, capture_output=True)
                temp_clips.append(out_path)
            # 4.2. Último clipe (sem transição)
            last = playlist[-1]
            last_path = os.path.join(temp_dir, f"temp_clip_{len(playlist)-1:03d}.mp4")
            cmd_last = [
                "ffmpeg", "-y", "-i", input_video,
                "-ss", str(last['start']), "-to", str(last['end']),
                "-c:v", "libx264", "-c:a", "aac", last_path
            ]
            self.log_message(f"Último clipe ffmpeg: {' '.join(map(str,cmd_last))}", "INFO")
            subprocess.run(cmd_last, capture_output=True)
            temp_clips.append(last_path)
            # 4.3. Consolidação
            concat_list = os.path.join(temp_dir, "filelist.txt")
            with open(concat_list, 'w') as f:
                for c in temp_clips:
                    f.write(f"file '{c}'\n")
            cmd_concat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", output_video]
            self.log_message(f"Concat ffmpeg: {' '.join(map(str,cmd_concat))}", "INFO")
            subprocess.run(cmd_concat, capture_output=True)
            self.config_status_label.config(text="J-Cut concluído!", foreground='green')
            self.log_message("J-Cut finalizado com sucesso!", "SUCCESS")
        except Exception as e:
            self.config_status_label.config(text=f"Erro no J-Cut: {e}", foreground='red')
            self.log_message(str(e), "ERROR")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def start_auto_magic_edit(self):
        """Executa o pipeline do modo Edição Automágica (com IA Completa)"""
        import threading
        def worker():
            try:
                self.config_status_label.config(text="Iniciando pipeline IA...", foreground='blue')
                self.log_message("Iniciando pipeline Automágico...", "INFO")
                video = self.input_file.get()
                output = self.output_file.get()
                cut_style = self.magic_cut_style.get()
                conciseness = self.magic_conciseness.get()
                # Mapear sliders para parâmetros concretos
                margin = round(0.1 + (cut_style-1)*0.1, 2)  # 0.1 a 0.5
                threshold = round(0.04 + (cut_style-1)*0.01, 2)  # 0.04 a 0.08
                # 1. Análise de Silêncio
                self.config_status_label.config(text="Analisando silêncio...", foreground='blue')
                json_path = tempfile.mktemp(suffix="_ae.json")
                cmd = ["auto-editor", video, "-m", str(margin), "--edit", "audio", "--silent-threshold", str(threshold), "--export", "json", "-o", json_path]
                self.log_message(f"Comando: {' '.join(map(str,cmd))}", "INFO")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.config_status_label.config(text="Erro na análise de silêncio.", foreground='red')
                    self.log_message(result.stderr, "ERROR")
                    return
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                speech_chunks = data.get('chunks', [])
                self.log_message(f"{len(speech_chunks)} clipes de fala detectados.", "SUCCESS")
                # 2. Transcrição com Whisper
                self.config_status_label.config(text="Transcrevendo áudio...", foreground='blue')
                if not WHISPER_AVAILABLE:
                    self.config_status_label.config(text="Whisper não disponível.", foreground='red')
                    self.log_message("Whisper não instalado.", "ERROR")
                    return
                if not hasattr(self, 'whisper_result') or self.whisper_result is None:
                    # Extrair áudio temporário
                    audio_path = tempfile.mktemp(suffix="_audio.mp3")
                    cmd_audio = ["ffmpeg", "-y", "-i", video, "-vn", "-acodec", "mp3", audio_path]
                    subprocess.run(cmd_audio, capture_output=True)
                    model = whisper.load_model(self.whisper_model.get())
                    self.whisper_result = model.transcribe(audio_path, fp16=self.use_gpu.get())
                transcription = self.whisper_result.get('text', '')
                segments = self.whisper_result.get('segments', [])
                # 3. Análise de Erros (LLM Pass 1)
                self.config_status_label.config(text="Analisando erros de fala (LLM Pass 1)...", foreground='blue')
                rigor_prompt = f"Remova erros de fala, hesitações e repetições. Seja rigoroso nível {conciseness}/5. Retorne apenas os timestamps dos erros."  # Exemplo
                error_timestamps = self.llm_analyze_errors(transcription, segments, rigor_prompt)
                # 4. Análise de Narrativa (LLM Pass 2)
                self.config_status_label.config(text="Analisando narrativa (LLM Pass 2)...", foreground='blue')
                conciseness_prompt = f"Reorganize e resuma o texto para um vídeo mais enxuto (nível {conciseness}/5). Retorne a playlist final (start/end) e clipes a excluir."  # Exemplo
                playlist, to_exclude = self.llm_analyze_narrative(transcription, segments, conciseness_prompt)
                # 5. Renderização
                if self.magic_jcut_enabled.get():
                    self.config_status_label.config(text="Renderizando com J-Cut...", foreground='blue')
                    self.engine_jcut(playlist, self.magic_jcut_duration.get(), video, output)
                else:
                    self.config_status_label.config(text="Renderizando vídeo final...", foreground='blue')
                    # Exportar clipes na ordem da playlist
                    addins = []
                    for clip in playlist:
                        addins.extend(["--add-in", f"{clip['start']}-{clip['end']}"])
                    cmd2 = ["auto-editor", video, "--edit", "all/e"] + addins + ["-o", output]
                    self.log_message(f"Comando: {' '.join(map(str,cmd2))}", "INFO")
                    result2 = subprocess.run(cmd2, capture_output=True, text=True)
                    if result2.returncode != 0:
                        self.config_status_label.config(text="Erro na renderização.", foreground='red')
                        self.log_message(result2.stderr, "ERROR")
                        return
                self.config_status_label.config(text="Edição Automágica concluída!", foreground='green')
                self.log_message("Edição Automágica finalizada com sucesso!", "SUCCESS")
            except Exception as e:
                self.config_status_label.config(text=f"Erro: {e}", foreground='red')
                self.log_message(str(e), "ERROR")
        threading.Thread(target=worker, daemon=True).start()

    def llm_analyze_errors(self, transcription, segments, prompt):
        """Chama o LLM para análise de erros de fala. Retorna lista de timestamps."""
        try:
            self.log_message("Chamando LLM para análise de erros de fala...", "INFO")
            if OPENAI_AVAILABLE and self.selected_llm_provider.get() == "openai":
                response = openai.ChatCompletion.create(
                    model=self.selected_llm_model.get(),
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": transcription}]
                )
                content = response['choices'][0]['message']['content']
                self.log_message(f"Resposta LLM: {content}", "INFO")
                try:
                    # Espera-se que o LLM retorne JSON: {"errors": [{"start":..., "end":...}, ...]}
                    import json as _json
                    parsed = _json.loads(content)
                    return parsed.get('errors', [])
                except Exception:
                    self.log_message("Resposta do LLM não é JSON. Retornando vazio.", "WARNING")
                    return []
            elif GEMINI_AVAILABLE and self.selected_llm_provider.get() == "gemini":
                response = genai.generate_content(prompt + "\n" + transcription)
                content = response.text
                self.log_message(f"Resposta Gemini: {content}", "INFO")
                try:
                    import json as _json
                    parsed = _json.loads(content)
                    return parsed.get('errors', [])
                except Exception:
                    self.log_message("Resposta do Gemini não é JSON. Retornando vazio.", "WARNING")
                    return []
            else:
                self.log_message("Nenhum LLM disponível. Retornando lista vazia.", "WARNING")
                return []
        except Exception as e:
            self.log_message(f"Erro ao chamar LLM: {e}", "ERROR")
            return []

    def llm_analyze_narrative(self, transcription, segments, prompt):
        """Chama o LLM para análise de narrativa. Retorna playlist e clipes a excluir."""
        try:
            self.log_message("Chamando LLM para análise de narrativa...", "INFO")
            if OPENAI_AVAILABLE and self.selected_llm_provider.get() == "openai":
                response = openai.ChatCompletion.create(
                    model=self.selected_llm_model.get(),
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": transcription}]
                )
                content = response['choices'][0]['message']['content']
                self.log_message(f"Resposta LLM: {content}", "INFO")
                try:
                    import json as _json
                    parsed = _json.loads(content)
                    playlist = parsed.get('playlist', [])
                    to_exclude = parsed.get('to_exclude', [])
                    return playlist, to_exclude
                except Exception:
                    self.log_message("Resposta do LLM não é JSON. Usando playlist padrão.", "WARNING")
                    playlist = []
                    for seg in segments:
                        playlist.append({'start': seg['start'], 'end': seg['end']})
                    to_exclude = []
                    return playlist, to_exclude
            elif GEMINI_AVAILABLE and self.selected_llm_provider.get() == "gemini":
                response = genai.generate_content(prompt + "\n" + transcription)
                content = response.text
                self.log_message(f"Resposta Gemini: {content}", "INFO")
                try:
                    import json as _json
                    parsed = _json.loads(content)
                    playlist = parsed.get('playlist', [])
                    to_exclude = parsed.get('to_exclude', [])
                    return playlist, to_exclude
                except Exception:
                    self.log_message("Resposta do Gemini não é JSON. Usando playlist padrão.", "WARNING")
                    playlist = []
                    for seg in segments:
                        playlist.append({'start': seg['start'], 'end': seg['end']})
                    to_exclude = []
                    return playlist, to_exclude
            else:
                self.log_message("Nenhum LLM disponível. Retornando playlist padrão.", "WARNING")
                playlist = []
                for seg in segments:
                    playlist.append({'start': seg['start'], 'end': seg['end']})
                to_exclude = []
                return playlist, to_exclude
        except Exception as e:
            self.log_message(f"Erro ao chamar LLM: {e}", "ERROR")
            playlist = []
            for seg in segments:
                playlist.append({'start': seg['start'], 'end': seg['end']})
            to_exclude = []
            return playlist, to_exclude

def main():
    """Função principal"""
    root = tk.Tk()
    app = AutoEditorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 