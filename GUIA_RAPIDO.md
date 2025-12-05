# Guia Rápido de Início - RKO-BRKGA para ALWABP

## 🚀 Início Rápido (5 minutos)

### 1. Instalação
```bash
pip install numpy
```

### 2. Teste Rápido
```bash
python main.py
```
Escolha opção `1` (instância simples) e `s` (parâmetros padrão)

## 📝 Uso Básico

### Criar e Resolver uma Instância

```python
from alwabp_instance import ALWABPInstance
from rko_brkga import RKO_BRKGA
import numpy as np

# 1. Criar instância
instance = ALWABPInstance(
    n_tasks=8,        # número de tarefas
    n_workers=4,      # número de trabalhadores
    n_stations=4      # número de estações
)

# 2. Definir tempos de execução (matriz: trabalhadores × tarefas)
instance.execution_times = np.array([
    [5, 7, 3, 6, 4, 8, 5, 7],   # Trabalhador 0
    [6, 5, 4, 7, 5, 6, 4, 8],   # Trabalhador 1
    [7, 8, 5, 5, 6, 7, 6, 6],   # Trabalhador 2
    [4, 6, 6, 8, 7, 5, 7, 5],   # Trabalhador 3
], dtype=float)

# 3. Adicionar precedências (tarefa i deve preceder tarefa j)
instance.add_precedence(0, 1)  # Tarefa 0 → Tarefa 1
instance.add_precedence(1, 3)  # Tarefa 1 → Tarefa 3
instance.add_precedence(3, 5)  # Tarefa 3 → Tarefa 5
# ... adicionar outras precedências

# 4. Definir incompatibilidades (opcional)
instance.set_incompatible_task(worker=1, task=5)  # Trabalhador 1 não pode fazer tarefa 5

# 5. Criar e executar o algoritmo
rko = RKO_BRKGA(instance)
solution, exec_time = rko.solve(verbose=True)

# 6. Ver resultados
rko.print_solution_details()
```

## 📊 Visualizar Resultados

```python
from visualization import visualize_solution

# Visualização completa da solução
visualize_solution(solution, instance)

# Tempo de ciclo (objetivo minimizado)
print(f"Tempo de ciclo: {solution.cycle_time}")

# Verificar se é factível
print(f"Factível: {solution.is_feasible()}")
```

## ⚙️ Ajustar Parâmetros

### Configuração Padrão (Boa para Iniciar)
```python
rko = RKO_BRKGA(
    instance,
    population_size=100,    # Tamanho da população
    elite_size=0.2,         # 20% são elite
    mutant_size=0.1,        # 10% são mutantes
    elite_bias=0.7          # 70% de herança do elite
)

solution, _ = rko.solve(
    brkga_generations=100,          # Número de gerações
    local_search_freq=10,           # Aplicar BL a cada 10 gerações
    local_search_iterations=50,     # Iterações da busca local
    verbose=True                    # Mostrar progresso
)
```

### Para Instâncias Pequenas (< 15 tarefas)
```python
rko = RKO_BRKGA(instance, population_size=50)
solution, _ = rko.solve(brkga_generations=50)
```

### Para Instâncias Grandes (> 30 tarefas)
```python
rko = RKO_BRKGA(instance, population_size=200)
solution, _ = rko.solve(brkga_generations=200)
```

### Para Melhor Qualidade (mais tempo)
```python
rko = RKO_BRKGA(instance, population_size=150)
solution, _ = rko.solve(
    brkga_generations=200,
    local_search_freq=5,        # BL mais frequente
    local_search_iterations=100  # BL mais intensiva
)
```

### Para Execução Rápida
```python
rko = RKO_BRKGA(instance, population_size=50)
solution, _ = rko.solve(
    brkga_generations=30,
    local_search_freq=15,
    local_search_iterations=20
)
```

## 🔍 Analisar a Solução

### Ver Detalhes
```python
# Atribuição de trabalhadores
print(solution.worker_assignment)  # Array: [worker em estação 0, worker em estação 1, ...]

# Atribuição de tarefas
print(solution.task_assignment)    # Array: [estação da tarefa 0, estação da tarefa 1, ...]

# Tempos por estação
print(solution.station_times)      # Array: [tempo estação 0, tempo estação 1, ...]

# Tempo de ciclo (gargalo)
print(solution.cycle_time)         # Tempo da estação mais carregada
```

### Verificar Qualidade
```python
# Factibilidade
is_valid = solution.is_feasible()

# Balanceamento
total_time = sum(solution.station_times)
max_time = solution.cycle_time * instance.n_stations
balance_percent = (total_time / max_time) * 100

print(f"Balanceamento: {balance_percent:.1f}%")
print(f"Ociosidade: {100 - balance_percent:.1f}%")
```

## 📚 Exemplos Prontos

```bash
# Executar exemplos interativos
python exemplos_uso.py

# Opções:
# 1 - Linha simples (8 tarefas)
# 2 - Trabalhadores especializados (10 tarefas)
# 3 - Precedências complexas (12 tarefas)
# 4 - Comparação de configurações
# 5 - Cenário industrial realista (15 tarefas)
# 6 - Todos os exemplos
```

## 🧪 Testes e Experimentos

```bash
# Executar testes comparativos
python test_experiments.py

# Opções:
# 1 - Comparar diferentes configurações
# 2 - Teste de escalabilidade
# 3 - Ambos
```

## 📖 Ler Instância de Arquivo

```python
# Se você tiver um arquivo com formato específico
instance = ALWABPInstance(n_tasks=0, n_workers=0, n_stations=0)
instance.read_from_file('caminho/para/instancia.txt')

# Nota: Você precisa implementar o método read_from_file 
# de acordo com o formato do seu arquivo
```

## 💡 Dicas

### Problema não converge?
- Aumente o tamanho da população
- Aumente o número de gerações
- Torne a busca local mais frequente

### Execução muito lenta?
- Diminua o tamanho da população
- Reduza frequência da busca local
- Use menos gerações

### Soluções infactíveis?
- Verifique se as precedências fazem sentido
- Verifique se há trabalhadores suficientes que podem fazer as tarefas
- Use o método `is_feasible()` para debugar

### Comparar múltiplas execuções?
```python
from test_experiments import run_experiment

config = {
    'population_size': 100,
    'elite_size': 0.2,
    'mutant_size': 0.1,
    'elite_bias': 0.7,
    'generations': 100,
    'ls_freq': 10,
    'ls_iterations': 50
}

results = run_experiment(instance, config, n_runs=10)
print(f"Média: {results['mean_cycle_time']:.2f}")
print(f"Desvio: {results['std_cycle_time']:.2f}")
print(f"Melhor: {results['best_cycle_time']:.2f}")
```

## 📧 Ajuda

- Veja **README_RKO.md** para documentação completa
- Veja **METODOLOGIA.md** para entender o algoritmo
- Execute **exemplos_uso.py** para ver casos práticos
- Analise os módulos individuais para entender cada componente

## 🎯 Checklist de Uso

- [ ] Instalei o numpy
- [ ] Criei uma instância do problema
- [ ] Defini os tempos de execução
- [ ] Adicionei as precedências
- [ ] (Opcional) Defini incompatibilidades
- [ ] Criei o objeto RKO_BRKGA
- [ ] Executei solve()
- [ ] Verifiquei se a solução é factível
- [ ] Analisei o tempo de ciclo

✅ Pronto para usar!
