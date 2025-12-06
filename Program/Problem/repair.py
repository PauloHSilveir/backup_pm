"""
Reparo de soluções para garantir factibilidade
"""

import numpy as np
from .alwabp_solution import ALWABPSolution


def repair_solution(solution: ALWABPSolution) -> ALWABPSolution:
    """
    Reconstrói atribuição de tarefas em ordem topológica para garantir factibilidade.
    
    Args:
        solution: solução com worker_assignment definido
        
    Returns:
        Solução factível
    """
    instance = solution.instance
    prec_matrix = instance.get_precedence_matrix()
    in_degree = np.sum(prec_matrix, axis=0).astype(int)
    
    task_assignment = np.zeros(instance.n_tasks, dtype=int)
    ready = [t for t in range(instance.n_tasks) if in_degree[t] == 0]
    
    while ready:
        task = ready.pop(0)
        
        # Estação mínima (respeitando predecessoras)
        preds = np.where(prec_matrix[:, task] == 1)[0]
        min_st = max(task_assignment[p] for p in preds) if len(preds) > 0 else 0
        
        # Procurar estação compatível
        for st in range(min_st, instance.n_stations):
            w = solution.worker_assignment[st]
            if task not in instance.incompatible_tasks[w] and not np.isinf(instance.execution_times[w][task]):
                task_assignment[task] = st
                break
        else:
            # Sem estação compatível respeitando precedências: procurar qualquer uma
            for st in range(instance.n_stations):
                w = solution.worker_assignment[st]
                if task not in instance.incompatible_tasks[w] and not np.isinf(instance.execution_times[w][task]):
                    task_assignment[task] = st
                    break
        
        # Atualizar sucessoras
        for succ in np.where(prec_matrix[task, :] == 1)[0]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                ready.append(succ)
    
    solution.task_assignment = task_assignment
    solution.calculate_cycle_time()
    return solution
