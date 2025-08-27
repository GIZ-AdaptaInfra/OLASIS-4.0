# Sistema de Sugestões Contextuais do OLABOT

## Visão Geral

O sistema de sugestões contextuais ("balões") foi implementado para melhorar a experiência do usuário ao interagir com o OLABOT. Ele fornece perguntas pré-sugeridas baseadas no contexto, área de conhecimento e histórico do usuário.

## Funcionalidades Implementadas

### 1. Sugestões Contextuais
- **Beginner**: Perguntas básicas para iniciantes em pesquisa científica
- **Intermediate**: Perguntas de nível intermediário sobre metodologias
- **Advanced**: Perguntas avançadas sobre publicação e financiamento
- **Search Focused**: Perguntas relacionadas à busca de literatura
- **Methodology Focused**: Perguntas sobre métodos de pesquisa
- **General**: Perguntas gerais sobre diversos tópicos

### 2. Sugestões por Área de Conhecimento
- **Medicina**: Medicina personalizada, ensaios clínicos, telemedicina
- **Tecnologia**: Machine learning, blockchain, IoT, computação quântica
- **Meio Ambiente**: Energias renováveis, mudanças climáticas, sustentabilidade
- **Educação**: Metodologias ativas, tecnologia educacional, avaliação online

### 3. Sugestões Adaptativas
- Análise do histórico de perguntas do usuário
- Detecção automática do nível de conhecimento
- Identificação de áreas de interesse
- Personalização baseada no comportamento

## Estrutura de Arquivos

### Backend
- `olasis/prompt_engineering.py`: Classe `ChatSuggestions` com toda a lógica de geração
- `app.py`: Endpoint `/api/chat/suggestions` para servir as sugestões

### Frontend
- `templates/index.html`: Interface visual e JavaScript para exibição das sugestões

## API Endpoint

### GET /api/chat/suggestions

**Parâmetros:**
- `context` (opcional): Tipo de contexto ("general", "beginner", "advanced", etc.)
- `field` (opcional): Área de conhecimento ("medicina", "tecnologia", etc.)
- `count` (opcional): Número de sugestões (padrão: 4)
- `history` (opcional): Histórico de perguntas para sugestões adaptativas

**Exemplo de Resposta:**
```json
{
  "context": "tecnologia",
  "count": 4,
  "field": "tecnologia",
  "suggestions": [
    "Aplicações de machine learning na ciência",
    "Blockchain na pesquisa científica",
    "Internet das Coisas (IoT) em saúde",
    "Computação quântica: fundamentos e aplicações"
  ]
}
```

## Interface do Usuário

### Elementos Visuais
- **Container de sugestões**: `.chat-suggestions`
- **Balões individuais**: `.suggestion-bubble`
- **Animações**: Fade-in ao carregar, fade-out ao clicar
- **Responsividade**: Adaptável a diferentes tamanhos de tela

### Comportamento
1. As sugestões aparecem automaticamente quando o chat é aberto
2. Usuário pode clicar em qualquer sugestão para enviá-la
3. Após o envio, as sugestões desaparecem com animação
4. Indicador de digitação do bot aparece durante o processamento

## Configurações

### Parâmetros Ajustáveis
```python
# Em prompt_engineering.py
BEST_PRACTICES_CONFIG = {
    "max_response_length": 2000,
    "min_response_length": 100,
    "temperature": 0.7,
    "supported_languages": ["pt-BR"],
    "response_format": "plain_text"
}
```

### CSS Customizável
```css
.chat-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 15px;
    padding: 10px;
}

.suggestion-bubble {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
}
```

## Testes Realizados

### Endpoint API
- ✅ Sugestões gerais: `GET /api/chat/suggestions`
- ✅ Sugestões por contexto: `GET /api/chat/suggestions?context=advanced`
- ✅ Sugestões por área: `GET /api/chat/suggestions?field=tecnologia`
- ✅ Combinação de parâmetros: `GET /api/chat/suggestions?field=medicina&context=beginner`

### Interface
- ✅ Carregamento automático das sugestões
- ✅ Animações de entrada e saída
- ✅ Envio de mensagem ao clicar
- ✅ Responsividade em diferentes dispositivos
- ✅ Fallback para sugestões estáticas em caso de erro na API

## Melhorias Futuras

### Funcionalidades Planejadas
1. **Internacionalização**: Suporte para inglês e espanhol
2. **Aprendizado de máquina**: Melhorar sugestões baseadas em interações
3. **Integração com perfil**: Conectar com dados do usuário logado
4. **Analytics**: Métricas de uso e efetividade das sugestões
5. **A/B Testing**: Testar diferentes conjuntos de sugestões

### Otimizações Técnicas
1. **Cache**: Implementar cache para sugestões frequentes
2. **Lazy Loading**: Carregar sugestões sob demanda
3. **Compressão**: Otimizar tamanho das respostas da API
4. **Rate Limiting**: Controlar frequência de requests

## Monitoramento

### Métricas Importantes
- Taxa de clique nas sugestões
- Tempo médio para primeira interação
- Satisfação do usuário com as sugestões
- Performance do endpoint API
- Erros e fallbacks utilizados

### Logs Relevantes
- Requests para o endpoint de sugestões
- Erros na geração de sugestões
- Tempos de resposta da API
- Uso de fallbacks

## Suporte e Manutenção

### Atualizando Sugestões
Para adicionar novas sugestões, edite os dicionários em `ChatSuggestions`:
- `SUGGESTIONS_BY_CONTEXT`: Para diferentes níveis de usuário
- `SUGGESTIONS_BY_FIELD`: Para áreas específicas de conhecimento

### Depuração
1. Verifique se a aplicação está rodando: `PORT=5001 python app.py`
2. Teste o endpoint: `curl "http://localhost:5001/api/chat/suggestions"`
3. Verifique os logs do console do navegador para erros JavaScript
4. Confirme se o CSS está sendo aplicado corretamente

## Conclusão

O sistema de sugestões contextuais está totalmente implementado e funcional, proporcionando uma experiência mais rica e intuitiva para os usuários do OLABOT. A arquitetura modular permite fácil expansão e customização conforme as necessidades futuras do projeto.
