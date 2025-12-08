# Trabalho Prático - Programação Matemática

## ALWABP - Assembly Line Worker Assignment and Balancing Problem

Este repositório contém duas abordagens para resolver o **ALWABP** (Assembly Line Worker Assignment and Balancing Problem):

1. **Modelagem Exata (Gurobi)** - Programação Linear Inteira Mista
2. **Meta-heurística RKO-BRKGA** - BRKGA + Busca Local

## 📁 Estrutura do Projeto

```
trabalho_pratico_PM/
├── Instances/ 
│   ├── 1_hes, 2_hes... 
│   ├── 1_ros, 2_ros... 
│   ├── 1_ton, 2_ton...  
│   └── 1_wee, 2_wee... 
├── Program/
│   ├── Problem/ 
│   │   ├── alwabp_instance.py 
│   │   ├── alwabp_solution.py 
│   │   ├── decoder.py
│   │   ├── repair.py
│   │   └── read_instance.py 
│   ├── MH/
│   │   ├── brkga.py
│   │   ├── local_search.py 
│   │   └── rko_brkga.py
│   └── Main/
│       └── main.py
├── Results/
├── run.py
├── modelagem.py
└── README.md
```

---

## 🚀 Como Executar

### 1. Modelo Exato (Gurobi)

```bash
python3 modelagem.py < Instances/1_hes
```

**Saída**: Grafo DOT mostrando estações, trabalhadores, tarefas e tempo de ciclo ótimo.

```
digraph Resultado {
  station1 [label="Estação 1\nTrabalhador: 3\nCarga: 93.00"];
  task1 [label="Tarefa 1"];
  station1 -> task1;
  ...
  C[label="Ciclo ótimo: 94.00"];
  Time[label="Tempo: 0.22s"];
}
```

**Limitações**:
- Requer licença Gurobi (acadêmica ou comercial)
- Licença acadêmica gratuita: limite de **2000 variáveis**
- Instâncias grandes (ex: 72_ton) excedem este limite

---

### 2. Meta-heurística (RKO-BRKGA)

#### 📌 Uso Básico (modo silencioso)
```bash
python3 run.py < Instances/2_ros
# Saída: 30.00
```

#### 📌 Com Modo Verbose (recomendado)
```bash
python3 run.py --seed 42 --verbose < Instances/2_ros
```

**Saída verbose inclui**:
- Progresso geração por geração
- Aplicações de busca local
- **Tabela de Resultados Computacionais**:
  - Solução Inicial (SI)
  - Solução Final (SF)
  - Desvio SI-SF (%)
  - Desvio SF-Ótimo (%) - se `--optimal` fornecido
  - Tempo Computacional (s)

#### 📌 Múltiplas Réplicas (recomendado para análise estatística)
```bash
python3 run.py --seed 42 --replicas 5 --verbose < Instances/1_hes
```

**Saída com réplicas**:
```
==========================================================================================
TABELA CONSOLIDADA - RESULTADOS COMPUTACIONAIS (5 réplicas)
==========================================================================================

Réplica    Seed      SI        SF     SI-SF(%)   SF-Ótimo(%)   Tempo(s)   Factível
------------------------------------------------------------------------------------------
    1        42    157.00    105.00     33.12         N/A         4.42      True
    2      1337    142.00     97.00     31.69         N/A         4.35      True
    3      7777    151.00    102.00     32.45         N/A         4.28      True
    4      9999    148.00    101.00     31.76         N/A         4.31      True
    5     12345    155.00    107.00     30.97         N/A         4.39      True
------------------------------------------------------------------------------------------
Média               150.60    102.40     32.00         N/A         4.35      
Desvio                5.79      3.85      0.87         N/A         0.05      
Melhor                  -      97.00        -          N/A           -       
==========================================================================================
```

#### 📌 Com Valor Ótimo (para calcular gap)
```bash
python3 run.py --seed 42 --optimal 94 --verbose < Instances/1_hes
```

**Gap SF-Ótimo será calculado**:
```
Desvio SF-Ótimo (%)                                11.70
...
Fórmula SF-Ótimo: 100 × (105.00 - 94.00) / 94.00 = 11.70%
```

#### 📌 Salvar Solução em JSON
```bash
python3 run.py Results/solution.json --seed 42 --replicas 5 < Instances/1_hes
```

**JSON gerado** (`Results/solution.json`):
```json
{
  "cycle_time": 97.0,
  "feasible": true,
  "task_assignment": [0, 1, 2, ...],
  "worker_assignment": [3, 1, 2, 0],
  "station_times": [93.0, 94.0, 92.0, 94.0],
  "instance": {...},
  "parameters": {...},
  "statistics": {
    "seeds": [42, 1337, 7777, 9999, 12345],
    "cycle_times": [105.0, 97.0, 102.0, 101.0, 107.0],
    "mean": 102.4,
    "std": 3.85,
    "min": 97.0,
    "max": 107.0
  }
}
```

---

## Parâmetros da Meta-heurística

### Parâmetros Principais

| Parâmetro | Flag | Padrão | Descrição |
|-----------|------|--------|-----------|
| Semente | `--seed SEED` | Aleatória | Semente do gerador aleatório |
| Réplicas | `--replicas N` | 1 | Número de execuções independentes |
| População | `--pop-size SIZE` | Auto* | Tamanho da população BRKGA |
| Gerações | `--generations GEN` | Auto* | Número de gerações |
| Elite | `--elite PROP` | 0.2 | Proporção de elite (0.0-1.0) |
| Mutantes | `--mutant PROP` | 0.1 | Proporção de mutantes (0.0-1.0) |
| Viés Elite | `--elite-bias BIAS` | 0.7 | Viés no crossover (0.5-1.0) |
| Freq. BL | `--ls-freq FREQ` | Auto* | Frequência busca local (gerações) |
| Iter. BL | `--ls-iters ITERS` | Auto* | Iterações busca local |
| Ótimo | `--optimal VALUE` | None | Valor ótimo para calcular gap |
| Verbose | `--verbose` | False | Modo detalhado |

\* **Valores automáticos** baseados no tamanho da instância:
- **≤20 tarefas**: pop=100, gen=100, ls_freq=10, ls_iters=50
- **21-40 tarefas**: pop=100, gen=100, ls_freq=25, ls_iters=30
- **>40 tarefas**: pop=100, gen=100, ls_freq=25, ls_iters=30

### Exemplos de Uso

```bash
# Instância pequena - parâmetros padrão
python3 run.py --verbose < Instances/1_ros

# Instância grande - aumentar população e gerações
python3 run.py --pop-size 200 --generations 300 --verbose < Instances/28_wee

# Análise estatística - 10 réplicas
python3 run.py --seed 42 --replicas 10 --verbose < Instances/1_hes

# Configuração personalizada completa
python3 run.py --seed 42 --replicas 5 --pop-size 150 --generations 200 \
               --elite 0.25 --mutant 0.15 --elite-bias 0.75 \
               --ls-freq 20 --ls-iters 100 --optimal 94 --verbose \
               < Instances/1_hes
```

---

## 📝 Formato da Instância

As instâncias seguem o formato padrão ALWABP:

```
28                          # n = número de tarefas
70 25 17 37                # tempos: tarefa 1 × 4 trabalhadores
59 Inf 54 42               # Inf = incompatibilidade
33 4 25 1
...                         # n linhas (matriz n×k)
1 3                         # precedência: tarefa 1 → tarefa 3
1 4                         # precedência: tarefa 1 → tarefa 4
3 5
...
-1 -1                       # fim das precedências
```

**Características**:
- Primeira linha: `n` (número de tarefas)
- Próximas `n` linhas: matriz de tempos `n × k`
  - `k` = número de trabalhadores (inferido)
  - `Inf` = incompatibilidade trabalhador-tarefa
- Linhas seguintes: pares `(i, j)` indicando precedência `i → j`
- Linha final: `-1 -1` (terminador)

---

## 🔧 Instalação

### Requisitos
- Python 3.8+
- NumPy
- Gurobi (opcional - apenas para modelo exato)

### Instalação de Dependências

```bash
# Criar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar NumPy (obrigatório)
pip install numpy

# Instalar Gurobi (opcional)
pip install gurobipy
```

---

## 👥 Autores

**Paulo Henrique Silveira**
- GitHub: [@PauloHSilveir](https://github.com/PauloHSilveir)
**Gabriel Jardim de Souza**
- GitHub: [@GNINE11](https://github.com/GNINE11)

---

## 📅 Data

Dezembro de 2025

---

## 📚 Referências

- Miralles, C., et al. (2007). "Advantages of assembly lines in sheltered work centres for disabled." *Management Science*
- Chaves, A. A., et al. (2007). "Biased random-key genetic algorithms"
- ALWABP Benchmark Instances: http://www.assembly-line-balancing.de/

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos.
