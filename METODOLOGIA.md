# Documentação Metodológica - RKO-BRKGA para ALWABP

## 1. Meta-heurística: RKO-BRKGA

**RKO (Random Key Optimization)** com **BRKGA (Biased Random-Key Genetic Algorithm)** e **Busca Local**.

## 2. Representação do Problema

### Codificação (Cromossomo)
O problema é representado por **chaves aleatórias** (random keys):

- **Chaves de tarefas** (n valores): `task_keys[i] ∈ [0,1]` - prioridade da tarefa i
- **Chaves de trabalhadores** (k valores): `worker_keys[w] ∈ [0,1]` - prioridade do trabalhador w

**Tamanho total do cromossomo**: n + k genes (valores reais entre 0 e 1)

### Decodificação
O decodificador transforma o cromossomo em uma solução factível:

1. **Atribuição de trabalhadores**: Ordena workers por suas chaves e atribui sequencialmente às estações
2. **Atribuição de tarefas**: 
   - Ordena tarefas por suas chaves (maior = maior prioridade)
   - Processa em múltiplas passagens respeitando precedências
   - Para cada tarefa, encontra a estação mais cedo possível que:
     - Respeita precedências (≥ estação de todas as predecessoras)
     - Tem trabalhador compatível (tempo finito)
     - Minimiza tempo de estação

## 3. Função Objetivo

**Minimizar o tempo de ciclo (makespan):**

```
C = max{C_s : s ∈ S}
```

onde `C_s` é o tempo total da estação s:

```
C_s = Σ(t_wi × y_isw)
```

- `t_wi`: tempo do trabalhador w executar tarefa i
- `y_isw = 1` se tarefa i é executada por trabalhador w na estação s

## 4. Geração da Solução Inicial

**População inicial aleatória**:
- Cada indivíduo tem `n + k` genes
- Cada gene é sorteado uniformemente em `[0, 1]`
- População de tamanho `pop_size` (padrão: 50-100 dependendo do tamanho)

## 5. BRKGA - Algoritmo Genético

### Parâmetros
- **População**: 50-200 indivíduos (auto-ajustado por tamanho)
- **Elite**: 20% dos melhores indivíduos
- **Mutantes**: 10% de indivíduos aleatórios
- **Elite bias**: 0.7 (probabilidade de herdar gene do pai elite)

### Operadores

#### Crossover Parametrizado
```python
filho[i] = elite[i]     se rand() < elite_bias
         = não_elite[i] caso contrário
```

#### Mutação
- 10% da população é substituída por indivíduos completamente aleatórios

### Seleção
- **Elite**: preservada integralmente para próxima geração
- **Crossover**: 70% da nova população (elite × não-elite)
- **Mutantes**: 10% completamente novos

## 6. Busca Local

### Vizinhança
Três movimentos implementados:

1. **Task Swap**: Troca duas tarefas de estações diferentes
   ```
   Swap(task_i, task_j) onde station[i] ≠ station[j]
   ```

2. **Worker Swap**: Troca dois trabalhadores de estações diferentes
   ```
   Swap(worker_s1, worker_s2) onde s1 ≠ s2
   ```

3. **Task Move**: Move uma tarefa para outra estação
   ```
   Move(task_i, station_old, station_new)
   ```

### Estratégia de Escolha
**First Improvement**: aceita o primeiro movimento que melhora a solução

### Aplicação
- Executada periodicamente no melhor indivíduo da elite
- Frequência: a cada 10-25 gerações (auto-ajustado)
- Iterações: 30-50 por aplicação

## 7. Integração RKO

O algoritmo alterna entre:
1. **Fase BRKGA** (exploração): evolução da população
2. **Fase Busca Local** (intensificação): refinamento do melhor

```
Para cada geração:
  1. Evoluir população (BRKGA)
  2. Se geração % ls_freq == 0:
     Aplicar busca local no melhor
```

## 8. Critério de Parada

**Número fixo de gerações**:
- 50-200 gerações (auto-ajustado por tamanho da instância)
- Configurável via linha de comando

## 9. Parâmetros Configuráveis

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--seed` | None | Semente aleatória |
| `--replicas` | 1 | Número de execuções |
| `--pop-size` | auto | Tamanho da população |
| `--generations` | auto | Número de gerações |
| `--elite` | 0.2 | % de elite |
| `--mutant` | 0.1 | % de mutantes |
| `--elite-bias` | 0.7 | Viés do crossover |
| `--ls-freq` | auto | Frequência busca local |
| `--ls-iters` | auto | Iterações busca local |

## 10. Método de Escolha de Parâmetros

### Auto-ajuste por Tamanho
```python
if n_tasks ≤ 10:
    pop=50, gen=50, ls_freq=10, ls_iter=30
elif n_tasks ≤ 20:
    pop=100, gen=100, ls_freq=10, ls_iter=50
elif n_tasks ≤ 40:
    pop=100, gen=200, ls_freq=25, ls_iter=30
else:
    pop=100, gen=100, ls_freq=25, ls_iter=30
```

### Calibração Experimental
Parâmetros fixos calibrados empiricamente:
- **Elite**: 20% (balança exploração/intensificação)
- **Mutantes**: 10% (mantém diversidade)
- **Elite bias**: 0.7 (favorece bons genes)

## 11. Restrições Tratadas

1. **Precedências**: Tarefa i antes de j → `station[i] ≤ station[j]`
2. **Incompatibilidades**: Evita `t_wi = ∞`
3. **Unicidade**: 
   - Cada tarefa em exatamente 1 estação
   - Cada trabalhador em exatamente 1 estação
   - Cada estação com exatamente 1 trabalhador

## 12. Documentação Experimental

Para métodos estocásticos, o código suporta:
- **Múltiplas réplicas** (`--replicas N`)
- **Sementes controladas** (`--seed S`)
- **Estatísticas agregadas**: média, desvio padrão, melhor/pior
- **Saída em JSON** com todos os detalhes

### Exemplo de Execução
```bash
python3 main.py solution.json --seed 42 --replicas 5 < instancia.txt
```

Saída:
- **stdout**: melhor tempo de ciclo
- **stderr**: estatísticas (média, desvio, tempo)
- **JSON**: solução completa com parâmetros

## 13. Referências

### Algoritmo Base
- GONÇALVES, J. F.; RESENDE, M. G. C. **Biased random-key genetic algorithms for combinatorial optimization**. Journal of Heuristics, v. 17, n. 5, p. 487-525, 2011.

### Problema
- MIRALLES, C. et al. **Advantages of assembly lines in Sheltered Work Centres for Disabled. A case study**. International Journal of Production Economics, v. 110, n. 1-2, p. 187-197, 2007.

### Implementação
- Código original desenvolvido para trabalho prático de Programação Matemática
- NumPy para operações numéricas eficientes
