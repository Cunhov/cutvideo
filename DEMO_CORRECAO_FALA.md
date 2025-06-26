# 🎯 Demonstração: Correção de Fala por IA

Este guia demonstra como usar a nova funcionalidade de **Correção de Fala por IA** na Auto-Editor GUI.

## 📋 Pré-requisitos

1. **Auto-Editor GUI** instalada e funcionando
2. **Whisper** instalado (execute `python3 install_whisper.py`)
3. **ffmpeg** instalado e no PATH
4. **Arquivo de vídeo** com áudio para testar

## 🚀 Passo a Passo

### 1. Preparação

```bash
# Instalar Whisper (se ainda não instalou)
python3 install_whisper.py

# Executar a aplicação
python3 auto_editor_gui.py
```

### 2. Configuração Inicial

1. **Aba "Configurações"**:
   - Clique em "Escolher Vídeo" e selecione um arquivo de vídeo
   - Configure o nome do arquivo de saída
   - Escolha o tipo de saída (ex: MP4)

### 3. 🎯 Correção de Fala por IA

1. **Vá para a aba "Correção de Fala (IA)"**

2. **Configure o Whisper**:
   - **Modelo**: Escolha entre:
     - `tiny`: Mais rápido, menos preciso
     - `base`: Equilibrado (recomendado para testes)
     - `small`: Melhor precisão
     - `medium`: Alta precisão
     - `large`: Máxima precisão
   - **GPU**: Marque se tiver GPU disponível

3. **Configure a Análise**:
   - ✅ **Detectar repetições**: Marque para detectar palavras repetidas
   - ✅ **Detectar palavras de preenchimento**: Marque para detectar "um", "ah", etc.
   - **Palavras personalizadas**: Adicione suas próprias palavras (ex: "tipo", "né", "então")

4. **Inicie a Análise**:
   - Clique em **"🎤 1. Analisar Fala com Whisper"**
   - Aguarde o processo (pode demorar alguns minutos)
   - O status mostrará o progresso

### 4. Revisão da Transcrição

Após a análise, você verá:

- **Transcrição completa** com timestamps
- **Erros detectados** em **amarelo**:
  - Palavras de preenchimento
  - Repetições
- **Contador de cortes** no canto superior direito

### 5. Seleção Manual

1. **Selecione trechos** na transcrição:
   - Clique e arraste para selecionar texto
   - O texto selecionado ficará com fundo azul

2. **Marcar para remoção**:
   - Clique em **"🔴 Marcar Seleção para Remover"**
   - O texto ficará com fundo **vermelho**
   - Será adicionado à lista de cortes

3. **Desmarcar**:
   - Selecione um trecho marcado
   - Clique em **"🔄 Desmarcar Seleção"**

### 6. Execução Final

1. **Volte para a aba "Configurações"**

2. **Verifique o comando gerado**:
   - Deve incluir `--cut-out` com os timestamps dos cortes

3. **Clique em "Iniciar Edição"**

4. **Acompanhe no console**:
   - Vá para a aba "Console"
   - Veja o progresso em tempo real
   - Os cortes de fala serão aplicados automaticamente

## 🎬 Exemplo Prático

### Cenário: Vídeo de apresentação com erros de fala

**Problemas típicos**:
- "Um... vamos começar"
- "Tipo assim, né?"
- "Então, basicamente..."
- Repetições: "O projeto, o projeto está pronto"

**Solução**:
1. Analise com Whisper
2. Marque automaticamente os fillers detectados
3. Selecione manualmente repetições não detectadas
4. Execute a edição

**Resultado**: Vídeo limpo sem erros de fala!

## ⚙️ Configurações Avançadas

### Modelos Whisper

| Modelo | Tamanho | Velocidade | Precisão | Uso Recomendado |
|--------|---------|------------|----------|-----------------|
| tiny   | 39 MB   | ⚡⚡⚡⚡⚡    | ⭐⭐      | Testes rápidos |
| base   | 74 MB   | ⚡⚡⚡⚡     | ⭐⭐⭐     | Uso geral |
| small  | 244 MB  | ⚡⚡⚡      | ⭐⭐⭐⭐    | Alta precisão |
| medium | 769 MB  | ⚡⚡       | ⭐⭐⭐⭐⭐   | Profissional |
| large  | 1550 MB | ⚡        | ⭐⭐⭐⭐⭐   | Máxima precisão |

### Palavras de Preenchimento Comuns

**Português**:
- um, uh, ah, hmm
- tipo, né, então, sabe
- basicamente, na verdade
- tipo assim, entendeu

**Inglês**:
- um, uh, ah, er
- like, you know, so
- basically, actually
- I mean, right

## 🔧 Solução de Problemas

### "Whisper não encontrado"
```bash
python3 install_whisper.py
```

### "Análise muito lenta"
- Use modelo `tiny` ou `base`
- Desmarque "Processar em GPU" se não tiver GPU
- Primeira execução é mais lenta (download do modelo)

### "Erros não detectados"
- Use modelo mais preciso (`small`, `medium`, `large`)
- Adicione palavras personalizadas
- Selecione manualmente os trechos

### "Transcrição incorreta"
- Verifique se o áudio está claro
- Use modelo mais preciso
- Verifique se o ffmpeg está funcionando

## 📊 Estatísticas Típicas

**Tempo de análise** (vídeo de 10 minutos):
- Modelo tiny: 2-3 minutos
- Modelo base: 5-7 minutos
- Modelo small: 10-15 minutos
- Modelo medium: 20-30 minutos
- Modelo large: 40-60 minutos

**Detecção de erros**:
- Palavras de preenchimento: 80-95% de precisão
- Repetições: 70-85% de precisão
- Depende da qualidade do áudio e modelo usado

## 🎯 Dicas de Uso

1. **Para vídeos longos**: Use modelo `tiny` primeiro, depois `base` se necessário
2. **Para qualidade profissional**: Use `small` ou `medium`
3. **Para máxima precisão**: Use `large` (requer mais tempo e recursos)
4. **Sempre revise**: A IA é boa, mas não perfeita
5. **Teste com trechos**: Use um trecho pequeno primeiro para testar

## 🚀 Próximos Passos

Após dominar a correção de fala por IA:

1. **Combine com edição manual** para resultados perfeitos
2. **Use diferentes modelos** para diferentes tipos de conteúdo
3. **Crie listas personalizadas** de palavras para seus projetos
4. **Automatize workflows** para projetos recorrentes

---

**🎉 Parabéns!** Você agora domina a funcionalidade de correção de fala por IA da Auto-Editor GUI! 