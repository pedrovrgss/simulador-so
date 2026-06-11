# Divisao do backend

A ideia aqui e explicar o backend como quatro frentes de trabalho que foram
juntadas no final. Cada frente tem uma parte importante da simulacao e depende
das outras para o sistema funcionar completo.

| Integrante | Frente | Arquivos principais |
|---|---|---|
| Integrante 1 | Entrada, validacao e API | `main.py`, `parser.py`, `models.py`, `sample_data.py` |
| Integrante 2 | Memoria principal e discos | `memory.py`, `resources.py` |
| Integrante 3 | Filas, estados e escalonamento | `admission.py`, `runtime.py`, `scheduler.py` |
| Integrante 4 | Execucao, motor e tela | `execution.py`, `simulator.py`, `snapshot.py` |

## Como explicar a integracao

1. A entrada chega pela API e vira uma lista de processos.
2. A admissao tenta colocar cada processo na memoria e na fila correta.
3. O escalonador escolhe quais processos vao para as CPUs.
4. A execucao avanca CPU, I/O, quantum e finalizacao.
5. O snapshot transforma tudo em dados simples para o frontend mostrar.

Essa ordem ajuda a apresentacao porque acompanha o caminho real de um processo
dentro do simulador.

## Roteiro simples para apresentar

1. Mostrar a entrada de processos.
2. Explicar que todos chegam no tempo 0.
3. Mostrar que primeiro o processo precisa entrar na memoria.
4. Mostrar que tempo real vai para FCFS e usuario vai para feedback.
5. Avancar alguns ticks e explicar CPU, quantum e I/O.
6. Mostrar memoria/discos sendo liberados quando o processo finaliza.

Nao precisa explicar cada linha do Pydantic/FastAPI. Para a professora, o mais
importante e mostrar que as regras de SO estao separadas e funcionando.

## Frente 1 - Entrada, validacao e API

Arquivos:

- `app/main.py`
- `app/parser.py`
- `app/models.py`
- `app/sample_data.py`

O que explica:

- formato da entrada;
- validacoes dos processos;
- endpoints usados pelo frontend;
- entrada padrao da demonstracao.

Resumo para falar:

> Eu fiquei com a parte que recebe a entrada, confere se os campos fazem sentido
> e abre os endpoints para o frontend controlar a simulacao.

Pontos principais:

- o backend aceita o formato minimo e o formato completo;
- todos os processos entram no tempo 0;
- se a entrada estiver errada, a API devolve erro antes de iniciar.

## Frente 2 - Memoria principal e discos

Arquivos:

- `app/memory.py`
- `app/resources.py`

O que explica:

- memoria total de 32768 MiB;
- alocacao por blocos usando First Fit;
- liberacao e juncao de blocos livres;
- reserva exclusiva dos 4 discos.

Resumo para falar:

> Eu fiquei com memoria e recursos. A memoria e uma lista de blocos, e os discos
> sao reservados de forma exclusiva para cada processo.

Pontos principais:

- a memoria tem 32768 MiB;
- a alocacao usa First Fit;
- quando um processo termina, a memoria dele e liberada;
- os discos sao recursos exclusivos durante o I/O.

## Frente 3 - Filas, estados e escalonamento

Arquivos:

- `app/admission.py`
- `app/runtime.py`
- `app/scheduler.py`

O que explica:

- admissao de processos nas filas;
- estados internos do processo;
- CPUs em execucao;
- fila FCFS de tempo real;
- feedback de usuario com 3 filas;
- quantum de 2 unidades de tempo.

Resumo para falar:

> Eu fiquei com os estados e com as filas. Tempo real entra em FCFS, e usuario
> passa pelas filas de feedback conforme consome quantum.

Pontos principais:

- tempo real usa a fila FCFS;
- usuario usa feedback com 3 niveis;
- o quantum dos usuarios e 2;
- processo bloqueado por I/O volta para a fila de usuario de maior prioridade;
- se o usuario gastar o quantum na fila 3, ele volta para a fila 1.

## Frente 4 - Execucao, motor da simulacao e tela

Arquivos:

- `app/execution.py`
- `app/simulator.py`
- `app/snapshot.py`

O que explica:

- como cada tick avanca;
- como CPU e I/O mudam os estados;
- como quantum causa preempcao;
- quando processo finaliza;
- como logs e dados sao enviados para a interface.

Resumo para falar:

> Eu fiquei com a execucao do tick. A cada unidade de tempo, o motor avanca I/O,
> avanca CPU, trata preempcao/finalizacao e monta o snapshot para a tela.

Pontos principais:

- cada clique em avancar chama um tick;
- o tick atualiza primeiro o que ja estava em andamento;
- depois o simulador tenta ocupar CPUs e discos livres;
- o snapshot e o formato final que o frontend entende.
