# Metodologia do Algoritmo RKO-BRKGA para ALWABP

## 📚 Fundamentação Teórica

### O Problema ALWABP

O **Assembly Line Worker Assignment and Balancing Problem (ALWABP)** é um problema de otimização combinatória que estende o clássico problema de balanceamento de linhas de produção ao considerar que:

1. **Trabalhadores são heterogêneos**: Cada trabalhador possui diferentes tempos de execução para cada tarefa
2. **Restrições de incompatibilidade**: Alguns trabalhadores podem ser incapazes de executar certas tarefas
3. **Precedências tecnológicas**: As tarefas devem respeitar uma ordem parcial definida por um grafo direcionado acíclico (DAG)

**Objetivo**: Minimizar o tempo de ciclo da linha (tempo da estação mais carregada)

**Restrições**:
- Cada tarefa deve ser atribuída a exatamente uma estação
- Cada estação possui exatamente um trabalhador
- Cada trabalhador é alocado a exatamente uma estação
- As precedências devem ser respeitadas: se i ⪯ j, então estação(i) ≤ estação(j)
- Trabalhadores não podem executar tarefas incompatíveis

## 🧬 BRKGA - Biased Random-Key Genetic Algorithm

### Conceito de Chaves Aleatórias

O BRKGA utiliza **chaves aleatórias** (random keys) como representação genética:
- Cada gene é um número real no intervalo [0, 1]
- A **decodificação** transforma esse vetor de números em uma solução válida
- Não há necessidade de operadores genéticos especializados

**Vantagens**:
- Simplicidade de implementação
- Garantia de que o crossover sempre gera cromossomos válidos
- Flexibilidade na decodificação para lidar com restrições

### Estrutura do Cromossomo

Para o ALWABP, o cromossomo possui:

```
[k₁, k₂, ..., kₙ, w₁, w₂, ..., wₘ]
 └─────────────┘  └─────────────┘
  Chaves das       Chaves dos
    tarefas        trabalhadores
```

- **n genes para tarefas**: Definem a prioridade de atribuição das tarefas
- **m genes para trabalhadores**: Definem a ordem de alocação dos trabalhadores

### Processo de Decodificação

#### 1. Atribuição de Trabalhadores
```
Ordenar trabalhadores por suas chaves (maior = maior prioridade)
Atribuir os primeiros |S| trabalhadores às estações sequencialmente
```

#### 2. Atribuição de Tarefas
```
Para cada tarefa em ordem de prioridade (maior chave primeiro):
    Para cada estação s = 0 até |S|-1:
        Se todas as precedências são satisfeitas:
            Se o trabalhador pode executar a tarefa:
                Calcular novo tempo da estação
                Se é a melhor opção encontrada:
                    Marcar como candidata
    
    Atribuir tarefa à estação candidata
```

Este processo **construtivo** garante que:
- Precedências são sempre respeitadas
- Incompatibilidades são evitadas
- Soluções são sempre factíveis

### Componentes do BRKGA

#### População
- **Elite (20%)**: Melhores indivíduos, preservados para a próxima geração
- **Mutantes (10%)**: Novos indivíduos aleatórios (diversidade)
- **Descendentes (70%)**: Gerados por crossover

#### Crossover Parametrizado

```
Para cada gene do cromossomo filho:
    Com probabilidade ρₑ (elite bias = 0.7):
        Herdar gene do pai elite
    Caso contrário:
        Herdar gene do pai não-elite
```

**Viés para o elite** (ρₑ = 0.7) significa:
- 70% dos genes vêm do melhor pai
- 30% dos genes vêm do outro pai
- Exploração guiada pelas boas soluções

## 🔍 Busca Local

### Movimentos Implementados

#### 1. Task Swap
```
Trocar duas tarefas i e j entre estações diferentes
Verificar:
  - Precedências mantidas?
  - Trabalhadores podem executar as tarefas trocadas?
  - Melhora o tempo de ciclo?
```

#### 2. Worker Swap
```
Trocar dois trabalhadores w₁ e w₂ entre estações
Verificar:
  - Trabalhadores podem executar as tarefas de suas novas estações?
  - Melhora o tempo de ciclo?
```

#### 3. Task Move
```
Mover tarefa i da estação s₁ para s₂
Verificar:
  - Precedências mantidas?
  - Trabalhador de s₂ pode executar i?
  - Melhora o tempo de ciclo?
```

### Estratégia de Busca

- **First Improvement**: Aceita o primeiro movimento que melhora
- **Parada**: Após N iterações sem melhoria
- **Aleatorização**: Ordem aleatória de exploração dos vizinhos

## 🔄 Hibridização RKO-BRKGA

### Algoritmo Principal

```
1. INICIALIZAÇÃO
   - Gerar população aleatória
   - Decodificar cromossomos em soluções
   - Avaliar fitness (tempo de ciclo)

2. EVOLUÇÃO HÍBRIDA
   Para cada geração g = 1 até G:
       a) Classificar população por fitness
       b) Selecionar elite
       c) Gerar mutantes
       d) Gerar descendentes (crossover)
       e) Avaliar nova população
       
       Se g % freq_bl == 0:
           Aplicar busca local na melhor solução
           Inserir solução melhorada na população

3. INTENSIFICAÇÃO FINAL
   Aplicar busca local intensiva na melhor solução global
```

### Balanceamento Exploração vs Explotação

| Componente | Papel | Parâmetro |
|------------|-------|-----------|
| BRKGA | Exploração global | Gerações, tamanho população |
| Mutantes | Diversidade | 10% da população |
| Elite | Explotação local | 20% da população |
| Busca Local | Refinamento | Frequência = 10 gerações |
| BL Final | Intensificação | 2× iterações |

## 📊 Parâmetros Recomendados

### Baseados em Literatura e Experimentos

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| População | 100-200 | Equilíbrio custo/qualidade |
| Elite | 20% | Padrão BRKGA |
| Mutantes | 10% | Diversidade moderada |
| Elite Bias | 0.7 | Herança forte do melhor |
| Gerações | 50-200 | Depende do tamanho |
| Freq. BL | 10 | Não muito frequente |
| Iter. BL | 50 | Refinamento adequado |

### Calibração Recomendada

Para **instâncias pequenas** (< 15 tarefas):
- População menor (50-100)
- Menos gerações (50)
- BL mais intensiva

Para **instâncias grandes** (> 30 tarefas):
- População maior (150-250)
- Mais gerações (100-200)
- BL menos frequente

## 🎯 Características da Abordagem

### Pontos Fortes

1. **Robustez**: Lida bem com restrições complexas
2. **Qualidade**: Hibridização melhora soluções
3. **Flexibilidade**: Fácil adaptação para variantes
4. **Eficiência**: Converge em tempo razoável

### Limitações

1. **Parâmetros sensíveis**: Requer calibração
2. **Decodificação custosa**: Pode ser gargalo computacional
3. **Garantias**: Não garante ótimo global

## 📖 Referências Metodológicas

### BRKGA
- Bean, J. C. (1994). Genetic algorithms and random keys for sequencing and optimization
- Gonçalves, J. F., & Resende, M. G. (2011). Biased random-key genetic algorithms for combinatorial optimization

### ALWABP
- Miralles, C., et al. (2007). Advantages of assembly lines in sheltered work centres for disabled
- Moreira, M. C. O., & Costa, A. M. (2013). Hybrid heuristics for planning job rotation schedules in assembly lines with heterogeneous workers

### Hibridização
- Resende, M. G., & Ribeiro, C. C. (2016). Optimization by GRASP: Greedy Randomized Adaptive Search Procedures
- Talbi, E. G. (2009). Metaheuristics: from design to implementation

## 💡 Extensões Possíveis

1. **Path Relinking**: Conectar soluções elite
2. **Multi-objetivo**: Considerar outros critérios (balanceamento, ergonomia)
3. **Memória de longo prazo**: Registrar boas configurações
4. **Paralelização**: Executar BL em múltiplas soluções simultaneamente
5. **Aprendizado**: Adaptar parâmetros durante a execução
