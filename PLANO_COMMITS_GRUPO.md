# Plano de commits do grupo

Este arquivo serve para organizar os commits do projeto de forma clara.

A ideia para explicar para a professora e:

> O Pedro fez o frontend. No backend, dividimos em quatro frentes: entrada/API,
> modelos/snapshot, memoria/recursos e escalonamento/execucao. Cada integrante
> fez e commitou sua parte. Depois fizemos uma reuniao final para integrar
> backend com frontend, ajustar documentacao e corrigir detalhes visuais.

## Divisao dos commits do backend

### Membro 1 - Entrada, parser e API

Responsavel por receber a entrada, validar o formato e expor as rotas para o
frontend.

Arquivos:

```bash
back/app/main.py
back/app/parser.py
back/app/sample_data.py
back/app/__init__.py
```

Commit:

```bash
git add back/app/main.py back/app/parser.py back/app/sample_data.py back/app/__init__.py
git commit -m "Implementa entrada, parser e API do simulador"
```

### Membro 2 - Modelos, estado interno e snapshot

Responsavel pelas estruturas de dados que representam processos, CPUs e o estado
que vai para a tela.

Arquivos:

```bash
back/app/models.py
back/app/runtime.py
back/app/snapshot.py
```

Commit:

```bash
git add back/app/models.py back/app/runtime.py back/app/snapshot.py
git commit -m "Implementa modelos, estados e snapshot da simulacao"
```

### Membro 3 - Memoria, discos e admissao

Responsavel por colocar processo no sistema, alocar memoria, reservar disco e
tratar espera por recurso.

Arquivos:

```bash
back/app/memory.py
back/app/resources.py
back/app/admission.py
```

Commit:

```bash
git add back/app/memory.py back/app/resources.py back/app/admission.py
git commit -m "Implementa memoria, discos e admissao de processos"
```

### Membro 4 - Escalonamento e execucao

Responsavel pelas filas, quantum, execucao da CPU, I/O e motor principal da
simulacao.

Arquivos:

```bash
back/app/scheduler.py
back/app/execution.py
back/app/simulator.py
```

Commit:

```bash
git add back/app/scheduler.py back/app/execution.py back/app/simulator.py
git commit -m "Implementa escalonamento e execucao da simulacao"
```

## Commit final de integracao

Este commit pode ser feito no final, depois dos quatro commits do backend.

Ele representa a reuniao de integracao do grupo, ajustes finais de documentacao
e pequenos detalhes na parte visual.

Arquivos:

```bash
README.md
back/DIVISAO_BACKEND.md
front/src/App.tsx
front/src/components/CpuCard.tsx
front/src/components/DisksPanel.tsx
front/src/data/fallbackSnapshot.ts
front/src/types/simulator.ts
```

Commit:

```bash
git add README.md back/DIVISAO_BACKEND.md front/src/App.tsx front/src/components/CpuCard.tsx front/src/components/DisksPanel.tsx front/src/data/fallbackSnapshot.ts front/src/types/simulator.ts
git commit -m "Ajusta integracao final e documentacao do simulador"
```

## Passo a passo para cada integrante

Antes de tudo, entrar na pasta do projeto:

```bash
cd /home/gabriel/Documentos/testando123/simulador-so
```

Verificar os arquivos modificados:

```bash
git status
```

Configurar o nome e email do integrante que vai fazer o commit:

```bash
git config user.name "Nome do Integrante"
git config user.email "email-do-integrante@email.com"
```

Adicionar somente os arquivos da parte dele:

```bash
git add arquivo1 arquivo2 arquivo3
```

Conferir se entrou apenas o que deveria:

```bash
git diff --cached --name-only
```

Se aparecer algum arquivo errado, remover da area de commit:

```bash
git restore --staged arquivo_errado
```

Fazer o commit:

```bash
git commit -m "Mensagem do commit"
```

## Validacao final

Depois dos commits do backend e do commit final de integracao, rodar:

```bash
cd back
./.venv/bin/python -B -c "from app.simulator import SimulatorEngine; e=SimulatorEngine(); [e.tick() for _ in range(40) if not e.is_finished()]; assert e.is_finished(); print('ok')"
```

Se aparecer:

```text
ok
```

o backend conseguiu executar a simulacao ate o fim.

## O que nao commitar

Nao commitar arquivos gerados pela maquina:

```bash
back/app/__pycache__
back/.venv
node_modules
dist
.pytest_cache
```

Evitar usar:

```bash
git add .
```

O ideal e sempre adicionar os arquivos pelo nome, para nao misturar parte de
outro integrante ou arquivo gerado automaticamente.
