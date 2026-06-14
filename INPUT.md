# Formato do arquivo de entrada

O simulador lê um arquivo de texto chamado `entrada.txt` na pasta `examples/`. Cada linha descreve um processo.

## Formato

```
[id, prioridade, chegada, cpu1, io, cpu2, ram, discos]
```

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | inteiro | identificador único do processo |
| `prioridade` | `0` ou `1` | `0` = tempo real (FCFS), `1` = usuário (feedback) |
| `chegada` | inteiro ≥ 0 | tick em que o processo chega ao sistema |
| `cpu1` | inteiro ≥ 1 | duração da primeira fase de CPU (obrigatório) |
| `io` | inteiro ≥ 0 | duração da fase de I/O em disco (0 = sem I/O) |
| `cpu2` | inteiro ≥ 0 | duração da segunda fase de CPU após o I/O (só faz sentido se `io > 0`) |
| `ram` | inteiro ≥ 1 | memória necessária em MiB |
| `discos` | IDs separados por espaço | discos usados na fase de I/O; use `0` se não houver I/O |

### Discos

O simulador tem 4 discos, numerados de 1 a 4. O campo `discos` lista quais drives o processo vai usar durante o I/O:

```
0       → sem I/O, nenhum disco
1       → usa apenas o disco 1
2 4     → usa os discos 2 e 4 simultaneamente
1 2 3   → usa os discos 1, 2 e 3 ao mesmo tempo
```

Um processo só entra em I/O quando **todos** os discos que ele precisa estiverem livres (aquisição atômica). Enquanto espera, fica no estado `ESPERANDO_DISCO`.

## Regras de validação

- `prioridade` deve ser `0` ou `1`
- `cpu1` deve ser maior que zero
- `cpu2` só pode ser maior que zero se `io > 0`
- se `io = 0`, o campo `discos` deve ser `0`
- se `io > 0`, o campo `discos` não pode ser `0`
- IDs de disco devem ser entre 1 e 4, sem repetição no mesmo processo
- processos de tempo real (`prioridade = 0`) não podem ter `io`, `cpu2` nem discos
- processos de tempo real não podem pedir mais de 512 MiB de RAM
- a RAM total do sistema é 32768 MiB; processos maiores que isso são rejeitados na admissão

Linhas começando com `#` são comentários e são ignoradas.

## Exemplo completo

```
# Formato: [id, prioridade, chegada, cpu1, io, cpu2, ram, discos]

[1, 0, 1, 5, 0, 0, 512, 0]
[2, 1, 2, 6, 3, 4, 1024, 1]
[3, 1, 3, 10, 0, 0, 2048, 0]
[4, 1, 4, 3, 4, 3, 4096, 2]
[5, 0, 5, 4, 0, 0, 256, 0]
[6, 1, 6, 8, 2, 2, 8192, 1 2]
```

Nesse exemplo:
- Processos 1 e 5 são tempo real: vão direto para a fila FCFS, sem I/O
- Processo 3 é usuário CPU-bound: tem `io = 0`, então não entra em I/O nem usa disco
- Processos 2 e 4 usam um disco cada durante o I/O
- Processo 6 usa os discos 1 e 2 ao mesmo tempo; só começa o I/O quando ambos estiverem livres

## Ciclo de vida de um processo

```
chegada → DMA (1 tick) → PRONTO → CPU fase 1
                                        ↓
                              sem I/O: FINALIZADO
                                        ↓
                              com I/O: aguarda disco(s)
                                        ↓
                                    I/O em disco(s)
                                        ↓
                              volta para PRONTO (fila 1)
                                        ↓
                                    CPU fase 2
                                        ↓
                                    FINALIZADO
```

- **DMA**: ao chegar, o processo tem memória alocada e aguarda 1 tick de transferência disco→RAM. Apenas 1 processo conclui DMA por tick.
- **Fila de pronto (tempo real)**: FCFS, sem preempção. Processo roda até terminar.
- **Fila de pronto (usuário)**: feedback de 3 níveis com quantum 2. Se esgotar o quantum na fila 1 ou 2, desce uma fila; se esgotar na fila 3, volta para a fila 1.
- **Após I/O**: o processo retorna sempre para a fila 1 do feedback para executar a fase 2 de CPU.

## Onde colocar o arquivo

O backend lê automaticamente `examples/entrada.txt` ao iniciar. Se o arquivo não existir, a interface mostra um aviso em amarelo no topo da tela.

Para trocar o cenário, basta substituir `examples/entrada.txt` e reiniciar o backend (`Ctrl+C` e subir novamente).
