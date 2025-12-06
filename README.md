# Trabalho Prático - Programação Matemática

## ALWABP - Assembly Line Worker Assignment and Balancing Problem

Este repositório contém duas abordagens para resolver o **ALWABP**:

1. **Modelagem Exata (Gurobi)** - Programação Linear Inteira Mista
2. **Meta-heurística RKO-BRKGA** - BRKGA + Busca Local

---

## 📁 Estrutura do Projeto

```
trabalho_pratico_PM/
├── Instances/              # Instâncias de teste do ALWABP
├── Program/                # Código fonte
│   ├── Problem/           # SPECIFIC_CODE - Código específico do ALWABP
│   │   ├── alwabp_instance.py    # Estrutura de dados do problema
│   │   ├── alwabp_solution.py    # Representação de soluções
│   │   ├── decoder.py            # Decodificador de chaves aleatórias
│   │   └── read_instance.py      # Parser de entrada
│   ├── MH/                # GENERAL_CODE - Meta-heurística
│   │   ├── brkga.py              # Algoritmo BRKGA
│   │   ├── local_search.py       # Busca local
│   │   └── rko_brkga.py          # Integração RKO-BRKGA
│   └── Main/              # Ponto de entrada
│       └── main.py               # Função principal
├── Results/               # Arquivos de saída (JSON)
├── run.py                 # Script de execução
├── modelagem.py           # Modelo Gurobi (exato)
├── METODOLOGIA.md         # Documentação técnica
└── README.md              # Este arquivo
```

---

## 🚀 Uso

### 1. Modelo Exato (Gurobi)

```bash
python3 modelagem.py < alwabp/1_hes
```

**Saída**: Grafo DOT com solução ótima e tempo de ciclo

**Nota**: Requer licença do Gurobi. A licença acadêmica gratuita tem limite de 2000 variáveis/restrições.

### 2. Meta-heurística (RKO-BRKGA)

#### Uso Básico
```bash
python3 run.py < Instances/10_hes
```

#### Uso Completo (com arquivo de saída)
```bash
python3 run.py Results/solution.json < Instances/10_hes
```

#### Com Múltiplas Réplicas (recomendado)
```bash
python3 run.py Results/solution.json --seed 42 --replicas 5 < Instances/10_hes
```

#### Parâmetros Configuráveis
```bash
python3 run.py Results/solution.json \
  --seed 42 \
  --replicas 10 \
  --pop-size 200 \
  --generations 300 \
  --elite 0.25 \
  --verbose \
  < Instances/10_hes
```

**Parâmetros disponíveis**:
- `--seed SEED`: Semente do gerador aleatório
- `--replicas N`: Número de réplicas (mínimo 5 para resultados confiáveis)
- `--pop-size SIZE`: Tamanho da população
- `--generations GEN`: Número de gerações
- `--elite PERC`: Percentual de elite (0.0-1.0)
- `--mutant PERC`: Percentual de mutantes (0.0-1.0)
- `--elite-bias BIAS`: Viés de elite no crossover (0.5-1.0)
- `--ls-freq FREQ`: Frequência de busca local (gerações)
- `--ls-iters ITERS`: Iterações de busca local
- `--verbose`: Modo verboso

**Saídas**:
- **stdout**: Melhor tempo de ciclo encontrado
- **stderr**: Estatísticas (média, desvio, tempo de execução)
- **JSON**: Solução completa com parâmetros e estatísticas

---

## 📝 Formato de Entrada

O formato segue o padrão das instâncias ALWABP:

```
n                          # número de tarefas
t11 t12 ... t1k           # tempos de execução (matriz n×k)
t21 t22 ... t2k
...
tn1 tn2 ... tnk
i j                        # precedências (i deve vir antes de j)
i j
...
-1 -1                      # fim das precedências
```

- `n`: número de tarefas
- `k`: número de trabalhadores (inferido da matriz)
- `Inf`: indica incompatibilidade trabalhador-tarefa
- Índices 1-based na entrada (convertidos para 0-based internamente)

**Exemplos**: `Instances/10_hes`, `Instances/10_ros`, etc.

---

## 🎯 Problema ALWABP

O problema consiste em:

- **Atribuir** trabalhadores a estações de trabalho
- **Atribuir** tarefas a estações
- **Minimizar** o tempo de ciclo (gargalo)

**Restrições**:
- Cada tarefa executada em exatamente uma estação
- Cada trabalhador em exatamente uma estação
- Cada estação com exatamente um trabalhador
- Precedências entre tarefas respeitadas
- Incompatibilidades trabalhador-tarefa respeitadas

---

## 🔧 Dependências

```bash
pip install numpy gurobipy
```

**Nota**: `gurobipy` é opcional (apenas para `modelagem.py`)

---

## 📊 Resultados

### Exemplo - Instância 1_hes (28 tarefas, 4 trabalhadores)

**Execução com 5 réplicas (seed=42)**:
```bash
python3 run.py Results/solution.json --seed 42 --replicas 5 < Instances/10_hes
```

| Método | Tempo de Ciclo | Desvio | Tempo Exec. | Factível |
|--------|---------------|--------|-------------|----------|
| Gurobi (ótimo) | 94.00 | - | ~1s | ✓ |
| RKO-BRKGA (melhor) | 102.00 | - | ~8s | ✓ |
| RKO-BRKGA (média) | 102.60 | 0.49 | ~8s | ✓ |

**Gap**: 9.1% do ótimo

---

## 📋 Conformidade com Regras

✅ **Regra 7**: Aceita instância via stdin, imprime solução em stdout  
✅ **Regra 8**: Parâmetros configuráveis via linha de comando, primeiro argumento é arquivo de saída  
✅ **Regra 6**: Suporte a múltiplas réplicas com sementes diferentes (média de N execuções)  
✅ **Regra 4**: Documentação completa em `METODOLOGIA.md`  
✅ **Regra 5**: Arquivo JSON com todos os parâmetros, sementes e estatísticas  
✅ **Regra 9**: Código original, referências citadas em `METODOLOGIA.md`

---

## 👤 Autor

Paulo H. Silveira

## 📅 Data

Dezembro de 2025
