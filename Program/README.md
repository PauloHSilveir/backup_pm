# Program - Estrutura do Código

## Organização Modular

### **Problem/** (SPECIFIC_CODE)
Código específico do problema ALWABP:

- **alwabp_instance.py**: Estrutura de dados do problema ALWABP
- **alwabp_solution.py**: Representação de soluções
- **decoder.py**: Decodificador de chaves aleatórias em soluções factíveis
- **read_instance.py**: Função de leitura de instâncias do stdin

### **MH/** (GENERAL_CODE)
Implementação da meta-heurística:

- **brkga.py**: BRKGA (Biased Random-Key Genetic Algorithm)
- **local_search.py**: Busca Local com três movimentos
- **rko_brkga.py**: Integração RKO-BRKGA (híbrido)

### **Main/**
Ponto de entrada do programa:

- **main.py**: Função principal, parsing de argumentos, controle de réplicas, estatísticas e saída

## Fluxo de Execução

1. **run.py** (raiz) → configura paths e chama Main
2. **Main/main.py** → lê instância (Problem) e executa algoritmo (MH)
3. **MH/rko_brkga.py** → alterna BRKGA + Busca Local
4. **Problem/decoder.py** → converte cromossomos em soluções
5. **Results/** → saída em JSON com solução e estatísticas

## Uso

Da raiz do projeto:
```bash
python3 run.py Results/solution.json --seed 42 --replicas 5 < Instances/10_hes
```
