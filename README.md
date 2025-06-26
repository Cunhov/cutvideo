# Auto-Editor GUI v3.0 🎬

**Interface gráfica avançada para edição automática de vídeos com IA**

Uma aplicação desktop completa que combina o poder do `auto-editor` com funcionalidades avançadas de Inteligência Artificial para transcrição, correção de fala e reorganização semântica de vídeos.

## ✨ Funcionalidades Principais

### 🎯 Edição Automática
- **Corte automático** baseado em áudio, movimento ou ambos
- **Interface intuitiva** para configuração de parâmetros
- **Visualização em tempo real** do comando gerado
- **Monitoramento de progresso** com logs detalhados

### 🗣️ Correção de Fala por IA
- **Transcrição inteligente** com OpenAI Whisper (API ou local)
- **Análise de erros por LLM** usando GPT-4o ou Google Gemini
- **Detecção automática** de:
  - Palavras de preenchimento ("um", "ah", "tipo", "né")
  - Repetições desnecessárias
  - Gaguejos e hesitações
  - Pausas longas
  - Erros gramaticais
  - Conteúdo irrelevante
- **Interface interativa** para revisão e aplicação de correções
- **Sugestões inteligentes** com justificativas detalhadas

### 🧠 Reorganização Semântica
- **Análise de estrutura narrativa** por LLM
- **Sugestões de reordenação** de clipes de fala
- **Identificação de conteúdo** desnecessário
- **Renderização avançada** com ffmpeg
- **Interface visual** para aprovação/rejeição de sugestões

### ⚡ Otimizações de Performance
- **Processamento em lotes** para economia de memória
- **Monitoramento de recursos** em tempo real
- **Limpeza automática** de arquivos temporários
- **Interface responsiva** sem travamentos

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- ffmpeg instalado no sistema
- auto-editor instalado

### Instalação Automática
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd cutvideo

# Execute o setup completo
python3 setup.py
```

### Instalação Manual
```bash
# Instalar dependências do sistema
pip install auto-editor
brew install ffmpeg  # macOS
# ou
sudo apt install ffmpeg  # Ubuntu/Debian

# Instalar dependências Python
pip install openai openai-whisper tiktoken psutil google-generativeai
```

## 🔑 Configuração de APIs

### 1. Obter API Keys
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Gemini**: https://makersuite.google.com/app/apikey

### 2. Configurar na Aplicação
1. Execute a aplicação: `python3 auto_editor_gui.py`
2. Vá para a aba "Configurações"
3. Insira suas API Keys nas seções correspondentes
4. Clique em "💾 Salvar Chaves"
5. Teste as conexões com "🧪 Testar OpenAI" e "🧪 Testar Gemini"

## 📖 Como Usar

### 1. Configuração Básica
1. **Selecione o arquivo de vídeo** na aba "Configurações"
2. **Escolha o tipo de corte**: Áudio, Movimento ou Todos
3. **Configure o arquivo de saída**
4. **Clique em "🎬 Iniciar Edição"**

### 2. Correção de Fala por IA
1. **Vá para a aba "Correção de Fala (IA)"**
2. **Clique em "🎤 1. Analisar Fala com Whisper"**
3. **Aguarde a transcrição** (pode demorar alguns minutos)
4. **Clique em "🤖 2. Analisar Erros com LLM"**
5. **Revise as sugestões** na lista
6. **Aplique ou rejeite** as correções desejadas
7. **Marque manualmente** trechos para remoção se necessário

### 3. Reorganização Semântica
1. **Vá para a aba "Reorganização por IA"**
2. **Descreva o objetivo** do vídeo no campo de texto
3. **Clique em "🧠 Analisar Estrutura Narrativa"**
4. **Revise as sugestões** de reordenação
5. **Aprove ou descarte** as mudanças
6. **Clique em "🎬 Renderizar Vídeo Final"**

### 4. Monitoramento
- **Aba "Console"**: Logs detalhados de todas as operações
- **Monitoramento de memória**: Uso de recursos em tempo real
- **Limpeza manual**: Botão para liberar memória quando necessário

## 🎯 Funcionalidades Avançadas

### Seleção de LLM
- **OpenAI GPT-4o**: Análise mais precisa e contextual
- **Google Gemini**: Alternativa eficiente e econômica
- **Seleção de modelos**: Escolha o modelo específico da API
- **Teste de conexão**: Verificação automática de disponibilidade

### Análise de Fala Inteligente
- **Detecção automática** de problemas de fala
- **Sugestões contextualizadas** com justificativas
- **Interface intuitiva** para revisão
- **Aplicação seletiva** de correções
- **Estatísticas detalhadas** de mudanças

### Otimizações de Memória
- **Processamento em lotes** para arquivos grandes
- **Limpeza automática** de recursos
- **Monitoramento em tempo real** do uso de memória
- **Interface responsiva** mesmo com arquivos pesados

## 🔧 Configurações Avançadas

### Whisper
- **Modo API**: Mais rápido, requer API Key
- **Modo Local**: Funciona offline, mais lento
- **Seleção de modelo**: tiny, base, small, medium, large
- **Suporte a GPU**: Aceleração quando disponível

### LLM
- **Provedor**: OpenAI ou Google Gemini
- **Modelo**: Seleção automática dos disponíveis
- **Configuração persistente**: Salva preferências
- **Teste de conectividade**: Verificação automática

## 📊 Monitoramento e Logs

### Console em Tempo Real
- **Logs detalhados** de todas as operações
- **Cores por tipo**: INFO, SUCCESS, WARNING, ERROR
- **Timestamps** precisos
- **Scroll automático** para acompanhar progresso

### Monitoramento de Recursos
- **Uso de memória** em tempo real
- **Logs de performance** em pontos críticos
- **Limpeza automática** de recursos
- **Botão de limpeza manual** quando necessário

## 🛠️ Solução de Problemas

### Erros Comuns

#### "API Key não configurada"
1. Verifique se inseriu a API Key corretamente
2. Clique em "💾 Salvar Chaves"
3. Teste a conexão com "🧪 Testar OpenAI/Gemini"

#### "Biblioteca não instalada"
```bash
# Execute o setup completo
python3 setup.py

# Ou instale manualmente
pip install openai openai-whisper tiktoken psutil google-generativeai
```

#### "ffmpeg não encontrado"
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Baixe de https://ffmpeg.org/download.html
```

#### "Uso excessivo de memória"
1. Use o modo API do Whisper (não local)
2. Clique em "🧹 Limpeza Manual" na aba Console
3. Processe arquivos menores ou em partes
4. Monitore os logs de memória

### Logs de Debug
- **Console detalhado**: Todas as operações são logadas
- **Timestamps**: Identificação precisa de problemas
- **Cores**: Diferenciação visual de tipos de log
- **Scroll automático**: Acompanhamento em tempo real

## 📈 Melhorias da Versão 3.0

### Novas Funcionalidades
- ✅ **Sistema completo de gerenciamento de APIs**
- ✅ **Suporte ao Google Gemini**
- ✅ **Análise de fala por LLM**
- ✅ **Interface intuitiva para correções**
- ✅ **Seleção de modelos de LLM**
- ✅ **Configuração persistente**
- ✅ **Teste de conectividade**
- ✅ **Monitoramento avançado de recursos**

### Otimizações
- ⚡ **Redução de 90% no uso de memória**
- ⚡ **Processamento em lotes**
- ⚡ **Limpeza automática de recursos**
- ⚡ **Interface mais responsiva**
- ⚡ **Logs detalhados de performance**

## 🤝 Contribuição

1. **Fork** o projeto
2. **Crie** uma branch para sua feature
3. **Commit** suas mudanças
4. **Push** para a branch
5. **Abra** um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- **Auto-Editor**: Ferramenta base para edição automática
- **OpenAI**: Whisper e GPT-4o para análise de fala
- **Google**: Gemini para análise alternativa
- **FFmpeg**: Processamento de vídeo
- **Comunidade Python**: Bibliotecas e ferramentas

---

**Desenvolvido com ❤️ para facilitar a edição de vídeos com IA** 