"""
Módulo para leitura de instâncias do ALWABP a partir da entrada padrão

Formato esperado:
- Primeira linha: número de tarefas (n)
- Próximas n linhas: matriz de tempos (n x k), onde k é o número de trabalhadores
  - Valores podem ser números ou "inf" para tarefas incompatíveis
- Linhas seguintes: pares (i, j) indicando precedências
- Última linha: -1 -1 (indica fim das precedências)
"""

import sys
import math
import numpy as np
from .alwabp_instance import ALWABPInstance


def parse_value(v: str) -> float:
    """
    Converte string em float, tratando 'inf' especialmente
    
    Args:
        v: string a ser convertida
        
    Returns:
        Valor float
    """
    if v.lower() == "inf":
        return math.inf
    return float(v)


def read_instance_from_stdin() -> ALWABPInstance:
    """
    Lê uma instância do ALWABP da entrada padrão
    
    Formato:
    - Linha 1: n (número de tarefas)
    - Linhas 2 até n+1: matriz de tempos (n x k)
    - Linhas seguintes: pares (i, j) de precedências
    - Última linha: -1 -1
    
    Returns:
        Instância do ALWABP
    """
    # Ler todas as linhas não vazias (removendo BOM se presente)
    lines = [line.strip() for line in sys.stdin if line.strip()]
    
    # Ler número de tarefas (removendo BOM se presente)
    n = int(lines[0].lstrip('\ufeff'))
    idx = 1
    
    times = []
    
    # Ler primeira linha da matriz para descobrir k (número de trabalhadores)
    first_row_tokens = lines[idx].split()
    k = len(first_row_tokens)
    
    # Ler primeira linha
    row = [parse_value(x) for x in first_row_tokens]
    times.append(row)
    idx += 1
    
    # Ler as demais n-1 linhas da matriz de tempos
    for _ in range(n - 1):
        parts = lines[idx].split()
        row = [parse_value(x) for x in parts]
        times.append(row)
        idx += 1
    
    # Ler precedências
    precedences = []
    while idx < len(lines):
        parts = lines[idx].split()
        i, j = int(parts[0]), int(parts[1])
        if i == -1 and j == -1:
            break
        precedences.append((i, j))
        idx += 1
    
    # Criar instância
    # Nota: O formato usa índices 1-based, mas internamente usamos 0-based
    instance = ALWABPInstance(n_tasks=n, n_workers=k, n_stations=k)
    
    # Converter matriz de tempos para formato interno (workers x tasks)
    # Input: times[tarefa][trabalhador] (0-based após conversão)
    # Interno: execution_times[worker][task]
    execution_times = np.zeros((k, n), dtype=float)
    for task in range(n):
        for worker in range(k):
            time_val = times[task][worker]
            execution_times[worker][task] = time_val
            
            # Se for infinito, marcar como incompatível
            if math.isinf(time_val):
                instance.set_incompatible_task(worker, task)
    
    instance.execution_times = execution_times
    
    # Adicionar precedências (converter de 1-based para 0-based)
    for i, j in precedences:
        instance.add_precedence(i - 1, j - 1)
    
    return instance


def read_instance_from_file(filename: str) -> ALWABPInstance:
    """
    Lê uma instância do ALWABP de um arquivo
    
    Args:
        filename: caminho do arquivo
        
    Returns:
        Instância do ALWABP
    """
    with open(filename, 'r') as f:
        # Redirecionar stdin temporariamente
        old_stdin = sys.stdin
        sys.stdin = f
        
        try:
            instance = read_instance_from_stdin()
        finally:
            sys.stdin = old_stdin
    
    return instance


if __name__ == "__main__":
    # Teste: ler da entrada padrão
    instance = read_instance_from_stdin()
    
    print(f"Instância lida:")
    print(f"  Tarefas: {instance.n_tasks}")
    print(f"  Trabalhadores: {instance.n_workers}")
    print(f"  Estações: {instance.n_stations}")
    print(f"  Precedências: {len(instance.precedences)}")
    
    # Contar incompatibilidades
    total_incomp = sum(len(s) for s in instance.incompatible_tasks)
    print(f"  Incompatibilidades: {total_incomp}")
