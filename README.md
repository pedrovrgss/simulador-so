# Simulador de Sistemas Operacionais

Projeto da disciplina de Sistemas Operacionais com foco em:

- escalonamento de processos
- gerenciamento de memoria principal
- uso de discos
- visualizacao dos estados do sistema

## Arquitetura adotada

O projeto foi estruturado em tres camadas:

- `back/app`: nucleo e API em Python
- `front/src`: interface em React
- arquivo de entrada textual para descrever processos

A decisao atual privilegia:

- Python como base principal do trabalho
- interface mais clara para demonstracao academica
- separacao entre logica de simulacao e apresentacao

Isso permite manter o motor do simulador independente da interface e, se necessario,
reaproveitar a mesma logica depois em outra UI.

## Requisitos do simulador

- 4 CPUs
- 4 discos
- 32 GiB de memoria principal compartilhada
- processos de tempo real e de usuario
- tempo real com prioridade 0, FCFS e sem preempcao
- usuario com prioridade 1, feedback de 3 filas e quantum 2
- representacao visual da memoria por blocos ocupados e livres

## Estrutura para entrega

### Backend

Arquivos principais:

- `back/app/main.py`: rotas da API usadas pela tela
- `back/app/models.py`: modelos de dados enviados entre backend e frontend
- `back/app/parser.py`: leitura e validacao da entrada textual
- `back/app/sample_data.py`: entrada padrao da demonstracao
- `back/app/memory.py`: controle dos blocos da memoria principal
- `back/app/resources.py`: controle dos discos
- `back/app/runtime.py`: estruturas internas de CPU e processo
- `back/app/admission.py`: entrada dos processos nas filas
- `back/app/scheduler.py`: escolha dos processos para as CPUs
- `back/app/execution.py`: regras de CPU, I/O, quantum e finalizacao
- `back/app/simulator.py`: motor principal da simulacao
- `back/app/snapshot.py`: conversao do estado interno para a tela
- `back/DIVISAO_BACKEND.md`: divisao sugerida para apresentacao do grupo
- `back/requirements.txt`: dependencias do backend

`back/app/main.py`

- `GET /health`: verifica se a API esta ativa
- `GET /api/snapshot`: devolve o estado real atual da simulacao
- `GET /api/default-input`: devolve a entrada padrao usada na demonstracao
- `POST /api/load`: carrega uma entrada textual e reinicia a simulacao
- `POST /api/tick`: avanca uma unidade de tempo
- `POST /api/reset`: reinicia a simulacao com a entrada atual
- `POST /api/processes/parse`: valida descritores em texto

Formatos aceitos pelo parser:

```text
[id, cpu1, io, cpu2, ram]
[id, prioridade, cpu1, io, cpu2, ram, discos]
```

Exemplo:

```text
[1, 0, 5, 0, 0, 512, 0]
[2, 1, 6, 3, 4, 1024, 1]
```

Observacao:
todos os processos chegam no tick 0. No formato minimo, o processo entra como
usuario, sem discos.

### Frontend

A interface atual mostra:

- 4 paineis de CPU
- filas centrais de escalonamento e estados
- RAM por blocos
- 4 discos
- log de eventos

Se o backend nao estiver rodando, o frontend usa um snapshot local de demonstracao.

## Execucao

### Backend

Na primeira vez, instale as dependencias dentro de um ambiente virtual:

```bash
cd back
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Depois rode a API:

```bash
cd back
./.venv/bin/uvicorn app.main:app --reload
```

### Frontend

```bash
cd front
npm run dev
```

## Pacote final

Para entregar o projeto, os arquivos importantes sao:

- `README.md`
- `LICENSE`
- `.gitignore`
- pasta `back`
- pasta `front`

Arquivos de cache, testes locais e ambientes virtuais nao fazem parte da entrega
final. Eles ficam no `.gitignore` para nao misturar codigo do projeto com
arquivos gerados pela maquina.

Se for enviar por ZIP, nao inclua `back/.venv`, `node_modules`, `dist`,
`__pycache__` ou `.pytest_cache`.
