"""
Módulo com decodificadores de chaves aleatórias para soluções do ALWABP
"""

import numpy as np
from typing import List
from alwabp_instance import ALWABPInstance
from alwabp_solution import ALWABPSolution


class RandomKeyDecoder:
    """Decodificador de chaves aleatórias para o ALWABP"""
    
    def __init__(self, instance: ALWABPInstance):
        """
        Inicializa o decodificador
        
        Args:
            instance: instância do problema
        """
        self.instance = instance
        
    def decode(self, chromosome: np.ndarray) -> ALWABPSolution:
        """
        Decodifica um cromossomo (chaves aleatórias) em uma solução do ALWABP
        
        O cromossomo possui:
        - n_tasks genes para ordem de atribuição das tarefas
        - n_workers genes para ordem de atribuição dos trabalhadores
        
        Args:
            chromosome: array com chaves aleatórias [0, 1]
            
        Returns:
            Solução decodificada
        """
        n_tasks = self.instance.n_tasks
        n_workers = self.instance.n_workers
        n_stations = self.instance.n_stations
        
        # Dividir cromossomo
        task_keys = chromosome[:n_tasks]
        worker_keys = chromosome[n_tasks:n_tasks + n_workers]
        
        # Criar solução
        solution = ALWABPSolution(self.instance)
        
        # Decodificar atribuição de trabalhadores (ordem de prioridade)
        worker_priority = np.argsort(worker_keys)[::-1]  # Maiores valores = maior prioridade
        solution.worker_assignment = worker_priority[:n_stations]
        
        # Decodificar atribuição de tarefas respeitando precedências
        solution.task_assignment = self._decode_tasks_with_precedence(task_keys, solution.worker_assignment)
        
        # Calcular tempo de ciclo
        solution.calculate_cycle_time()
        
        return solution
    
    def _decode_tasks_with_precedence(self, task_keys: np.ndarray, worker_assignment: np.ndarray) -> np.ndarray:
        """
        Decodifica as tarefas respeitando precedências e incompatibilidades
        
        Args:
            task_keys: chaves aleatórias das tarefas
            worker_assignment: atribuição de trabalhadores às estações
            
        Returns:
            Array com atribuição de tarefas às estações
        """
        n_tasks = self.instance.n_tasks
        n_stations = self.instance.n_stations
        
        # Ordenar tarefas por prioridade (valores das chaves)
        task_priority = np.argsort(task_keys)[::-1]
        
        # Atribuição de tarefas
        task_assignment = np.zeros(n_tasks, dtype=int)
        station_times = np.zeros(n_stations)
        
        # Matriz de precedências
        prec_matrix = self.instance.get_precedence_matrix()
        
        # Para cada tarefa em ordem de prioridade
        for task in task_priority:
            best_station = None
            best_time = np.inf
            
            # Tentar atribuir à estação que minimiza o tempo de ciclo
            for station in range(n_stations):
                worker = worker_assignment[station]
                
                # Verificar incompatibilidade
                if task in self.instance.incompatible_tasks[worker]:
                    continue
                
                # Verificar precedências
                precedence_ok = True
                for prev_task in range(n_tasks):
                    if prec_matrix[prev_task][task] == 1:
                        if task_assignment[prev_task] > station:
                            precedence_ok = False
                            break
                
                if not precedence_ok:
                    continue
                
                # Calcular novo tempo da estação
                task_time = self.instance.execution_times[worker][task]
                new_station_time = station_times[station] + task_time
                
                # Escolher estação que resulta em menor tempo de ciclo
                if new_station_time < best_time:
                    best_time = new_station_time
                    best_station = station
            
            # Se nenhuma estação válida foi encontrada, forçar atribuição à última estação
            if best_station is None:
                # Tentar encontrar qualquer estação válida
                for station in range(n_stations):
                    worker = worker_assignment[station]
                    if task not in self.instance.incompatible_tasks[worker]:
                        # Verificar apenas precedências básicas
                        can_assign = True
                        for prev_task in range(task):
                            if prec_matrix[prev_task][task] == 1:
                                if task_assignment[prev_task] > station:
                                    can_assign = False
                                    break
                        if can_assign:
                            best_station = station
                            break
                
                # Última tentativa: atribuir à última estação possível
                if best_station is None:
                    best_station = n_stations - 1
            
            # Atribuir tarefa
            task_assignment[task] = best_station
            worker = worker_assignment[best_station]
            task_time = self.instance.execution_times[worker][task]
            station_times[best_station] += task_time
        
        return task_assignment
