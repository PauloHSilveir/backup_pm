# Estrutura Modular do Código - RKO-BRKGA para ALWABP

## 📦 Visão Geral dos Módulos

Este documento explica a organização modular do código e como os componentes interagem.

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APLICAÇÃO                      │
├─────────────────────────────────────────────────────────────┤
│  main.py          │ exemplos_uso.py   │ test_experiments.py │
│  Script principal │ Casos de uso      │ Testes e benchmarks│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA DE ALGORITMO                       │
├─────────────────────────────────────────────────────────────┤
│              rko_brkga.py (Orquestrador)                    │
│  - Integra BRKGA com Busca Local                           │
│  - Gerencia o ciclo evolutivo híbrido                      │
└─────────────────────────────────────────────────────────────┘
              ↓                          ↓
┌────────────────────────┐  ┌───────────────────────────┐
│   OTIMIZAÇÃO GLOBAL    │  │  OTIMIZAÇÃO LOCAL         │
├────────────────────────┤  ├───────────────────────────┤
│     brkga.py           │  │   local_search.py         │
│  - População           │  │  - Task Swap              │
│  - Elitismo            │  │  - Worker Swap            │
│  - Crossover           │  │  - Task Move              │
│  - Mutação             │  │  - First Improvement      │
└────────────────────────┘  └───────────────────────────┘
              ↓                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA DE DECODIFICAÇÃO                   │
├─────────────────────────────────────────────────────────────┤
│                      decoder.py                             │
│  - Transforma chaves aleatórias em soluções factíveis      │
│  - Respeita precedências e incompatibilidades              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                CAMADA DE DOMÍNIO DO PROBLEMA                │
├────────────────────────────┬────────────────────────────────┤
│   alwabp_instance.py       │   alwabp_solution.py           │
│  - Dados do problema       │  - Representação da solução    │
│  - Tempos de execução      │  - Atribuições                 │
│  - Precedências            │  - Cálculo de fitness          │
│  - Incompatibilidades      │  - Validação                   │
└────────────────────────────┴────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE UTILIDADES                     │
├─────────────────────────────────────────────────────────────┤
│                   visualization.py                          │
│  - Visualização de soluções                                │
│  - Gráficos de precedências                                │
│  - Comparação de soluções                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🔍 Detalhamento dos Módulos

### 1. alwabp_instance.py
**Responsabilidade**: Representar o problema

**Classes**:
- `ALWABPInstance`: Contêiner para dados da instância

**Dados armazenados**:
- `n_tasks`: Número de tarefas
- `n_workers`: Número de trabalhadores
- `n_stations`: Número de estações
- `execution_times`: Matriz [workers × tasks] com tempos
- `precedences`: Lista de tuplas (i, j) de precedências
- `incompatible_tasks`: Lista de sets com tarefas incompatíveis por worker

**Métodos principais**:
- `add_precedence(i, j)`: Adiciona precedência
- `set_execution_time(w, t, time)`: Define tempo
- `set_incompatible_task(w, t)`: Marca incompatibilidade
- `get_precedence_matrix()`: Retorna matriz de precedências (com fechamento transitivo)

**Quando usar**:
- Criar nova instância do problema
- Carregar dados de arquivos
- Consultar informações da instância

---

### 2. alwabp_solution.py
**Responsabilidade**: Representar uma solução

**Classes**:
- `ALWABPSolution`: Contêiner para solução do problema

**Dados armazenados**:
- `task_assignment`: Array [tasks] indicando estação de cada tarefa
- `worker_assignment`: Array [stations] indicando trabalhador de cada estação
- `cycle_time`: Tempo de ciclo (fitness)
- `station_times`: Array [stations] com tempo de cada estação

**Métodos principais**:
- `is_feasible()`: Valida todas as restrições
- `calculate_cycle_time()`: Calcula e atualiza fitness
- `copy()`: Cria cópia independente

**Quando usar**:
- Representar candidatos a solução
- Avaliar qualidade (fitness)
- Verificar factibilidade

---

### 3. decoder.py
**Responsabilidade**: Converter cromossomos em soluções

**Classes**:
- `RandomKeyDecoder`: Decodificador de chaves aleatórias

**Processo**:
1. Recebe array de floats [0, 1]
2. Divide em: chaves de tarefas + chaves de workers
3. Ordena workers por prioridade
4. Atribui workers às estações
5. Ordena tarefas por prioridade
6. Atribui tarefas respeitando restrições

**Métodos principais**:
- `decode(chromosome)`: Transforma array em ALWABPSolution
- `_decode_tasks_with_precedence()`: Atribui tarefas factivamente

**Quando usar**:
- Avaliar cromossomo do BRKGA
- Converter representação genética em solução do problema
- Garantir factibilidade durante decodificação

---

### 4. brkga.py
**Responsabilidade**: Implementar BRKGA

**Classes**:
- `BRKGA`: Algoritmo genético com chaves aleatórias

**Componentes**:
- **População**: Matriz [pop_size × chromosome_size]
- **Elite**: Melhores indivíduos preservados
- **Mutantes**: Novos indivíduos aleatórios
- **Descendentes**: Gerados por crossover

**Métodos principais**:
- `initialize_population()`: Cria população inicial aleatória
- `evolve(generations)`: Executa gerações evolutivas
- `_crossover()`: Combina elite com não-elite (biased)
- `get_best_solution()`: Retorna melhor encontrado

**Parâmetros importantes**:
- `population_size`: Tamanho da população (padrão: 100)
- `elite_size`: Proporção de elite (padrão: 0.2)
- `mutant_size`: Proporção de mutantes (padrão: 0.1)
- `elite_bias`: Viés do crossover (padrão: 0.7)

**Quando usar**:
- Exploração global do espaço de busca
- Manter diversidade populacional
- Busca evolucionária

---

### 5. local_search.py
**Responsabilidade**: Refinar soluções

**Classes**:
- `LocalSearch`: Busca em vizinhança

**Movimentos**:
1. **Task Swap**: Troca 2 tarefas entre estações
2. **Worker Swap**: Troca 2 workers entre estações
3. **Task Move**: Move 1 tarefa para outra estação

**Métodos principais**:
- `improve(solution)`: Aplica busca local
- `_try_task_swap()`: Tenta movimento 1
- `_try_worker_swap()`: Tenta movimento 2
- `_try_task_move()`: Tenta movimento 3

**Estratégia**:
- First Improvement (aceita primeira melhoria)
- Parada por iterações sem melhoria
- Aleatorização da ordem de exploração

**Quando usar**:
- Refinamento de soluções promissoras
- Intensificação em região boa
- Escape de ótimos locais fracos

---

### 6. rko_brkga.py
**Responsabilidade**: Orquestrar algoritmo híbrido

**Classes**:
- `RKO_BRKGA`: Algoritmo principal

**Fluxo de execução**:
```
1. INICIALIZAÇÃO
   ├─ Criar instância BRKGA
   ├─ Criar instância LocalSearch
   └─ Inicializar população

2. EVOLUÇÃO HÍBRIDA (G gerações)
   Para cada geração:
   ├─ Evoluir BRKGA (1 geração)
   └─ Se geração % freq == 0:
      └─ Aplicar busca local no melhor

3. INTENSIFICAÇÃO FINAL
   └─ Busca local intensiva no melhor global
```

**Métodos principais**:
- `solve()`: Executa algoritmo completo
- `get_best_solution()`: Retorna melhor encontrado
- `print_solution_details()`: Exibe detalhes

**Quando usar**:
- Resolver instância do ALWABP
- Obter solução de alta qualidade
- Balancear exploração e explotação

---

### 7. visualization.py
**Responsabilidade**: Visualizar e analisar

**Funções**:
- `visualize_solution()`: Mostra solução completa
- `visualize_precedence_graph()`: Exibe grafo
- `visualize_worker_capabilities()`: Mostra habilidades
- `compare_solutions()`: Compara duas soluções

**Quando usar**:
- Entender solução obtida
- Debugar problemas
- Comparar resultados
- Gerar relatórios

---

### 8. main.py
**Responsabilidade**: Interface de execução

**Funções**:
- `create_simple_instance()`: Instância pequena de teste
- `create_medium_instance()`: Instância média de teste
- `main()`: Menu interativo
- `save_results()`: Salvar em arquivo

**Quando usar**:
- Executar algoritmo interativamente
- Testar rapidamente
- Gerar resultados para relatório

---

### 9. exemplos_uso.py
**Responsabilidade**: Demonstrar uso prático

**Funções**:
- `exemplo_1_linha_simples()`: Caso básico
- `exemplo_2_trabalhadores_especializados()`: Workers especializados
- `exemplo_3_grafo_complexo()`: Precedências complexas
- `exemplo_4_comparacao_configuracoes()`: Tuning de parâmetros
- `exemplo_5_instancia_real()`: Cenário realista

**Quando usar**:
- Aprender a usar o código
- Ver casos de aplicação
- Entender configurações

---

### 10. test_experiments.py
**Responsabilidade**: Experimentos e testes

**Funções**:
- `run_experiment()`: Executa múltiplas rodadas
- `compare_configurations()`: Compara configurações
- `test_scalability()`: Testa escalabilidade

**Quando usar**:
- Avaliar robustez
- Comparar parâmetros
- Análise estatística
- Validação científica

---

## 🔗 Dependências entre Módulos

```
main.py
  └─ rko_brkga.py
      ├─ brkga.py
      │   ├─ decoder.py
      │   │   ├─ alwabp_instance.py
      │   │   └─ alwabp_solution.py
      │   ├─ alwabp_instance.py
      │   └─ alwabp_solution.py
      └─ local_search.py
          ├─ alwabp_instance.py
          └─ alwabp_solution.py

visualization.py
  ├─ alwabp_instance.py
  └─ alwabp_solution.py

exemplos_uso.py
  ├─ rko_brkga.py
  ├─ visualization.py
  ├─ alwabp_instance.py
  └─ alwabp_solution.py

test_experiments.py
  ├─ rko_brkga.py
  └─ alwabp_instance.py
```

## 🛠️ Como Estender

### Adicionar novo movimento de busca local
1. Editar `local_search.py`
2. Criar método `_try_new_move()`
3. Chamar em `improve()`

### Adicionar nova estratégia de decodificação
1. Criar nova classe em `decoder.py`
2. Implementar método `decode()`
3. Usar em `brkga.py`

### Adicionar nova métrica de qualidade
1. Editar `alwabp_solution.py`
2. Adicionar método de cálculo
3. Usar em `visualization.py`

### Adicionar suporte a novo formato de arquivo
1. Editar `alwabp_instance.py`
2. Implementar `read_from_file()`
3. Documentar formato

## ✅ Checklist de Compreensão

Para entender completamente o código, certifique-se de:

- [ ] Compreender representação de instância (`alwabp_instance.py`)
- [ ] Compreender representação de solução (`alwabp_solution.py`)
- [ ] Entender processo de decodificação (`decoder.py`)
- [ ] Conhecer funcionamento do BRKGA (`brkga.py`)
- [ ] Saber como funciona busca local (`local_search.py`)
- [ ] Entender integração híbrida (`rko_brkga.py`)
- [ ] Saber executar o algoritmo (`main.py`)
- [ ] Conhecer casos de uso (`exemplos_uso.py`)

## 📚 Ordem de Leitura Recomendada

1. **GUIA_RAPIDO.md** - Para começar rapidamente
2. **alwabp_instance.py** - Entender o problema
3. **alwabp_solution.py** - Entender a solução
4. **decoder.py** - Entender decodificação
5. **brkga.py** - Entender BRKGA
6. **local_search.py** - Entender busca local
7. **rko_brkga.py** - Entender integração
8. **METODOLOGIA.md** - Entender teoria
9. **exemplos_uso.py** - Ver aplicações
10. **README_RKO.md** - Documentação completa
