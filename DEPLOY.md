# OLASIS 4.0 - Deploy no Railway

## 🚀 Guia de Deploy Passo a Passo

### Preparação Completa ✅
- ✅ Procfile configurado com gunicorn
- ✅ railway.json configurado
- ✅ requirements.txt atualizado
- ✅ .gitignore configurado
- ✅ Código otimizado para produção

### Passo 1: Acesse o Railway
1. Vá para: https://railway.app
2. Clique em "Start a New Project"
3. Conecte sua conta GitHub

### Passo 2: Deploy do Repositório
1. Clique em "Deploy from GitHub repo"
2. Selecione este repositório OLASIS4.0
3. O Railway detectará automaticamente que é uma aplicação Python

### Passo 3: Configure a Variável de Ambiente
1. No dashboard do Railway, clique na aba "Variables"
2. Adicione a variável:
   - Nome: `GOOGLE_API_KEY`
   - Valor: `AIzaSyCyafUCrwzxm8DCxn3XCmGULnynruRWL30`

### Passo 4: Deploy Automático
- O Railway iniciará o build automaticamente
- Aguarde alguns minutos para completar
- Você receberá uma URL pública como: `https://olasis4-production.up.railway.app`

### Passo 5: Teste a Aplicação
1. Acesse a URL fornecida
2. Teste a busca de artigos
3. Teste a busca de especialistas  
4. Teste o chatbot OLABOT

## 📋 Checklist Pré-Deploy
- [x] Gunicorn instalado
- [x] Procfile criado
- [x] requirements.txt atualizado
- [x] railway.json configurado
- [x] .gitignore atualizado
- [x] Código commitado no Git
- [x] Tratamento de erros implementado
- [x] Configuração de produção adicionada

## 🔧 Configurações Técnicas
- **Server**: Gunicorn WSGI
- **Python**: 3.12+
- **Framework**: Flask 3.0+
- **Chatbot**: Google Gemini 2.5 Flash
- **APIs**: OpenAlex + ORCID

## 🌐 URLs da Aplicação (após deploy)
- **Homepage**: `https://seu-app.up.railway.app/`
- **API Search**: `https://seu-app.up.railway.app/api/search?q=infraestrutura`
- **API Chat**: `https://seu-app.up.railway.app/api/chat`

## 🚨 Resolução de Problemas
- Se der erro 500: verifique se GOOGLE_API_KEY está configurada
- Se não carregar: aguarde alguns minutos para o build completar
- Para logs: use o dashboard do Railway > seção "Deployments"

## 💡 Próximos Passos
1. Faça o deploy seguindo os passos acima
2. Compartilhe o link público gerado
3. Monitore os logs através do dashboard Railway
4. Configure domínio customizado (opcional)
