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

## Estrutura atual

### Backend

`back/app/main.py`

- `GET /health`: verifica se a API esta ativa
- `GET /api/snapshot`: devolve um snapshot de demonstracao para a interface
- `POST /api/processes/parse`: faz o parser inicial de descritores em texto

Formato inicial do parser:

```text
pid;nome;classe;chegada;prioridade;memoria_mb;cpu1;disco;io;cpu2
```

Exemplo:

```text
TR-01;Controle de voo;TR;0;0;256;5;-;-;-
U-07;Editor;U;1;1;2048;3;2;4;2
```

Observacao:
esse formato foi colocado como ponto de partida e pode ser adaptado rapidamente
quando o formato definitivo da disciplina estiver fechado.

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

```bash
cd back
python -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd front
npm run dev
```

## Proximos passos sugeridos

1. Implementar o modelo interno de processo e estados.
2. Criar o relogio da simulacao e o avanco por unidade de tempo.
3. Implementar o escalonador de tempo real.
4. Implementar o feedback de 3 filas para usuario.
5. Integrar alocacao e liberacao de memoria por blocos.
6. Integrar E/S em disco e retorno do processo para pronto.
