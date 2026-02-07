# 📱 Instagram Growth Suite

Sistema completo de automação inteligente para crescimento orgânico no Instagram.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.15+-green.svg)](https://selenium.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Funcionalidades

### 📈 Crescimento Orgânico
- ✅ **Follow em Curtidores** - Segue quem curtiu posts de influenciadores (taxa de follow-back: 30-50%)
- ✅ **Follow em Seguidores** - Segue seguidores de concorrentes do seu nicho
- ✅ **Unfollow Inteligente** - Remove quem não segue de volta (mantém ratio saudável)
- ✅ **Story Engagement** - Visualiza stories de usuários do nicho (5-10% visitam seu perfil)
- ✅ **Comentários Estratégicos** - Comenta em posts grandes para exposição massiva
- ✅ **Like por Hashtag** - Engajamento automático em posts do seu nicho

### 📤 Auto-Postagem
- ✅ **Agendamento Inteligente** - Agenda posts para os melhores horários
- ✅ **Legenda Automática** - Gera legendas usando templates
- ✅ **Daemon de Publicação** - Publica automaticamente sem intervenção
- ✅ **Suporte a Stories** - Postagem automática de stories

### 📊 Analytics
- ✅ **Análise de Horários** - Descobre quando seus seguidores estão mais ativos
- ✅ **Performance de Posts** - Analisa engajamento dos posts recentes
- ✅ **Relatórios Semanais** - Estatísticas completas de crescimento
- ✅ **Projeções** - Estimativas de crescimento futuro

### 🛡️ Segurança
- ✅ **Rate Limiting** - Limites automáticos para evitar bloqueios
- ✅ **Comportamento Humano** - Delays aleatórios e digitação simulada
- ✅ **Anti-Detecção** - Remove flags de automação do navegador
- ✅ **Whitelist** - Protege usuários importantes de unfollow
- ✅ **Persistência de Sessão** - Cookies salvos para login rápido

---

## 📋 Requisitos

- **Python 3.8+**
- **Google Chrome** instalado
- **Conta Instagram** (recomendado: Business ou Creator)
- **Sistema Operacional**: Windows, macOS ou Linux

---

## 🛠️ Instalação Passo a Passo

### 1. Clone ou Baixe o Projeto

```bash
# Clone o repositório (ou extraia o ZIP)
git clone https://github.com/seu-usuario/instagram-growth-suite.git
cd instagram-growth-suite

# Ou crie a estrutura manualmente
mkdir instagram-growth-suite
cd instagram-growth-suite
```

### 2. Crie o Ambiente Virtual

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 **Dica**: O ambiente virtual isola as dependências do projeto.

### 3. Instale as Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Isso instalará:
- `selenium` - Automação de navegador
- `webdriver-manager` - Gerenciamento automático do ChromeDriver
- `fake-useragent` - User agents rotativos
- `python-dotenv` - Variáveis de ambiente
- `colorama` - Cores no terminal
- E outras dependências...

### 4. Configure as Credenciais

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas credenciais
```

**Edite o arquivo `.env`:**

```env
# ============================================
# CREDENCIAIS DO INSTAGRAM (OBRIGATÓRIO)
# ============================================
IG_USERNAME=seu_usuario_aqui
IG_PASSWORD=sua_senha_aqui

# ============================================
# CONFIGURAÇÕES OPCIONAIS
# ============================================

# Modo headless (True = sem interface gráfica)
HEADLESS_MODE=False

# Limites de ações (ajuste conforme necessidade)
MAX_LIKES_PER_HOUR=30
MAX_FOLLOWS_PER_HOUR=20
MAX_UNFOLLOWS_PER_HOUR=25
MAX_COMMENTS_PER_HOUR=8

# Hashtags do seu nicho
TARGET_HASHTAGS=tecnologia,programacao,developer,python

# Influenciadores do seu nicho
TARGET_INFLUENCERS=programador.tv,codigofonte.tv
```

> ⚠️ **IMPORTANTE**: Nunca compartilhe o arquivo `.env`! Ele contém suas credenciais.

### 5. Prepare a Pasta de Conteúdo

```bash
# Crie a pasta para imagens
mkdir -p content/images

# Coloque suas imagens na pasta
# Formatos suportados: .jpg, .jpeg, .png
```

### 6. Verifique a Instalação

```bash
python main.py
```

Se tudo estiver configurado corretamente, você verá o banner do sistema e o menu principal.

---

## 🎯 Primeiros Passos

### 1. Login Inicial

Na primeira execução, o sistema fará login manualmente. Nas próximas vezes, usará cookies salvos.

```bash
python main.py
# Escolha qualquer opção que requeira login
```

### 2. Configure seus Alvos

```bash
# No menu principal, escolha:
# 5 → Configurações → 1 → Adicionar Influenciador Alvo

# Adicione influenciadores do SEU nicho:
# - programador.tv (nicho: programação)
# - codigofonte.tv (nicho: tecnologia)
# - Adicione os seus!
```

### 3. Execute uma Sessão de Teste

```bash
# Menu: 1 → Crescimento → 3 → Sessão Segura
# Isso executará ações conservadoras para testar
```

### 4. Analise seus Melhores Horários

```bash
# Menu: 4 → Analytics → 1 → Analisar Melhores Horários
# Isso otimizará seus horários de postagem
```

### 5. Agende Conteúdo

```bash
# Coloque imagens em content/images/
# Menu: 3 → Conteúdo → 1 → Agendar Semana
```

---

## 📖 Guia de Uso

### 🚀 Sessões de Crescimento

#### Sessão Balanceada (Recomendado)
```
Menu: 1 → 1
```
- 30 follows/hora
- 30 unfollows/hora
- 60 curtidas/hora
- 8 comentários/hora
- 50 stories/hora

#### Sessão Agressiva (Risco maior)
```
Menu: 1 → 2
```
- 50 follows/hora
- 100 curtidas/hora
- Use com cautela!

#### Sessão Segura (Contas novas)
```
Menu: 1 → 3
```
- 15 follows/hora
- Ideal para contas com menos de 1000 seguidores

### 👥 Estratégias de Follow

#### Follow em Curtidores (Mais Efetivo)
```
Menu: 1 → 4
URL do post: https://instagram.com/p/ABC123/
Quantidade: 15
```
**Taxa de follow-back: 30-50%**

#### Follow em Seguidores de Concorrentes
```
Menu: 5 → 1
Username: influenciador_do_nicho
```

### 🧹 Unfollow Inteligente

```
Menu: 1 → 5
Máximo: 30
```
- Remove apenas quem não segue de volta
- Respeita período de carência (2 dias)
- Nunca remove quem está na whitelist

### 📤 Auto-Postagem

#### Agendar Semana Completa
```bash
# 1. Coloque imagens em content/images/
# 2. Menu: 3 → 1
# 3. Informe posts por dia (recomendado: 2)
```

#### Iniciar Daemon (Publicação Automática)
```
Menu: 3 → 6
```
O sistema verificará a cada 5 minutos se há posts para publicar.

### 📊 Analytics

#### Ver Relatório Completo
```
Menu: 4 → 3
```

Exemplo de saída:
```
╔══════════════════════════════════════════════════════════╗
║           📊 RELATÓRIO DE ANALYTICS                      ║
╠══════════════════════════════════════════════════════════╣
║  🕐 MELHORES HORÁRIOS PARA POSTAR:                      ║
║  1. 20:00 - Score: 85/100 🟢 EXCELENTE                  ║
║  2. 19:00 - Score: 80/100 🟢 EXCELENTE                  ║
║  3. 13:00 - Score: 75/100 🟢 EXCELENTE                  ║
╚══════════════════════════════════════════════════════════╝
```

---

## ⚙️ Configurações Avançadas

### Ajustar Limites de Ações

Edite o arquivo `.env`:

```env
# Para contas novas (menos de 1000 seguidores)
MAX_FOLLOWS_PER_HOUR=15
MAX_LIKES_PER_HOUR=20

# Para contas estabelecidas (5000+ seguidores)
MAX_FOLLOWS_PER_HOUR=40
MAX_LIKES_PER_HOUR=80
```

### Modo Headless (Sem Interface)

```env
HEADLESS_MODE=True
```

Útil para rodar em servidores ou VPS.

### Proxy

```env
PROXY_URL=http://usuario:senha@host:porta
```

### User Agent Personalizado

```env
CUSTOM_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
```

---

## 📁 Estrutura de Arquivos

```
instagram-growth-suite/
├── 📄 main.py                    # Ponto de entrada
├── 📄 requirements.txt           # Dependências
├── 📄 .env                       # Configurações (não commitar!)
├── 📄 .env.example               # Exemplo de configurações
├── 📄 README.md                  # Este arquivo
│
├── 📁 src/                       # Código fonte
│   ├── bot.py                   # Bot principal
│   ├── config.py                # Configurações
│   ├── utils.py                 # Utilitários
│   ├── followers_manager.py     # Gestão de seguidores
│   ├── growth_engine.py         # Motor de crescimento
│   ├── content_scheduler.py     # Auto-postagem
│   └── analytics_engine.py      # Analytics
│
├── 📁 data/                      # Dados persistentes
│   ├── followers_data.json      # Histórico de follows
│   ├── analytics_data.json      # Dados de analytics
│   ├── content_schedule.json    # Posts agendados
│   ├── whitelist.json           # Usuários protegidos
│   └── growth_targets.json      # Alvos de crescimento
│
├── 📁 content/                   # Conteúdo para postar
│   └── images/                  # Imagens
│
└── 📁 logs/                      # Logs
    └── bot_20240115.log         # Log diário
```

---

## 🎯 Estratégias Recomendadas

### Para Contas Novas (0-1000 seguidores)

**Semana 1-2: Fundação**
```
- Sessão: Segura
- Posts: 1 por dia
- Follows: 15/dia
- Foco: Construir base sólida
```

**Semana 3-4: Aceleração**
```
- Sessão: Balanceada
- Posts: 2 por dia
- Follows: 25/dia
- Foco: Manter ratio saudável
```

### Para Contas em Crescimento (1000-5000)

```
- Sessão: Balanceada/Agressiva
- Posts: 2 por dia
- Follows: 30-40/dia
- Story engagement: 50/dia
- Foco: Máxima exposição
```

### Para Contas Estabelecidas (5000+)

```
- Sessão: Agressiva
- Posts: 2-3 por dia
- Follows: 40-50/dia
- Comentários estratégicos: 10/dia
- Foco: Consolidação
```

---

## ⚠️ Limites de Segurança

O sistema respeita automaticamente:

| Ação | Limite/Hora | Limite/Dia |
|------|-------------|------------|
| Follows | 20-50 | 200-400 |
| Unfollows | 25-50 | 200-400 |
| Likes | 30-100 | 300-800 |
| Comments | 8-15 | 50-100 |
| Stories | 50-100 | 500-1000 |

> 💡 **Dica**: Contas mais antigas e com mais seguidores suportam limites maiores.

---

## 🔧 Solução de Problemas

### Erro: "ChromeDriver não encontrado"

```bash
# O webdriver-manager deve instalar automaticamente
# Se falhar, instale manualmente:

# Windows
pip install webdriver-manager --upgrade

# Linux
sudo apt-get install chromium-chromedriver
```

### Erro: "Login falhou"

1. Verifique usuário e senha no `.env`
2. Desative autenticação de dois fatores temporariamente
3. Faça login manualmente no navegador primeiro
4. Aguarde 24h se a conta foi bloqueada

### Erro: "Elemento não encontrado"

Os seletores do Instagram mudam frequentemente. Atualize em `src/config.py`:

```python
SELECTORS = {
    'like_button': 'svg[aria-label="Curtir"]',  # Novo seletor
    # ...
}
```

### Conta Bloqueada

Se receber "Ação bloqueada":
1. Pare todas as automações imediatamente
2. Aguarde 24-48 horas
3. Reduza os limites no `.env`
4. Use sessão "Segura" por uma semana

---

## 📊 Resultados Esperados

Com uso consistente (5x por semana):

| Período | Novos Seguidores | Taxa de Crescimento |
|---------|------------------|---------------------|
| 1 semana | 50-150 | Base |
| 1 mês | 300-800 | 20-50% |
| 3 meses | 1500-3000 | 100%+ |
| 6 meses | 4000-8000 | 200%+ |

**Taxas de Conversão:**
- Follow em curtidores: 30-50% follow-back
- Story engagement: 5-10% visitam perfil
- Comentários estratégicos: 100%+ exposição

---

## 🛡️ Boas Práticas de Segurança

1. **Nunca compartilhe o arquivo `.env`**
2. **Use limites conservadores inicialmente**
3. **Poste conteúdo próprio regularmente**
4. **Responda comentários manualmente**
5. **Varie os horários de execução**
6. **Não execute 24/7 sem pausas**
7. **Mantenha o ratio seguidores/seguindo < 1.5**

---

## 📝 Logs

Os logs são salvos em `logs/bot_YYYYMMDD.log`:

```bash
# Ver logs em tempo real
tail -f logs/bot_$(date +%Y%m%d).log

# Ver últimas ações
tail -n 50 logs/bot_$(date +%Y%m%d).log
```

---

## 🔄 Atualização

```bash
# Backup dos dados
cp -r data data_backup_$(date +%Y%m%d)

# Atualize o código
git pull

# Reinstale dependências
pip install -r requirements.txt --upgrade
```

---

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## ⚠️ Aviso Legal

Este software é fornecido apenas para fins educacionais. O uso deste software para violar os Termos de Serviço do Instagram é de responsabilidade exclusiva do usuário. O autor não se responsabiliza por:

- Bloqueios de conta
- Perda de dados
- Violações de termos de serviço
- Quaisquer danos diretos ou indiretos

**Use por sua conta e risco.**

---

## 💬 Suporte

- 📧 Email: seu-email@exemplo.com
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/instagram-growth-suite/issues)
- 💬 Discord: [Link do Discord]

---

## ⭐ Agradecimentos

Se este projeto te ajudou, considere dar uma estrela no GitHub!

---

**Desenvolvido com ❤️ para a comunidade**
