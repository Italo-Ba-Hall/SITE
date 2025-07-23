# Checklist de Lançamento do Site /-HALL-DEV

## 1. [ ] Fase 1: Configuração e Estrutura do Projeto
1.1. [ ] Inicializar o repositório do projeto com Git (`git init`).
1.2. [ ] Criar a estrutura de pastas: `/frontend` e `/backend`.
1.3. [ ] No diretório `/frontend`, inicializar o projeto com React + TypeScript (`npx create-react-app frontend --template typescript`).
1.4. [ ] No diretório `/backend`, configurar o ambiente virtual Python (`python -m venv venv`) e instalar as dependências iniciais (Flask ou FastAPI).

## 2. [ ] Fase 2: Desenvolvimento do Frontend (React + TypeScript)
2.1. [ ] **Estrutura Base e Estilos**
2.1.1. [ ] Migrar a estrutura do `site.html` para componentes React (ex: `App.tsx`, `IntroAnimation.tsx`, `MainContent.tsx`).
2.1.2. [ ] Configurar o TailwindCSS no projeto React para aproveitar os estilos já criados.
2.1.3. [ ] Replicar as animações de fundo (Matrix Rain, Circuitos) em um componente de Canvas.
2.1.4. [ ] Implementar a animação de introdução do SVG, garantindo que ela seja executada apenas uma vez na carga inicial.

2.2. [ ] **Componentes de Interação**
2.2.1. [ ] Criar o componente do prompt de comando (`Prompt.tsx`), incluindo o `input` com o placeholder "No que você trabalha?...".
2.2.2. [ ] Criar o componente do dropdown de sugestões (`SuggestionsDropdown.tsx`), estilizado e inicialmente oculto.
2.2.3. [ ] Criar o componente do modal de resultados (`ResultModal.tsx`), capaz de receber conteúdo dinamicamente.
2.2.4. [ ] Criar o componente de navegação (`Navbar.tsx`) com os botões "Divirta-se" e "Crie".

## 3. [ ] Fase 3: Desenvolvimento do Backend (Python)
3.1. [ ] **Configuração da API**
3.1.1. [ ] Estruturar a aplicação base com Flask ou FastAPI.
3.1.2. [ ] Configurar o CORS para permitir requisições do ambiente de desenvolvimento do React.

3.2. [ ] **Criação dos Endpoints**
3.2.1. [ ] Criar o endpoint `POST /suggest` que recebe o texto do usuário e retorna uma lista de sugestões com base em palavras-chave.
3.2.2. [ ] Criar o endpoint `GET /content/<suggestion_id>` que retorna o título e o texto detalhado para ser exibido no modal.
3.2.3. [ ] Criar o endpoint `POST /contact` que recebe `nome` e `email` do formulário no modal e implementa a lógica de notificação (ex: enviar um e-mail).

## 4. [ ] Fase 4: Integração Frontend-Backend e Lógica
4.1. [ ] Conectar o `input` do `Prompt.tsx` para chamar o endpoint `/suggest` a cada alteração de texto (com debounce para evitar excesso de requisições).
4.2. [ ] Usar a resposta da API para popular e exibir o componente `SuggestionsDropdown.tsx`.
4.3. [ ] Ao clicar em uma sugestão, chamar o endpoint `/content/<suggestion_id>` e passar os dados recebidos para o `ResultModal.tsx` para exibi-lo.
4.4. [ ] Implementar a submissão do formulário de contato no modal para o endpoint `/contact`.
4.5. [ ] Adicionar estados de carregamento (loading) na interface enquanto as chamadas de API estão em andamento.
4.6. [ ] Implementar o feedback ao usuário após o envio do formulário (mensagem de sucesso ou erro).

## 5. [ ] Fase 5: Testes Finais e Lançamento
5.1. [ ] **Testes**
5.1.1. [ ] Testar o fluxo completo do usuário: digitar no prompt -> clicar na sugestão -> ver o modal -> enviar contato.
5.1.2. [ ] Testar a responsividade do site em diferentes tamanhos de tela (desktop, tablet, mobile).
5.1.3. [ ] Verificar a compatibilidade entre os principais navegadores (Chrome, Firefox, Safari).

5.2. [ ] **Lançamento (Deploy)**
5.2.1. [ ] Preparar a versão de produção do frontend (`npm run build`).
5.2.2. [ ] Escolher e configurar um serviço de hospedagem para o frontend (ex: Vercel, Netlify).
5.2.3. [ ] Escolher e configurar um serviço de hospedagem para o backend Python (ex: Render, Heroku).
5.2.4. [ ] Configurar as variáveis de ambiente em produção (principalmente a URL da API no código do frontend).
5.2.5. [ ] Fazer o deploy de ambas as aplicações.
5.2.6. [ ] Realizar um teste final no ambiente de produção para garantir que tudo está funcionando.