# RKO-BRKGA para ALWABP

## Assembly Line Worker Assignment and Balancing Problem

Este projeto implementa um algoritmo **RKO (Random Key Optimization)** combinando **BRKGA (Biased Random-Key Genetic Algorithm)** com **Busca Local** para resolver o problema ALWABP.

## 📋 Sobre o Problema

O ALWABP (Assembly Line Worker Assignment and Balancing Problem) é um problema de otimização que considera:

- **Estações de trabalho** linearmente ordenadas
- **Trabalhadores** com diferentes habilidades e velocidades
- **Tarefas** com relações de precedência
- **Objetivo**: Minimizar o tempo de ciclo da linha de produção

### Características
- Cada trabalhador tem tempos de execução diferentes para cada tarefa
- Alguns trabalhadores podem ser incapazes de executar certas tarefas
- As tarefas devem respeitar relações de precedência
- Cada estação possui exatamente um trabalhador
- O tempo de ciclo é determinado pela estação mais carregada

## 🏗️ Estrutura do Código

O código está organizado de forma **modular** para facilitar o entendimento:

### 1. `alwabp_instance.py`
- **Classe**: `ALWABPInstance`
- **Função**: Representa uma instância do problema
- **Contém**:
  - Número de tarefas, trabalhadores e estações
  - Matriz de tempos de execução
  - Relações de precedência
  - Tarefas incompatíveis por trabalhador

### 2. `alwabp_solution.py`
- **Classe**: `ALWABPSolution`
- **Função**: Representa uma solução do problema
- **Contém**:
  - Atribuição de tarefas às estações
  - Atribuição de trabalhadores às estações
  - Tempo de ciclo
  - Métodos para validação e cálculo de fitness

### 3. `decoder.py`
- **Classe**: `RandomKeyDecoder`
- **Função**: Decodifica cromossomos (chaves aleatórias) em soluções
- **Estratégia**:
  - Cromossomo dividido em duas partes:
    - Genes para ordem de tarefas
    - Genes para ordem de trabalhadores
  - Decodificação construtiva respeitando restrições

### 4. `local_search.py`
- **Classe**: `LocalSearch`
- **Função**: Refina soluções através de busca local
- **Movimentos**:
  - **Task Swap**: Troca duas tarefas entre estações
  - **Worker Swap**: Troca dois trabalhadores entre estações
  - **Task Move**: Move uma tarefa para outra estação
- **Estratégia**: First Improvement com parada por iterações sem melhoria

### 5. `brkga.py`
- **Classe**: `BRKGA`
- **Função**: Implementa o algoritmo genético com chaves aleatórias
- **Componentes**:
  - População de cromossomos (chaves aleatórias [0,1])
  - **Elitismo**: Mantém os melhores indivíduos
  - **Mutantes**: Introduz diversidade
  - **Crossover parametrizado**: Combina elite com não-elite (viés configurável)

### 6. `rko_brkga.py`
- **Classe**: `RKO_BRKGA`
- **Função**: Algoritmo principal que integra BRKGA + Busca Local
- **Fases**:
  1. Inicialização da população
  2. Evolução com aplicação periódica de busca local
  3. Busca local final intensiva

### 7. `main.py`
- **Função**: Script principal para execução
- **Recursos**:
  - Criação de instâncias de teste
  - Configuração interativa de parâmetros
  - Execução do algoritmo
  - Exibição e salvamento de resultados

## 🚀 Como Usar

### Instalação de Dependências
```bash
pip install numpy
```

### Execução
```bash
python main.py
```

### Uso Interativo
1. Escolha o tipo de instância (simples ou média)
2. Configure os parâmetros ou use valores padrão
3. Aguarde a execução
4. Visualize os resultados
5. Opcionalmente, salve os resultados em arquivo

### Exemplo de Uso Programático
```python
from alwabp_instance import ALWABPInstance
from rko_brkga import RKO_BRKGA

# Criar instância
instance = ALWABPInstance(n_tasks=10, n_workers=5, n_stations=5)
# ... configurar tempos e precedências ...

# Criar e executar algoritmo
rko = RKO_BRKGA(
    instance=instance,
    population_size=100,
    elite_size=0.2,
    mutant_size=0.1,
    elite_bias=0.7
)

solution, exec_time = rko.solve(
    brkga_generations=100,
    local_search_freq=10,
    local_search_iterations=50,
    verbose=True
)

# Ver resultados
rko.print_solution_details()
```

## ⚙️ Parâmetros do Algoritmo

### BRKGA
- **population_size**: Tamanho da população (padrão: 100)
- **elite_size**: Proporção de elite (padrão: 0.2 = 20%)
- **mutant_size**: Proporção de mutantes (padrão: 0.1 = 10%)
- **elite_bias**: Viés do crossover (padrão: 0.7 = 70% de herança do elite)

### Evolução
- **brkga_generations**: Número de gerações (padrão: 100)
- **local_search_freq**: Frequência de aplicação da busca local (padrão: a cada 10 gerações)
- **local_search_iterations**: Iterações da busca local (padrão: 50)

## 📊 Saída do Algoritmo

O algoritmo fornece:
- **Tempo de ciclo**: Objetivo minimizado
- **Atribuição de trabalhadores**: Qual trabalhador em cada estação
- **Atribuição de tarefas**: Quais tarefas em cada estação
- **Tempo por estação**: Carga de trabalho de cada estação
- **Balanceamento**: Percentual de utilização da linha
- **Factibilidade**: Validação das restrições
- **Tempo de execução**: Duração do algoritmo

## 🔬 Características do RKO-BRKGA

### Vantagens
1. **Codificação Flexível**: Chaves aleatórias permitem lidar com restrições complexas
2. **Hibridização**: BRKGA para exploração + Busca Local para refinamento
3. **Modularidade**: Fácil manutenção e extensão
4. **Eficiência**: Boa qualidade de solução em tempo razoável

### Estratégias Implementadas
- Decodificação construtiva respeitando precedências
- Crossover parametrizado com viés para elite
- Busca local multi-movimento
- Elitismo com reintrodução de mutantes

## 📝 Referência

Baseado em:
> Miralles, C., Garcia-Sabater, J. P., Andres, C., & Cardos, M. (2007). 
> Advantages of assembly lines in sheltered work centres for disabled. A case study. 
> International Journal of Production Economics, 110(1-2), 187-197.

## 👤 Autor

Paulo H. Silveira

## 📅 Data

Dezembro de 2025
