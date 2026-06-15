# Backend — lógica e estrutura

Este arquivo explica o que cada módulo do backend faz, por que ele existe e quais decisões de design foram tomadas.

## Fluxo geral

```
entrada.txt → parser → simulator.load()
                              ↓
                         tick a tick:
                         admitir_chegadas
                         avancar_io
                         avancar_cpus
                         avancar_carregamento_memoria
                         tentar_processos_em_espera
                         despachar_cpus_livres
                              ↓
                          snapshot → frontend
```

---

## `main.py` — API e ponto de entrada

Expõe a API REST que o frontend consome. Usa FastAPI com CORS liberado para `localhost`.

**Por que FastAPI:** tipagem automática via Pydantic, validação de resposta e documentação gerada em `/docs` sem custo extra.

Ao iniciar, lê `examples/entrada.txt` automaticamente e carrega no engine. Se o arquivo não existir, salva um aviso que aparece como banner na interface.

Rotas:

| Rota | Método | O que faz |
|---|---|---|
| `/health` | GET | confirma que o backend está no ar |
| `/api/snapshot` | GET | devolve o estado atual da simulação |
| `/api/tick` | POST | avança 1 unidade de tempo e devolve o novo estado |
| `/api/reset` | POST | reinicia a simulação com a entrada atual |
| `/api/step-back` | POST | desfaz o último tick (histórico em memória) |
| `/api/load` | POST | carrega uma nova entrada textual |
| `/api/processes/parse` | POST | valida uma entrada sem rodar a simulação |

---

## `models.py` — contratos entre backend e frontend

Define os modelos Pydantic que saem pela API. O frontend TypeScript espera exatamente esses campos.

**Por que separar de `runtime.py`:** as estruturas internas da simulação (`ProcessRuntime`, `CpuRuntime`) mudam durante a execução e carregam dados que o frontend não precisa ver. Os modelos daqui são o contrato público; o runtime é detalhe de implementação.

Principais classes:

- `ProcessCard` — representação resumida de um processo para aparecer em qualquer painel da tela
- `CpuSlot` — estado de uma CPU: processo rodando, quantum restante, burst restante
- `QueueSnapshot` — estado de uma fila: lista de processos e quais estão ativos
- `DiskSnapshot` — estado de um disco: processo em I/O, processos na RAM, processos só em disco
- `MemoryBlock` / `MemorySnapshot` — blocos da RAM com endereço, tamanho e dono
- `SimulatorSnapshot` — objeto raiz que o frontend recebe a cada tick; contém tudo acima mais o log de eventos e avisos

---

## `parser.py` — leitura e validação da entrada

Transforma o texto do arquivo de entrada em uma lista de `ProcessDescriptor`.

Aceita o formato de 8 campos: `[id, prioridade, chegada, cpu1, io, cpu2, ram, discos]`. Linhas com `#` são ignoradas.

**Por que validar aqui e não no simulador:** erros de entrada devem ser detectados antes de qualquer simulação rodar. O parser lança `DescriptorFormatError` com número de linha e motivo, que a API devolve como HTTP 422 para o frontend exibir ao usuário.

Validações notáveis:

- tempo real (`prioridade = 0`) não pode ter I/O, CPU 2 nem discos — essas fases não existem para FCFS
- tempo real não pode pedir mais de 512 MiB — reserva de memória para processos críticos
- `cpu2 > 0` exige `io > 0` — não há segunda fase de CPU sem I/O entre elas
- IDs de disco devem ser 1–4 sem duplicata no mesmo processo
- `io = 0` exige `discos = 0` e vice-versa

O campo `discos` aceita `"0"` (sem disco), `"2"` (disco 2) ou `"1 3"` (discos 1 e 3 simultaneamente).

---

## `models.py` → `ProcessDescriptor`

Resultado do parser: dados imutáveis vindos do arquivo de entrada. Não muda durante a simulação. É a "especificação" do processo; `ProcessRuntime` é a instância viva.

---

## `runtime.py` — estado interno durante a simulação

Contém as duas estruturas que mudam tick a tick:

**`ProcessRuntime`**: tudo que varia enquanto o processo existe no sistema.

- `phase`: qual das fases o processo está executando (`fase_cpu_1`, `fase_io`, `fase_cpu_2`, `cpu_bound`)
- `cpu1_remaining`, `io_remaining`, `cpu2_remaining`: contadores decrementados a cada tick
- `queue_level`: nível atual no feedback (0, 1 ou 2); reseta para 0 após I/O
- `state`: string do estado atual para o log e para a tela
- `home_disk_id`: disco "de origem" do processo (round-robin entre os 4), usado só para exibição

**`CpuRuntime`**: qual processo está na CPU e quanto de quantum sobrou. `quantum_left = None` para tempo real (sem quantum).

**Por que separar de `ProcessDescriptor`:** o descriptor vem do arquivo e não muda; o runtime acumula o estado mutável. Isso torna o `copy.deepcopy` do histórico (step-back) mais seguro e o código mais fácil de entender.

---

## `memory.py` — gerenciamento da RAM

Implementa alocação e liberação de memória com First Fit sobre uma lista de blocos contíguos.

**Estrutura:** a RAM é uma lista de `MemoryBlock`, cada um com endereço de início, tamanho e dono. Inicialmente é um único bloco livre de 32768 MiB.

**`allocate(pid, size)`:** percorre os blocos em ordem, acha o primeiro livre onde o processo cabe, divide em "ocupado + livre" e retorna `True`. Se nenhum bloco serve, retorna `False` e o processo vai para `waiting_memory`.

**`free(pid)`:** marca o bloco do processo como livre e faz merging com vizinhos livres adjacentes para evitar fragmentação acumulada.

**Por que First Fit:** é o algoritmo exigido pelo enunciado e o mais simples de implementar corretamente com uma lista de blocos.

---

## `resources.py` — controle dos discos

Gerencia os 4 drives de I/O.

**`Disk`**: dataclass com `id` e `io_pid` (qual processo está usando, ou `None` se livre).

**`DiskManager`**:

- `can_acquire(disk_ids)` — verifica se todos os discos da lista estão livres
- `acquire_io(pid, disk_ids)` — marca todos os discos com o PID do processo
- `release_io(pid)` — libera todos os discos que estavam com esse PID
- `active_io_pid(disk_id)` — retorna quem está usando determinado disco (para o snapshot)

**Decisão de design — aquisição no momento do I/O, não na admissão:** os discos são reservados quando o processo termina a CPU fase 1 e vai entrar em I/O, não quando chega ao sistema. Isso reflete o comportamento real de um SO: o processo só precisa do disco durante a transferência. Se o disco estiver ocupado, o processo vai para `blocked_disk` com estado `ESPERANDO_DISCO` e é desbloqueado automaticamente assim que o disco libera.

**Aquisição atômica de múltiplos discos:** se o processo precisa de mais de um disco, todos precisam estar livres ao mesmo tempo. Isso evita deadlock por aquisição parcial (um processo segura disco 1 esperando disco 2 enquanto outro segura disco 2 esperando disco 1).

---

## `admission.py` — entrada dos processos no sistema

Controla as três etapas de admissão: chegada, alocação de memória e DMA.

**`admitir_chegadas(sim)`:** a cada tick, verifica quais processos do `pending_processes` têm `arrival_time == clock` e os admite.

**`admitir_processo(sim, process)`:** tenta alocar memória. Se não couber, coloca em `waiting_memory`. Se couber, inicia o DMA.

**`_iniciar_dma_memoria(sim, process)`:** memória alocada, processo entra em `loading_memory` com estado `CARREGANDO_MEMORIA`. O DMA representa a transferência disco→RAM: o processo não pode executar enquanto não terminar.

**`avancar_carregamento_memoria(sim)`:** conclui o DMA de **apenas um processo por tick**, o primeiro da fila. Isso serializa a transferência, simulando que há um canal DMA compartilhado. Sem isso, com vários processos chegando no mesmo tick, todos completariam o DMA simultaneamente e entrariam na fila de prontos juntos, tornando a fase "somente em disco" invisível na interface.

**`tentar_processos_em_espera(sim)`:** quando memória libera (processo finaliza), tenta realocar os processos em `waiting_memory` em ordem de chegada.

---

## `scheduler.py` — filas de prontos

Mantém as filas e decide qual processo vai para qual CPU.

**Filas:**

- `real_time`: deque FCFS para processos com `prioridade = 0`
- `user_queues[0..2]`: três deques para o feedback de usuário

**`next_process(cpu)`:** sempre verifica tempo real primeiro. Se houver algum processo na fila FCFS, ele tem prioridade absoluta sobre qualquer usuário. Entre usuários, percorre as filas em ordem (0 → 1 → 2).

**`add_ready(pid, priority, queue_level)`:** coloca o processo na fila correta. Tempo real vai para `real_time`; usuário vai para `user_queues[queue_level]`.

**Por que não há fila global de prioridade:** FCFS e feedback têm semânticas diferentes (FCFS não tem quantum, feedback tem). Manter filas separadas facilita aplicar as regras certas sem condicionais espalhados pelo código.

---

## `execution.py` — regras de execução por tick

Contém as funções que avançam o estado da simulação a cada unidade de tempo.

**`despachar_cpus_livres(sim)`:** para cada CPU livre, pede o próximo processo ao scheduler e o coloca na CPU.

**`avancar_cpus(sim)`:** decrementa CPU de todos os processos em execução. Se o processo de tempo real terminar o burst, finaliza. Se o usuário terminar o burst ou o quantum, chama `tratar_fim_da_fase_cpu` ou `preemptar_usuario`.

**`preemptar_usuario(sim, cpu, process)`:** quantum esgotado. Se estiver nas filas 0 ou 1, desce uma fila; se estiver na fila 2, volta para a fila 0 (rotação). O processo volta para o scheduler e a CPU fica livre.

**`tratar_fim_da_fase_cpu(sim, cpu, process)`:** CPU chegou a zero. Se for tempo real, ou fase 2, ou sem I/O, finaliza. Caso contrário, tenta adquirir os discos:
- se conseguir: vai para `blocked_io` com estado `BLOQUEADO_IO`
- se não conseguir: vai para `blocked_disk` com estado `ESPERANDO_DISCO`

**`avancar_io(sim)`:** decrementa I/O de todos em `blocked_io`. Quando termina, libera os discos, muda para `fase_cpu_2`, volta para a fila 0 do feedback e chama `_tentar_bloqueados_disco`.

**`_tentar_bloqueados_disco(sim)`:** sempre que um disco libera (fim de I/O ou fim de processo), varre `blocked_disk` e tenta mover processos para `blocked_io` se os discos deles estiverem livres agora.

**`finalizar_processo(sim, process)`:** libera a memória do processo, libera seus discos e marca como `FINALIZADO`. Chama `_tentar_bloqueados_disco` porque a liberação do disco pode desbloquear outro processo.

---

## `simulator.py` — motor e estado global

É o coordenador: não contém regras de negócio, apenas organiza a execução.

**Estado que mantém:**

- `processes`: dicionário `pid → ProcessRuntime`
- `loading_memory`: PIDs em DMA (aguardando transferência)
- `waiting_memory`: PIDs aguardando RAM livre
- `blocked_io`: PIDs em I/O ativo
- `blocked_disk`: PIDs aguardando disco ficar livre
- `finished` / `rejected`: PIDs finalizados e rejeitados
- `clock`: tick atual
- `history`: pilha de snapshots anteriores para o step-back
- `warnings`: avisos que aparecem no banner da interface

**`tick()`:** ordem de execução:
1. incrementa o clock
2. admite processos com `arrival_time == clock`
3. avança I/O (`avancar_io`)
4. avança CPUs (`avancar_cpus`)
5. conclui 1 DMA (`avancar_carregamento_memoria`)
6. tenta acordar processos em `waiting_memory`
7. despacha CPUs livres

**`is_finished()`:** verdadeiro quando não há nenhum processo em nenhuma fila ativa (loading, waiting, blocked, prontos, em CPU) e todos os pending já chegaram.

**`_save_state` / `_restore_state`:** usados pelo step-back. Salva `copy.deepcopy` do estado antes de cada tick; restaura ao receber `/api/step-back`. O histórico é limitado (últimos 50 ticks) para não consumir memória indefinidamente.

---

## `snapshot.py` — tradução do estado interno para o frontend

Converte as estruturas do simulador (`ProcessRuntime`, `CpuRuntime`, filas, etc.) no `SimulatorSnapshot` que a API serializa como JSON.

**Por que existe:** o frontend não deve conhecer os tipos internos. Se a implementação mudar, o contrato externo (snapshot) pode permanecer estável. É a separação entre modelo de domínio e modelo de apresentação.

**`_disk_snapshots`:** para cada disco, descobre qual processo está em I/O (`active_io_pid`), quais processos têm RAM alocada nesse disco (`inMemory`) e quais ainda estão só em disco secundário (`onDiskOnly`). O `home_disk_id` de cada processo determina em qual card de disco ele aparece.

**`_queue_snapshots`:** monta as filas visíveis. A fila "DMA" exibe `blocked_io + blocked_disk` (todos os processos que saíram da CPU para operações de I/O ou disco). A fila "Aguardando memória" exibe `waiting_memory + loading_memory`.

**`_queue_label`:** gera o rótulo individual de cada processo dentro de uma fila (ex: "Disco 1 e 2", "Aguardando disco", "Fila 1").

---

## `sample_data.py` — dados auxiliares

Contém apenas dois itens:

- `PROCESS_COLORS`: lista de 16 cores hexadecimais atribuídas aos processos em round-robin pelo índice
- `DEFAULT_INPUT`: entrada de demonstração usada como fallback se `examples/entrada.txt` não existir (não é mais carregada no `main.py` por padrão; o arquivo externo tem precedência)
