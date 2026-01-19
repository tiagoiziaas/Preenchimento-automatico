# 🖥️ Preenchimento Automático de Formulários Web

Automação inteligente de formulários web com mapeamento visual de campos, leitura de planilhas e execução controlada via interface desktop.

---

## 📌 Visão Geral

Este projeto é uma aplicação **desktop em Python** que permite automatizar o preenchimento e a navegação em formulários web **sem necessidade de programação por parte do usuário**.

A automação é criada de forma **visual**, clicando diretamente nos elementos da página, e os dados são extraídos de **planilhas CSV ou Excel**.

É uma solução voltada para:
- Rotinas administrativas
- Backoffice
- Cadastro de dados em sistemas web
- Processos repetitivos
- Testes manuais automatizados

---

## ✨ Funcionalidades

- 📄 Leitura de dados a partir de **CSV e XLSX**
- 🖱️ Mapeamento visual de campos e botões
- ⌨️ Preenchimento automático de formulários
- 🔁 Execução em loop (linha a linha da planilha)
- ⏱️ Controle de tempo entre ações
- 🖥️ Interface gráfica amigável (Tkinter)
- 📦 Geração de executável (.exe)

---

## 🧠 Como Funciona

### 1️⃣ Configuração
- Selecione uma planilha (CSV ou Excel)
- Informe a URL do sistema web
- Ajuste o tempo de digitação e o modo de execução

### 2️⃣ Mapeamento Visual
No navegador aberto pelo sistema:
- **Shift + Clique esquerdo** → mapear campo para preenchimento
- **Ctrl + Clique esquerdo** → mapear ação de clique (botões/links)

O sistema captura o elemento automaticamente e solicita a associação com a coluna da planilha.

### 3️⃣ Execução
- O navegador é aberto automaticamente
- Os dados são preenchidos conforme o mapeamento
- As ações são repetidas para cada linha da planilha (se habilitado)

---

## 🧩 Estrutura do Projeto

