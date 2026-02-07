# 📋 Guia Rápido de Comandos

## 🚀 Iniciar o Sistema

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Executar
python main.py
```

---

## 📈 Crescimento

### Sessão Completa
```
Menu: 1 → 1  # Balanceada (recomendado)
Menu: 1 → 2  # Agressiva
Menu: 1 → 3  # Segura
```

### Follow Específico
```
Menu: 1 → 4
URL: https://instagram.com/p/ABC123/
Quantidade: 15
```

### Unfollow
```
Menu: 1 → 5
Máximo: 30
```

### Stories
```
Menu: 1 → 6
Hashtags: tecnologia, programacao
Quantidade: 50
```

### Comentários
```
Menu: 1 → 7
URLs: url1, url2, url3
Quantidade: 5
```

### Curtidas
```
Menu: 1 → 8
Hashtag: tecnologia
Quantidade: 20
```

---

## 📤 Conteúdo

### Agendar Semana
```
Menu: 3 → 1
Pasta: ./content/images
Posts/dia: 2
```

### Agendar Manual
```
Menu: 3 → 2
Imagem: ./content/images/foto.jpg
Legenda: (deixe vazio para automático)
Data: 2024-01-20 19:00
```

### Ver Agendados
```
Menu: 3 → 3
```

### Cancelar Post
```
Menu: 3 → 4
ID: post_20240115_120000_1234
```

### Iniciar Daemon
```
Menu: 3 → 6
```

### Parar Daemon
```
Menu: 3 → 7
```

---

## 📊 Analytics

### Analisar Horários
```
Menu: 4 → 1
```

### Analisar Posts
```
Menu: 4 → 2
Quantidade: 9
```

### Relatório Completo
```
Menu: 4 → 3
```

### Exportar Horários
```
Menu: 4 → 4
```

### Estatísticas do Sistema
```
Menu: 4 → 5
```

---

## ⚙️ Configurações

### Adicionar Influenciador
```
Menu: 5 → 1
Username: programador.tv
Nicho: programacao
```

### Adicionar Concorrente
```
Menu: 5 → 2
Username: concorrente_x
```

### Adicionar à Whitelist
```
Menu: 5 → 3
Username: amigo_importante
```

### Ver Whitelist
```
Menu: 5 → 4
```

### Remover da Whitelist
```
Menu: 5 → 5
Username: usuario_a_remover
```

### Estatísticas de Seguidores
```
Menu: 5 → 6
```

---

## 🔧 Comandos Úteis

### Ver Logs
```bash
# Linux/Mac
tail -f logs/bot_$(date +%Y%m%d).log

# Windows
type logs\bot_20240115.log
```

### Backup dos Dados
```bash
# Linux/Mac
cp -r data data_backup_$(date +%Y%m%d)

# Windows
xcopy /E /I data data_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%
```

### Atualizar Dependências
```bash
pip install -r requirements.txt --upgrade
```

### Limpar Cache
```bash
# Remove cookies e sessão
rm -rf data/chrome_profile
rm -f data/session_cookies.pkl
```

---

## 🎯 Fluxo de Trabalho Recomendado

### Diário
```
1. Manhã: Menu 1 → 1 (Sessão Balanceada)
2. Tarde: Menu 4 → 3 (Ver Relatório)
3. Noite: Verificar se há posts para publicar
```

### Semanal
```
1. Segunda: Menu 3 → 1 (Agendar semana)
2. Quarta: Menu 4 → 1 (Analisar horários)
3. Sexta: Menu 5 → 6 (Ver estatísticas)
```

---

## ⚠️ Solução de Problemas

### Login Falhou
```bash
# Limpar cookies
rm -f data/session_cookies.pkl

# Tentar novamente
python main.py
```

### Chrome Não Encontrado
```bash
# Reinstalar webdriver
pip install webdriver-manager --upgrade --force-reinstall
```

### Erro de Rate Limit
```
1. Pare o sistema (Ctrl+C)
2. Aguarde 24 horas
3. Reduza limites no .env
4. Use sessão "Segura"
```
