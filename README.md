# OLASIS 4.0

## Visão Geral

**OLASIS 4.0** (*Observatório para Sistema de Infraestrutura Sustentável*) é uma aplicação web completa desenvolvida em Python. Ela fornece três serviços principais:

1. **Assistente conversacional (OLABOT)** – um chatbot inteligente alimentado pelos modelos Gemini do Google. Ele pode resumir documentos, responder perguntas e fornecer orientações sobre infraestrutura sustentável. Internamente utiliza o cliente [Gemini API quick‑start](https://ai.google.dev/gemini-api/docs/quickstart). A aplicação lê a chave da API de uma variável de ambiente (`GOOGLE_API_KEY`) e inicializa um cliente através do SDK `google‑genai` para gerar respostas programaticamente.

2. **Busca de artigos** – consulta a [API pública do OpenAlex](https://api.openalex.org) para recuperar trabalhos acadêmicos. Por exemplo, o pacote R de código aberto `openalexR` internamente envia requisições como:

   > `https://api.openalex.org/works?search=BRAF%20AND%20melanoma`

   A aplicação replica esse comportamento em Python para buscar metadados (título, autores, ano, DOI, etc.) e exibir os registros mais relevantes para o usuário.

3. **Busca de especialistas** – faz interface com a [API de busca pública do ORCID](https://pub.orcid.org). De acordo com o FAQ do ORCID da Australian Access Federation, a API pública permite consultas anônimas por endereço de e-mail ou nome da organização; por exemplo, `https://pub.orcid.org/v3.0/search/?q=email:*@orcid.org` busca endereços de e-mail públicos e `https://pub.orcid.org/v3.0/search/?q=affiliation-org-name:"ORCID"` busca registros públicos por afiliação. OLASIS 4.0 usa esses endpoints de busca para encontrar especialistas por nome, afiliação ou palavra-chave e retorna seu identificador ORCID junto com um breve perfil.

## Estrutura do Repositório

```
OLASIS-4.0/
│
├── README.md               # Este arquivo: descrição, instalação e uso
├── requirements.txt        # Dependências Python para a aplicação
├── app.py                  # Ponto de entrada da aplicação Flask
├── Procfile                # Configuração para deploy (Railway/Heroku)
├── railway.json            # Configuração específica do Railway
├── runtime.txt             # Versão do Python para deploy
├── .env                    # Variáveis de ambiente (não versionado)
├── .gitignore              # Arquivos ignorados pelo Git
├── templates/
│   └── index.html          # Página HTML principal (adaptada do Olasis4.html)
├── static/
│   └── js/
│       └── main.js         # Lógica do lado cliente que integra com a API
└── olasis/
    ├── __init__.py         # Marcador de pacote Python
    ├── chatbot.py          # Wrapper em torno do cliente Google Gemini
    ├── articles.py         # Funções para consultar OpenAlex
    ├── specialists.py      # Funções para consultar ORCID
    └── utils.py            # Funções auxiliares compartilhadas
```

## Instalação

1. **Clone o repositório** (ou copie-o para o diretório do seu projeto).

   ```sh
   git clone <seu-fork-deste-repo> olasis4
   cd olasis4
   ```

2. **Crie um ambiente virtual Python** (opcional, mas recomendado).

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências**. O projeto requer Python 3.9 ou posterior.

   ```sh
   pip install -r requirements.txt
   ```

4. **Configure a chave da API do Google**. A chave da API Gemini deve ser fornecida através da variável de ambiente `GOOGLE_API_KEY`. Você pode obter uma chave gratuita do [Google AI Studio](https://aistudio.google.com/) e exportá-la antes de executar a aplicação:

   ```sh
   export GOOGLE_API_KEY="sua_chave_api_aqui"
   ```

   Ou criar um arquivo `.env` na raiz do projeto:

   ```
   GOOGLE_API_KEY=sua_chave_api_aqui
   ```

5. **Execute a aplicação** usando Flask. O servidor iniciará em `http://localhost:5000` por padrão.

   ```sh
   python app.py
   ```

## Deploy

OLASIS 4.0 usa um backend Flask e um frontend estático, o que torna o deploy flexível. Você pode executar a aplicação em qualquer plataforma que suporte Python e [Flask](https://flask.palletsprojects.com/).

### Deploy no Railway (Recomendado)

1. **Acesse [railway.app](https://railway.app)** e faça login com sua conta GitHub
2. **Clique em "New Project"** e selecione "Deploy from GitHub repo"
3. **Conecte seu repositório** do OLASIS 4.0
4. **Configure as variáveis de ambiente**:
   - `GOOGLE_API_KEY`: sua chave da API do Google Gemini
5. **O deploy será feito automaticamente** e você receberá uma URL pública

### Outras Opções de Deploy

- **Render**: [render.com](https://render.com) - gratuito com HTTPS
- **Vercel**: [vercel.com](https://vercel.com) - para aplicações serverless
- **Heroku**: [heroku.com](https://heroku.com) - plataforma clássica (pago)

Para uso em produção, é recomendado servir a aplicação via um servidor WSGI como **gunicorn** (já incluído no `requirements.txt`) atrás de um proxy reverso como **nginx**.

## Uso

A página principal fornece três funcionalidades principais:

### 🤖 **Chatbot (OLABOT)**
Clique no ícone OLABOT para abrir uma janela de chat e fazer qualquer pergunta relacionada à infraestrutura sustentável. As mensagens são enviadas para o modelo Gemini do Google através do backend e a resposta é exibida na interface do chat com formatação rica (negrito, itálico, links, quebras de linha). O modelo padrão é `gemini-2.5-flash`, mas você pode ajustá-lo em `app.py`.

### 📚 **Busca de Artigos**
Use a barra de pesquisa na página inicial para procurar artigos acadêmicos. O backend consulta a API OpenAlex usando seu termo de pesquisa e retorna os cinco melhores resultados. Cada resultado exibe:
- Título do artigo
- Autores
- Ano de publicação
- DOI (se disponível)
- Link direto para o artigo

### 👨‍🔬 **Busca de Especialistas**
Especialistas são pesquisadores registrados no ORCID. Quando você realiza uma busca, o backend envia sua consulta para a API pública do ORCID e retorna até cinco perfis correspondentes. Cada perfil inclui:
- Nome completo do pesquisador
- Identificador ORCID
- Link para o perfil público do pesquisador

Você pode usar os filtros acima dos resultados para mostrar apenas artigos, apenas especialistas ou ambos.

## Funcionalidades

- 🤖 **Chatbot IA**: Assistente inteligente com Google Gemini
- 📚 **Busca de Artigos**: Integração com OpenAlex API
- 👨‍🔬 **Busca de Especialistas**: Integração com ORCID API
- 🎨 **Interface Moderna**: Design responsivo e intuitivo
- 🌍 **Deploy Fácil**: Pronto para Railway, Render, Heroku
- 🔒 **Seguro**: Variáveis de ambiente para chaves de API
- ✨ **Formatação Rica**: Suporte a Markdown no chatbot
- 📱 **Responsivo**: Funciona em desktop e mobile

## Tecnologias Utilizadas

- **Backend**: Python 3.9+, Flask, Gunicorn
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **IA**: Google Gemini API
- **APIs**: OpenAlex, ORCID
- **Deploy**: Railway, Docker-ready
- **Estilo**: CSS customizado com variáveis

## Configuração da API

### Google Gemini API
1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Crie uma conta ou faça login
3. Gere uma nova chave de API
4. Configure a variável `GOOGLE_API_KEY` no seu ambiente

### APIs Públicas
- **OpenAlex**: Não requer autenticação
- **ORCID**: Usa a API pública, sem autenticação necessária

## Solução de Problemas

### Chatbot não funciona
- ✅ Verifique se `GOOGLE_API_KEY` está configurada
- ✅ Confirme que a chave da API é válida
- ✅ Verifique o console do navegador para erros

### Resultados de busca não aparecem
- ✅ Verifique sua conexão com a internet
- ✅ Tente termos de busca diferentes
- ✅ Verifique o console do navegador para erros de rede

### Erro de deploy
- ✅ Confirme que `GOOGLE_API_KEY` está configurada no serviço de deploy
- ✅ Verifique os logs de deploy para erros específicos
- ✅ Confirme que todos os arquivos estão no repositório

## Contribuição e Licença

Este projeto é fornecido para fins de demonstração e educacionais. Pull requests são bem-vindos! 

### Como contribuir:
1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

Ao contribuir, você concorda em licenciar suas contribuições sob os termos da licença MIT.

## Suporte

Para dúvidas ou problemas:

- 📝 **Abra uma issue** no GitHub
- 📖 **Consulte a documentação** das APIs utilizadas:
  - [Google Gemini API](https://ai.google.dev/gemini-api/docs)
  - [OpenAlex API](https://docs.openalex.org/)
  - [ORCID API](https://info.orcid.org/documentation/)
- 🔑 **Verifique se** a chave `GOOGLE_API_KEY` está configurada corretamente
- 🌐 **Teste localmente** antes de fazer deploy

---

**OLASIS 4.0** - Transformando a busca por conhecimento em infraestrutura sustentável! 🌱
