"""
Reparo de soluções para garantir factibilidade
"""

import numpy as np
from .alwabp_solution import ALWABPSolution


def repair_solution(solution: ALWABPSolution, task_priorities: np.ndarray = None) -> ALWABPSolution:
    """
    Reconstrói atribuição de tarefas PRESERVANDO prioridades dos decoders COM ALEATORIEDADE.
    
    IMPORTANTE: Esta abordagem BALANCEIA diversidade e factibilidade.
    - Ordena tarefas por prioridades COM RUÍDO aleatório para quebrar empates
    - Adiciona aleatoriedade na escolha de estações
    - Mantém respeito a precedências básicas
    - Permite exploração do espaço de busca sem destruir completamente a factibilidade
    
    Args:
        solution: solução com worker_assignment definido
        task_priorities: array opcional com prioridades das tarefas (maior = mais prioritária)
        
    Returns:
        Solução reparada com variação estocástica
    """
    instance = solution.instance
    prec_matrix = instance.get_precedence_matrix()
    in_degree = np.sum(prec_matrix, axis=0).astype(int)
    
    # Se não forneceu prioridades, usar ordem natural COM RUÍDO
    if task_priorities is None:
        task_priorities = np.arange(instance.n_tasks, dtype=float) + np.random.rand(instance.n_tasks) * 0.3
    
    task_assignment = np.zeros(instance.n_tasks, dtype=int)
    station_loads = np.zeros(instance.n_stations)  # Balanceamento de carga
    ready = [t for t in range(instance.n_tasks) if in_degree[t] == 0]
    
    while ready:
        # ORDENAR POR PRIORIDADE + RUÍDO ALEATÓRIO para quebrar empates deterministicamente
        # Ruído pequeno (0-0.2) mantém ordem geral mas adiciona variação
        noise = np.random.rand(len(ready)) * 0.2
        ready_with_priority = [(t, task_priorities[t] + noise[i]) for i, t in enumerate(ready)]
        ready_with_priority.sort(key=lambda x: x[1], reverse=True)
        
        task = ready_with_priority[0][0]
        ready.remove(task)
        
        # Estação mínima (respeitando predecessoras)
        preds = np.where(prec_matrix[:, task] == 1)[0]
        min_st = max(task_assignment[p] for p in preds) if len(preds) > 0 else 0
        
        # BALANCEAMENTO COM ALEATORIEDADE: escolher estação com carga baixa + fator aleatório
        valid_stations = []
        
        for st in range(min_st, instance.n_stations):
            w = solution.worker_assignment[st]
            if task in instance.incompatible_tasks[w] or np.isinf(instance.execution_times[w][task]):
                continue
            
            task_time = instance.execution_times[w][task]
            new_load = station_loads[st] + task_time
            valid_stations.append((st, new_load))
        
        # Se encontrou estações válidas, escolher com probabilidade inversamente proporcional à carga
        if valid_stations:
            # Adicionar ruído aleatório para não sempre escolher a menor carga
            if np.random.rand() < 0.3:  # 30% de chance de escolha aleatória
                best_station = valid_stations[np.random.randint(len(valid_stations))][0]
            else:
                # 70% de chance de escolher estação com menor carga
                best_station = min(valid_stations, key=lambda x: x[1])[0]
        else:
            best_station = -1
        
        # Fallback: sem estação compatível respeitando precedências
        if best_station == -1:
            for st in range(instance.n_stations):
                w = solution.worker_assignment[st]
                if task not in instance.incompatible_tasks[w] and not np.isinf(instance.execution_times[w][task]):
                    best_station = st
                    break
        
        if best_station != -1:
            task_assignment[task] = best_station
            w = solution.worker_assignment[best_station]
            if not np.isinf(instance.execution_times[w][task]):
                station_loads[best_station] += instance.execution_times[w][task]
        
        # Atualizar sucessoras
        for succ in np.where(prec_matrix[task, :] == 1)[0]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                ready.append(succ)
    
    solution.task_assignment = task_assignment
    solution.calculate_cycle_time()
    return solution
