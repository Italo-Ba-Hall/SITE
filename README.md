# /-HALL-DEV | Plataforma Conversacional

> **Decodificando o Amanhã** - Interface conversacional para captura e qualificação de leads com IA

[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?style=flat&logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5.4-3178C6?style=flat&logo=typescript)](https://typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4.1-06B6D4?style=flat&logo=tailwindcss)](https://tailwindcss.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-Planned-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)

## 🎯 Visão Geral

Site web conversacional que abandona a navegação tradicional em favor de um **agente de IA** que guia o usuário a soluções personalizadas. Interface minimalista, moderna e dinâmica, refletindo a vanguarda tecnológica da marca.

### ✨ Características Principais

- **Interface Conversacional** - Prompt terminal interativo
- **Animações Cinematográficas** - Matrix Rain + Sequência Fibonacci SVG
- **Design Cyberpunk** - Estética futurista com paleta ciano/preto
- **Experiência Imersiva** - Transições fluidas e efeitos visuais
- **Arquitetura Desacoplada** - Frontend React + Backend FastAPI

## 🚀 Demo

A aplicação está estruturada com:
1. **Intro Animada** - Sequência SVG Fibonacci matematicamente precisa
2. **Background Dinâmico** - Matrix Rain → Circuits pulsantes
3. **Prompt Conversacional** - Interface terminal responsiva
4. **Modal de Resultados** - Exibição de conteúdo personalizado

## 📁 Estrutura do Projeto

```
/-HALL-DEV/
├── frontend/                 # React + TypeScript + TailwindCSS
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnimationIntro.tsx     # Sequência SVG Fibonacci
│   │   │   ├── BackgroundCanvas.tsx   # Matrix Rain/Circuits
│   │   │   ├── MainContent.tsx        # Logo + Prompt interface
│   │   │   └── ResultModal.tsx        # Modal de resultados
│   │   ├── App.tsx
│   │   └── index.css
│   ├── package.json
│   └── tailwind.config.js
├── backend/                  # FastAPI (em desenvolvimento)
├── site.html                # HTML original (referência)
└── CHECKLIST_PROJECT.md      # Roadmap de desenvolvimento
```

## 🛠 Tecnologias

### Frontend
- **React 18.3.1** - Biblioteca UI
- **TypeScript 5.5.4** - Tipagem estática
- **TailwindCSS 3.4.1** - Framework CSS
- **Canvas API** - Animações de background
- **SVG Animation** - Sequência matemática Fibonacci

### Backend (Planejado)
- **FastAPI** - Framework Python async
- **Pydantic** - Validação de dados
- **SQLAlchemy** - ORM database

## 🎨 Design System

```css
/* Paleta de Cores */
--cyber-blue: #00e5ff;      /* Ciano principal */
--deep-black: #080808;      /* Fundo principal */
--card-black: #010101;      /* Cards/modais */
--text-gray: #cccccc;       /* Texto secundário */

/* Tipografia */
font-family: 'Roboto Mono', monospace;
```

## 🚦 Como Executar

### Frontend (React)
```bash
cd frontend
npm install
npm start
# Acesse: http://localhost:3000
```

### Backend (Em desenvolvimento)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install fastapi uvicorn
uvicorn main:app --reload
# Acesse: http://localhost:8000
```

## 📋 Status do Desenvolvimento

### ✅ Concluído
- [x] **Estrutura do projeto** frontend/backend
- [x] **Migração HTML → React** com fidelidade 100%
- [x] **Componentes funcionais** com TypeScript
- [x] **Animações preservadas** (Matrix Rain, SVG Fibonacci)
- [x] **Interface conversacional** responsiva
- [x] **Configuração TailwindCSS** com cores personalizadas

### 🔄 Em Desenvolvimento
- [ ] **Backend FastAPI** com endpoints
- [ ] **Integração API** frontend ↔ backend
- [ ] **Lógica de sugestões** baseada em IA
- [ ] **Sistema de leads** e qualificação

### 📅 Próximos Passos
- [ ] **Testes unitários** e integração
- [ ] **Deploy** frontend (Vercel/Netlify)
- [ ] **Deploy** backend (Render/Heroku)
- [ ] **Domínio customizado** e SSL

## 🎯 Arquitetura

### Princípios de Design
- **User-First Obsession** - Experiência centrada no usuário
- **Owner Mindset** - Pensar como dono do produto
- **API-First** - Contrato da API como fonte da verdade
- **Componentes Únicos** - Responsabilidade única por componente

### Fluxo de Interação
```mermaid
graph TD
    A[Usuário digita] --> B[Frontend: PromptInput]
    B --> C[API: POST /suggest]
    C --> D[Backend: Processa texto]
    D --> E[Frontend: SuggestionsDropdown]
    E --> F[Usuário clica sugestão]
    F --> G[API: GET /content/{id}]
    G --> H[Frontend: ResultModal]
```

## 📊 Performance

### Otimizações Implementadas
- **Lazy Loading** de componentes
- **Memoização** de animações Canvas
- **CSS Transitions** hardware-accelerated
- **Event Listeners** otimizados
- **Bundle Size** < 2MB

### Métricas Alvo
- **FCP** < 1.5s (First Contentful Paint)
- **LCP** < 2.5s (Largest Contentful Paint)
- **FID** < 100ms (First Input Delay)
- **CLS** < 0.1 (Cumulative Layout Shift)

## 🤝 Contribuição

Este é um projeto proprietário. Para contribuições:

1. Seguir **owner mindset** e **user-first obsession**
2. Manter **fidelidade visual** nas alterações
3. Testar **responsividade** em diferentes dispositivos
4. Documentar **mudanças de API** adequadamente

## 📞 Contato

**Desenvolvedor:** Italo-Ba-Hall  
**Email:** italo@barra-hall-dev.com  
**Repositório:** [github.com/Italo-Ba-Hall/SITE](https://github.com/Italo-Ba-Hall/SITE)

---

**/-HALL-DEV** - *Decodificando o Amanhã através da tecnologia* 