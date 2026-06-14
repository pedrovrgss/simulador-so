# Simulador de Sistemas Operacionais

Simulador visual de escalonamento de processos, gerenciamento de memória e I/O em disco, desenvolvido como trabalho da disciplina de Sistemas Operacionais.

O backend roda em Python com FastAPI e contém toda a lógica de simulação. O frontend é uma interface React que consome a API e exibe o estado do sistema em tempo real, com controles de avanço tick a tick ou em velocidade automática.

## O que o simulador faz

- Admite processos com tempo de chegada, burst de CPU, I/O e requisito de memória
- Aloca memória RAM com First Fit em um espaço de 32768 MiB
- Carrega cada processo da "memória secundária" para a RAM via DMA (1 processo por tick)
- Escalona processos de tempo real em fila FCFS sem preempção
- Escalona processos de usuário em feedback de 3 níveis com quantum 2
- Bloqueia processos em I/O e os despacha para discos específicos (até 4 discos)
- Libera memória e discos quando o processo termina
- Permite avançar, retroceder e resetar a simulação

## Estrutura do projeto

```
simulador-so/
├── back/          backend FastAPI (motor da simulação)
├── front/         frontend React
└── examples/      arquivos de entrada prontos para uso
```

## Como executar

### Backend

Na primeira vez, crie o ambiente virtual e instale as dependências:

```bash
cd back
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Suba a API:

```bash
cd back
./.venv/bin/uvicorn app.main:app --reload
```

O backend lê automaticamente o arquivo `examples/entrada.txt` ao iniciar. Se o arquivo não existir, aparece um aviso na interface. Veja `INPUT.md` para o formato aceito.

### Frontend

```bash
cd front
npm install
npm run dev
```

Acesse `http://localhost:5173`. Se o backend não estiver rodando, a interface exibe um snapshot de demonstração estático.

## O que aparece na tela

| Painel | O que mostra |
|---|---|
| CPUs | 4 slots; processo rodando, burst restante e quantum (quando aplicável) |
| Filas | FCFS (tempo real), Feedback 1/2/3 (usuário), DMA, Aguardando memória, Finalizados |
| Log de eventos | Histórico textual de cada mudança de estado |
| Discos | 4 drives; qual processo está em I/O em cada um e quais processos residem ali |
| Memória | Mapa visual de blocos ocupados e livres na RAM |

## Arquivos de entrada prontos

A pasta `examples/` contém cenários pré-montados:

| Arquivo | Cenário |
|---|---|
| `entrada.txt` | Entrada padrão carregada automaticamente |
| `exemplo_poucos.txt` | 5 processos; fácil de acompanhar passo a passo |
| `exemplo_contencao_disco.txt` | Vários processos disputando o mesmo disco |
| `exemplo_contencao_memoria.txt` | Processos grandes que esgotam a RAM |
| `exemplo_tempo_real.txt` | Muitos processos de tempo real dominando as CPUs |
| `exemplo_multiplos_discos.txt` | Processos usando 2 discos simultaneamente |

Para trocar o cenário, renomeie ou copie o arquivo desejado para `examples/entrada.txt` e reinicie o backend.

## O que não subir para o repositório

```
back/.venv/
front/node_modules/
front/dist/
back/app/__pycache__/
```
