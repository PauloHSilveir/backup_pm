"""
Módulo para representação de soluções do ALWABP
"""

import numpy as np
from typing import List
from alwabp_instance import ALWABPInstance


class ALWABPSolution:
    """Classe para representar uma solução do ALWABP"""
    
    def __init__(self, instance: ALWABPInstance):
        """
        Inicializa uma solução
        
        Args:
            instance: instância do problema
        """
        self.instance = instance
        
        # Atribuição de tarefas às estações: task_assignment[i] = estação da tarefa i
        self.task_assignment = np.zeros(instance.n_tasks, dtype=int)
        
        # Atribuição de trabalhadores às estações: worker_assignment[s] = trabalhador na estação s
        self.worker_assignment = np.zeros(instance.n_stations, dtype=int)
        
        # Tempo de ciclo (objetivo)
        self.cycle_time = np.inf
        
        # Tempos de cada estação
        self.station_times = np.zeros(instance.n_stations)
        
    def is_feasible(self) -> bool:
        """Verifica se a solução é factível"""
        
        # Verificar precedências
        prec_matrix = self.instance.get_precedence_matrix()
        for i in range(self.instance.n_tasks):
            for j in range(self.instance.n_tasks):
                if prec_matrix[i][j] == 1:
                    if self.task_assignment[i] > self.task_assignment[j]:
                        return False
        
        # Verificar incompatibilidades
        for station in range(self.instance.n_stations):
            worker = self.worker_assignment[station]
            tasks_in_station = np.where(self.task_assignment == station)[0]
            
            for task in tasks_in_station:
                if task in self.instance.incompatible_tasks[worker]:
                    return False
        
        # Verificar se cada trabalhador está em exatamente uma estação
        if len(set(self.worker_assignment)) != self.instance.n_workers:
            return False
        
        return True
    
    def calculate_cycle_time(self) -> float:
        """Calcula e atualiza o tempo de ciclo da solução"""
        self.station_times = np.zeros(self.instance.n_stations)
        
        for task in range(self.instance.n_tasks):
            station = self.task_assignment[task]
            worker = self.worker_assignment[station]
            task_time = self.instance.execution_times[worker][task]
            self.station_times[station] += task_time
        
        self.cycle_time = np.max(self.station_times)
        return self.cycle_time
    
    def copy(self) -> 'ALWABPSolution':
        """Cria uma cópia da solução"""
        new_sol = ALWABPSolution(self.instance)
        new_sol.task_assignment = self.task_assignment.copy()
        new_sol.worker_assignment = self.worker_assignment.copy()
        new_sol.cycle_time = self.cycle_time
        new_sol.station_times = self.station_times.copy()
        return new_sol
