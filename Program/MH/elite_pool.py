"""
Pool de soluções elite para manter diversidade e qualidade
"""

import numpy as np
from typing import List, Optional
from Program.Problem.alwabp_solution import ALWABPSolution


class ElitePool:
    """
    Mantém um conjunto de soluções elite de alta qualidade e diversas.
    Usado para restart inteligente e preservação de boas soluções.
    """
    
    def __init__(self, max_size: int = 10, min_distance: float = 0.15):
        """
        Args:
            max_size: tamanho máximo do pool
            min_distance: distância mínima entre soluções (0-1, baseada em diferenças)
        """
        self.solutions: List[ALWABPSolution] = []
        self.max_size = max_size
        self.min_distance = min_distance
    
    def add(self, solution: ALWABPSolution) -> bool:
        """
        Adiciona solução ao pool se for boa e suficientemente diferente.
        
        Args:
            solution: solução candidata
            
        Returns:
            True se adicionada, False caso contrário
        """
        # Se pool vazio, adicionar
        if len(self.solutions) == 0:
            self.solutions.append(solution.copy())
            return True
        
        # Verificar se é melhor que a pior do pool (quando pool cheio)
        if len(self.solutions) >= self.max_size:
            worst_fitness = max(s.cycle_time for s in self.solutions)
            if solution.cycle_time >= worst_fitness:
                return False
        
        # Verificar diversidade (distância mínima das existentes)
        for elite in self.solutions:
            distance = self._calculate_distance(solution, elite)
            if distance < self.min_distance:
                # Muito similar - manter apenas a melhor
                if solution.cycle_time < elite.cycle_time:
                    self.solutions.remove(elite)
                    break
                else:
                    return False
        
        # Adicionar solução
        self.solutions.append(solution.copy())
        
        # Se ultrapassou max_size, remover a pior
        if len(self.solutions) > self.max_size:
            worst_idx = max(range(len(self.solutions)), 
                          key=lambda i: self.solutions[i].cycle_time)
            self.solutions.pop(worst_idx)
        
        # Ordenar por qualidade
        self.solutions.sort(key=lambda s: s.cycle_time)
        
        return True
    
    def get_best(self) -> Optional[ALWABPSolution]:
        """Retorna melhor solução do pool"""
        if len(self.solutions) == 0:
            return None
        return self.solutions[0].copy()
    
    def get_random_elite(self) -> Optional[ALWABPSolution]:
        """Retorna elite aleatória (útil para perturbação/restart)"""
        if len(self.solutions) == 0:
            return None
        idx = np.random.randint(0, len(self.solutions))
        return self.solutions[idx].copy()
    
    def get_top_k(self, k: int) -> List[ALWABPSolution]:
        """Retorna k melhores soluções"""
        k = min(k, len(self.solutions))
        return [s.copy() for s in self.solutions[:k]]
    
    def size(self) -> int:
        """Retorna tamanho atual do pool"""
        return len(self.solutions)
    
    def is_empty(self) -> bool:
        """Verifica se pool está vazio"""
        return len(self.solutions) == 0
    
    def get_best_fitness(self) -> float:
        """Retorna fitness da melhor solução"""
        if len(self.solutions) == 0:
            return np.inf
        return self.solutions[0].cycle_time
    
    def _calculate_distance(self, sol1: ALWABPSolution, sol2: ALWABPSolution) -> float:
        """
        Calcula distância entre duas soluções (0 = idênticas, 1 = completamente diferentes)
        Considera diferenças em task_assignment e worker_assignment
        """
        instance = sol1.instance
        
        # Distância em task_assignment (proporção de tarefas em estações diferentes)
        task_diff = np.sum(sol1.task_assignment != sol2.task_assignment) / instance.n_tasks
        
        # Distância em worker_assignment (proporção de workers diferentes)
        worker_diff = np.sum(sol1.worker_assignment != sol2.worker_assignment) / instance.n_stations
        
        # Distância combinada (média ponderada)
        distance = 0.7 * task_diff + 0.3 * worker_diff
        
        return distance
    
    def __repr__(self) -> str:
        if len(self.solutions) == 0:
            return "ElitePool(vazio)"
        best = self.solutions[0].cycle_time
        worst = self.solutions[-1].cycle_time
        return f"ElitePool(size={len(self.solutions)}, best={best:.2f}, worst={worst:.2f})"
