# Guia do backend

Este arquivo explica o que cada arquivo do backend faz.

A ideia e ajudar o grupo a entender o codigo antes da apresentacao.

## Visao geral do fluxo

O simulador segue este caminho:

1. O frontend envia a entrada de processos para a API.
2. A API chama o parser para transformar o texto em processos.
3. O simulador cria os processos no tempo 0.
4. Cada processo tenta entrar na memoria.
5. Se precisar de disco, tenta reservar recurso de disco.
6. Se estiver tudo certo, entra em uma fila de pronto.
7. O escalonador escolhe processos para as 4 CPUs.
8. A cada tick, CPU, I/O, quantum e finalizacao sao atualizados.
9. O backend monta um snapshot para o frontend desenhar a tela.

Em resumo:

```text
entrada -> parser -> admissao -> memoria/discos -> filas -> execucao -> snapshot
```

## `app/main.py`

Arquivo da API.

Ele usa FastAPI para criar as rotas que o frontend chama.

Principais partes:

- cria o `app`;
- libera CORS para o frontend acessar o backend;
- cria o `engine`, que e a instancia principal do simulador;
- recebe entrada textual;
- avanca tick;
- reinicia simulacao;
- devolve o estado atual para a tela.

Rotas principais:

- `GET /health`: retorna se o backend esta ativo;
- `GET /api/snapshot`: devolve o estado atual;
- `GET /api/default-input`: devolve a entrada padrao;
- `POST /api/load`: carrega uma nova entrada;
- `POST /api/tick`: avanca uma unidade de tempo;
- `POST /api/reset`: reinicia a simulacao atual;
- `POST /api/processes/parse`: valida uma entrada sem necessariamente rodar tudo.

Como explicar:

> Esse arquivo e a porta de entrada do backend. Ele nao faz a regra do
> escalonador, so recebe pedidos do frontend e chama o motor da simulacao.

## `app/models.py`

Arquivo dos modelos de dados.

Ele define o formato dos objetos que o backend envia para o frontend.

Principais classes:

- `ProcessCard`: informacoes resumidas de um processo para aparecer na tela;
- `CpuSlot`: estado de uma CPU;
- `QueueSnapshot`: estado de uma fila;
- `MemoryBlock`: bloco visual da memoria;
- `MemorySnapshot`: estado geral da memoria;
- `DiskSnapshot`: estado de um disco;
- `EventEntry`: linha do log de eventos;
- `SimulatorSnapshot`: estado completo da simulacao;
- `ProcessDescriptor`: processo lido da entrada.

Como explicar:

> Esse arquivo organiza os dados. O frontend espera receber campos como
> `runningProcess`, `eventLog` e `totalMb`, entao os modelos ja usam esses nomes.

## `app/parser.py`

Arquivo responsavel por ler a entrada textual.

Ele aceita dois formatos:

```text
[id, cpu1, io, cpu2, ram]
[id, prioridade, cpu1, io, cpu2, ram, discos]
```

O formato minimo segue o enunciado. Nesse caso:

- prioridade vira `1`, processo de usuario;
- discos vira `0`;
- chegada e considerada no tick `0`.

O formato completo foi usado para testar tempo real e disputa por discos.

Validacoes feitas:

- prioridade precisa ser `0` ou `1`;
- CPU e I/O nao podem ser negativos;
- CPU 1 precisa ser maior que zero;
- RAM precisa ser positiva;
- discos precisa estar entre `0` e `4`;
- se I/O for `0`, CPU 2 precisa ser `0`;
- processo de tempo real nao pode passar de `512 MiB`;
- processo de tempo real nao pode pedir I/O, CPU 2 ou disco.

Como explicar:

> O parser pega cada linha da entrada, separa os campos, converte para numeros
> e valida se o processo respeita as regras do trabalho.

## `app/sample_data.py`

Arquivo com a entrada padrao da demonstracao.

Ele tambem guarda as cores usadas nos processos.

A entrada padrao tem processos variados para mostrar:

- tempo real;
- usuario;
- CPU-bound;
- processo com I/O;
- processo com CPU 1, I/O e CPU 2;
- tamanhos diferentes de memoria;
- disputa por disco;
- espera por memoria.

Como explicar:

> Esse arquivo e so a massa de teste inicial. Ele ajuda a abrir o simulador com
> um exemplo bom para demonstracao.

## `app/runtime.py`

Arquivo com os dados internos da simulacao.

Ele nao escolhe fila nem executa regra. Ele so guarda o estado atual.

Principais classes:

- `CpuRuntime`: representa uma CPU durante a simulacao;
- `ProcessRuntime`: representa um processo vivo durante a simulacao.

`ProcessRuntime` guarda coisas que mudam durante a execucao:

- estado atual;
- fila atual do feedback;
- fase atual;
- quanto falta de CPU 1;
- quanto falta de I/O;
- quanto falta de CPU 2.

Como explicar:

> O descriptor tem os dados que vieram da entrada. O runtime tem os dados que
> mudam enquanto o simulador esta rodando.

## `app/memory.py`

Arquivo que gerencia a memoria principal.

Regras implementadas:

- memoria total de `32768 MiB`;
- memoria representada por blocos;
- alocacao usando First Fit;
- liberacao quando o processo finaliza;
- juncao de blocos livres vizinhos.

Como funciona o First Fit:

1. Percorre a lista de blocos.
2. Procura o primeiro bloco livre onde o processo cabe.
3. Se couber, divide o bloco em parte ocupada e parte livre.
4. Se nao couber em nenhum, retorna falso.

Como explicar:

> A memoria nao e so um contador. Ela e uma lista de segmentos. Quando um
> processo entra, ele ocupa um trecho. Quando sai, o trecho fica livre e e unido
> com outros blocos livres se estiverem lado a lado.

## `app/resources.py`

Arquivo que controla os 4 discos.

No nosso simulador, os discos sao recursos de I/O.

O que ele faz:

- cria 4 discos;
- reserva discos para um processo;
- impede dois processos de usarem o mesmo disco;
- libera discos quando o processo finaliza;
- monta os dados dos discos para aparecerem na tela.

Importante:

O disco aqui nao representa memoria secundaria/swap. Ele representa recurso de
I/O, conforme o enunciado.

Como explicar:

> Se o processo pediu disco e existe disco livre, ele reserva. Se nao existir,
> o processo fica esperando recurso. Quando o processo finaliza, os discos dele
> sao liberados.

## `app/scheduler.py`

Arquivo do escalonador.

Ele guarda as filas de processos prontos.

Filas:

- `real_time`: fila FCFS dos processos de tempo real;
- `user_queues[0]`: fila de usuario de maior prioridade;
- `user_queues[1]`: fila intermediaria;
- `user_queues[2]`: fila de menor prioridade.

Regras:

- tempo real sempre tem prioridade sobre usuario;
- tempo real usa FCFS;
- usuario usa feedback com 3 filas;
- quando nao ha tempo real, procura usuario em U0, depois U1, depois U2.

Como explicar:

> Esse arquivo decide quem e o proximo processo pronto. Ele nao executa CPU, so
> entrega o proximo PID para a CPU livre.

## `app/admission.py`

Arquivo de admissao dos processos.

Ele e responsavel por colocar o processo dentro do sistema.

Fluxo:

1. Cria o `ProcessRuntime`.
2. Tenta alocar memoria.
3. Se nao couber, coloca em `waiting_memory`.
4. Se couber, tenta reservar discos.
5. Se nao tiver disco, coloca em `waiting_resource`.
6. Se tiver tudo, coloca na fila de pronto.

Tambem tenta acordar processos em espera quando memoria ou disco ficam livres.

Como explicar:

> Esse arquivo e o despachante/admissao. Ele confere se o processo pode entrar
> no sistema antes de deixar o escalonador escolher esse processo.

## `app/execution.py`

Arquivo que executa as regras a cada tick.

Principais funcoes:

- `despachar_cpus_livres`: coloca processos prontos em CPUs livres;
- `avancar_io`: diminui o tempo restante de I/O;
- `avancar_cpus`: diminui o tempo restante de CPU;
- `tratar_fim_da_fase_cpu`: decide se vai para I/O ou finaliza;
- `preemptar_usuario`: troca o usuario de fila quando acaba o quantum;
- `finalizar_processo`: libera memoria e discos.

Regras importantes:

- tempo real nao tem quantum;
- usuario tem quantum 2;
- se usuario acaba o quantum na fila 1 ou 2, desce uma fila;
- se usuario acaba o quantum na fila 3, volta para a fila 1;
- se termina CPU 1 e tem I/O, vai para bloqueado;
- depois do I/O, o usuario volta para a fila 1 para executar CPU 2;
- se termina CPU 2 ou nao tem I/O, finaliza.

Como explicar:

> Esse arquivo e onde o tempo realmente anda. Cada tick tira uma unidade da CPU
> ou do I/O e decide a proxima acao do processo.

## `app/simulator.py`

Arquivo do motor principal da simulacao.

Ele junta todos os outros modulos.

Responsabilidades:

- guardar o estado geral;
- carregar entrada;
- resetar simulacao;
- avancar tick;
- verificar se a simulacao acabou;
- registrar logs;
- gerar snapshot para a tela.

Ordem do tick:

1. incrementa o relogio;
2. avanca I/O;
3. avanca CPUs;
4. tenta acordar processos esperando memoria ou recurso;
5. coloca processos prontos em CPUs livres;
6. devolve o snapshot.

Como explicar:

> O simulador e o coordenador. Ele nao guarda todas as regras dentro dele. Ele
> chama admissao, execucao, memoria, recursos e escalonador na ordem certa.

## `app/snapshot.py`

Arquivo que transforma o estado interno em dados para o frontend.

Ele monta:

- lista de CPUs;
- filas;
- memoria;
- discos;
- log de eventos.

Por que existe:

O backend usa estruturas internas como `ProcessRuntime`, `CpuRuntime` e filas.
O frontend precisa receber dados simples para desenhar a tela.

Como explicar:

> Esse arquivo e um adaptador. Ele pega o estado real da simulacao e transforma
> em um formato facil para a interface mostrar.

## `app/__init__.py`

Arquivo simples que marca `app` como pacote Python.

Como explicar:

> Esse arquivo so ajuda o Python a reconhecer a pasta `app` como modulo do
> backend.

## Como apresentar o codigo em ordem

Uma ordem boa para apresentar:

1. `main.py`: mostrar as rotas.
2. `parser.py`: mostrar como a entrada vira processo.
3. `models.py`: mostrar os dados principais.
4. `memory.py`: mostrar alocacao por blocos.
5. `resources.py`: mostrar discos.
6. `scheduler.py`: mostrar FCFS e feedback.
7. `admission.py`: mostrar entrada no sistema.
8. `execution.py`: mostrar tick, CPU, I/O e quantum.
9. `simulator.py`: mostrar o motor chamando tudo.
10. `snapshot.py`: mostrar como vai para o frontend.

## Frase curta para explicar o backend

> O backend recebe a entrada dos processos, valida as regras, aloca memoria,
> reserva recursos, escalona nas 4 CPUs, simula CPU/I/O por tick e envia para o
> frontend um snapshot completo do estado atual.

## Pontos que podem gerar pergunta

### Disco e memoria secundaria

No projeto, os 4 discos sao tratados como recursos de I/O.

Nao implementamos swap nem memoria secundaria. Quando um processo nao cabe na
RAM, ele fica em `Aguardando memoria`.

### Threads

O simulador poderia usar threads para separar tarefas, por exemplo:

- uma thread para a interface;
- uma thread para o motor da simulacao;
- threads para simular I/O em paralelo.

Mas neste trabalho usamos tick manual para deixar a demonstracao mais previsivel
e facil de acompanhar.

### Chegada dos processos

Todos os processos chegam no tick `0`.

Isso simplifica a demonstracao e esta documentado no README. O foco fica no
escalonamento, memoria, I/O e recursos.
