# Trabalho Prático - Programação Matemática

## Algoritmo RKO-BRKGA para ALWABP

Este repositório contém a implementação de um algoritmo **RKO (Random Key Optimization)** combinando **BRKGA (Biased Random-Key Genetic Algorithm)** com **Busca Local** para resolver o **ALWABP (Assembly Line Worker Assignment and Balancing Problem)**.

### 📁 Estrutura do Projeto

```
trabalho_pratico_PM/
├── alwabp_instance.py      # Definição e manipulação de instâncias do problema
├── alwabp_solution.py      # Representação de soluções
├── decoder.py              # Decodificador de chaves aleatórias
├── brkga.py                # Implementação do BRKGA
├── local_search.py         # Busca local para refinamento
├── rko_brkga.py           # Algoritmo principal (RKO-BRKGA)
├── main.py                 # Script principal de execução
├── exemplos_uso.py         # Exemplos práticos de uso
├── test_experiments.py     # Testes e experimentos
├── visualization.py        # Funções de visualização
├── README_RKO.md          # Documentação detalhada
├── METODOLOGIA.md         # Explicação da metodologia
└── bygpt.py               # [arquivo existente]
```

### 🚀 Como Executar

#### Instalação
```bash
pip install numpy
```

#### Execução Rápida
```bash
python main.py              # Execução interativa
python exemplos_uso.py      # Ver exemplos práticos
python test_experiments.py  # Executar testes
```

### 📚 Documentação

- **README_RKO.md**: Documentação completa do código e uso
- **METODOLOGIA.md**: Explicação teórica da abordagem
- **exemplos_uso.py**: 5 exemplos práticos diferentes

### 🎯 Características

- Código **totalmente modularizado**
- Algoritmo híbrido eficiente (BRKGA + Busca Local)
- Tratamento de todas as restrições do ALWABP
- Visualizações em texto das soluções
- Exemplos práticos de uso
- Testes e comparação de configurações

### 👤 Autor

Paulo H. Silveira

### 📅 Data

Dezembro de 2025
