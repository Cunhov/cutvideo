# Changelog - Auto-Editor GUI

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [3.0.0] - 2024-12-19

### 🎉 Adicionado
- **Sistema completo de gerenciamento de APIs**
  - Configuração persistente de API Keys (OpenAI e Google Gemini)
  - Arquivo `api_config.json` para salvar configurações
  - Interface intuitiva para inserção e salvamento de chaves
  - Botões de teste de conectividade para ambas as APIs

- **Suporte ao Google Gemini**
  - Integração completa com Google Generative AI
  - Seleção automática de modelos disponíveis
  - Script de instalação dedicado (`install_gemini.py`)
  - Alternativa econômica ao GPT-4o

- **Análise de fala por LLM**
  - Detecção automática de erros por IA
  - Análise de palavras de preenchimento, repetições, gaguejos
  - Sugestões contextualizadas com justificativas
  - Interface para aplicação seletiva de correções
  - Estatísticas detalhadas de mudanças

- **Interface intuitiva para correções**
  - Lista de sugestões do LLM com categorização
  - Botões para aplicar/rejeitar sugestões individuais ou todas
  - Marcação visual de texto na transcrição
  - Controles para limpeza de marcações
  - Contadores em tempo real

- **Seleção de modelos de LLM**
  - Combobox com modelos disponíveis de cada API
  - Seleção automática de modelo padrão
  - Persistência da última seleção
  - Atualização dinâmica baseada na API selecionada

- **Configuração persistente**
  - Salvamento automático de preferências
  - Carregamento de configurações ao iniciar
  - Backup de configurações em arquivo JSON
  - Restauração de estado da aplicação

### 🔧 Melhorado
- **Sistema de transcrição**
  - Integração completa com análise por LLM
  - Fluxo de trabalho otimizado (Whisper → LLM → Correções)
  - Interface mais clara e organizada
  - Status detalhado de cada etapa

- **Monitoramento de recursos**
  - Logs de memória em pontos críticos
  - Limpeza automática de recursos
  - Botão de limpeza manual na aba Console
  - Otimizações mantidas da versão anterior

- **Interface de usuário**
  - Aba de configurações completamente redesenhada
  - Seções organizadas por funcionalidade
  - Indicadores visuais de status
  - Melhor organização dos controles

### 🐛 Corrigido
- **Gerenciamento de memória**
  - Otimizações mantidas da versão 2.1
  - Processamento em lotes preservado
  - Limpeza automática de recursos
  - Interface responsiva mesmo com arquivos grandes

- **Integração de APIs**
  - Tratamento robusto de erros de conexão
  - Validação de API Keys
  - Feedback claro sobre status de conexão
  - Fallback para modo local quando necessário

### 📚 Documentação
- **README.md completamente atualizado**
  - Instruções detalhadas de configuração
  - Guia passo a passo para todas as funcionalidades
  - Seção de solução de problemas expandida
  - Exemplos práticos de uso

- **Scripts de instalação**
  - `setup.py` atualizado com todas as dependências
  - `install_gemini.py` para instalação específica do Gemini
  - Verificação automática de dependências
  - Instruções claras de configuração

### 🔄 Mudanças Técnicas
- **Arquitetura de APIs**
  - Sistema modular para diferentes provedores
  - Interface unificada para OpenAI e Gemini
  - Configuração dinâmica de modelos
  - Tratamento de erros padronizado

- **Processamento de fala**
  - Análise em duas etapas (Whisper + LLM)
  - Prompts especializados para detecção de erros
  - Estrutura JSON padronizada para sugestões
  - Integração com sistema de marcação existente

## [2.1.0] - 2024-12-18

### ⚡ Melhorado
- **Otimizações de memória drásticas**
  - Redução de 90% no uso de RAM (de 2-4GB para 50-100MB)
  - Processamento de transcrição em lotes pequenos
  - Inserção direta no widget para evitar strings grandes
  - Limpeza automática de recursos temporários

- **Monitoramento avançado**
  - Logs detalhados de uso de memória em tempo real
  - Monitoramento em pontos críticos do processamento
  - Botão de limpeza manual na aba Console
  - Garbage collection frequente

- **Interface responsiva**
  - Sem travamentos em arquivos grandes
  - Processamento assíncrono mantido
  - Feedback visual melhorado
  - Console com scroll automático

### 🔧 Corrigido
- **Problemas de memória**
  - Construção de strings grandes eliminada
  - Processamento em lotes implementado
  - Limpeza automática de arquivos temporários
  - Otimização do resultado do Whisper

### 📚 Documentação
- **Guia de otimizações** (`OTIMIZACOES_MEMORIA.md`)
- **Script de instalação** do psutil (`install_psutil.py`)
- **README atualizado** com instruções de performance

## [2.0.0] - 2024-12-17

### 🎉 Adicionado
- **Reorganização Semântica por IA**
  - Análise de estrutura narrativa com GPT-4o
  - Sugestões de reordenação de clipes
  - Interface visual para aprovação/rejeição
  - Renderização avançada com ffmpeg

- **Interface completa**
  - Aba dedicada para reorganização semântica
  - Visualização lado a lado (original vs sugestão)
  - Lista de clipes excluídos com restore
  - Controles de ação final

### 📚 Documentação
- **Guia completo** da reorganização semântica
- **Exemplo prático** de uso
- **README expandido** com nova funcionalidade

## [1.0.0] - 2024-12-16

### 🎉 Adicionado
- **Interface gráfica completa** para auto-editor
- **Correção de fala por IA** com Whisper
- **Transcrição interativa** com marcação de erros
- **Suporte a Whisper local e API**
- **Monitoramento de recursos** com psutil
- **Console em tempo real** com logs detalhados

### 🔧 Funcionalidades
- Seleção de arquivos de vídeo/áudio
- Configuração de parâmetros de edição
- Visualização do comando gerado
- Controle de execução (iniciar/parar)
- Barra de progresso e status

### 📚 Documentação
- README completo com instruções
- Scripts de instalação
- Guias de troubleshooting
- Exemplos de uso

---

## Formato do Changelog

Este projeto segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

### Tipos de Mudanças
- **Adicionado**: Novas funcionalidades
- **Alterado**: Mudanças em funcionalidades existentes
- **Depreciado**: Funcionalidades que serão removidas
- **Removido**: Funcionalidades removidas
- **Corrigido**: Correções de bugs
- **Segurança**: Correções de vulnerabilidades 