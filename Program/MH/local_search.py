"""
Módulo de busca local para o ALWABP
"""

import numpy as np
import sys
import os
from typing import List, Tuple
import random

# Adicionar diretório Problem ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Problem'))

from Program.Problem.alwabp_solution import ALWABPSolution
from Program.Problem.alwabp_instance import ALWABPInstance


class LocalSearch:
    """Implementa busca local para melhorar soluções do ALWABP"""
    
    def __init__(self, instance: ALWABPInstance):
        """
        Inicializa a busca local
        
        Args:
            instance: instância do problema
        """
        self.instance = instance
        
    def improve(self, solution: ALWABPSolution, max_iterations: int = 100) -> ALWABPSolution:
        """
        Aplica busca local para melhorar a solução
        
        Args:
            solution: solução inicial
            max_iterations: número máximo de iterações sem melhoria
            
        Returns:
            Solução melhorada
        """
        current_solution = solution.copy()
        current_solution.calculate_cycle_time()
        best_solution = current_solution.copy()
        
        iterations_without_improvement = 0
        
        while iterations_without_improvement < max_iterations:
            # Tentar movimento de troca de tarefas
            improved = self._try_task_swap(current_solution)
            
            if not improved:
                # Tentar movimento de troca de trabalhadores
                improved = self._try_worker_swap(current_solution)
            
            if not improved:
                # Tentar mover tarefa para outra estação
                improved = self._try_task_move(current_solution)
            
            if improved:
                current_solution.calculate_cycle_time()
                if current_solution.cycle_time < best_solution.cycle_time:
                    best_solution = current_solution.copy()
                    iterations_without_improvement = 0
                else:
                    iterations_without_improvement += 1
            else:
                iterations_without_improvement += 1
        
        return best_solution
    
    def _try_task_swap(self, solution: ALWABPSolution) -> bool:
        """
        Tenta trocar duas tarefas de estações diferentes
        
        Returns:
            True se houve melhoria
        """
        n_tasks = self.instance.n_tasks
        prec_matrix = self.instance.get_precedence_matrix()
        
        # Tentar todas as trocas possíveis
        tasks = list(range(n_tasks))
        random.shuffle(tasks)
        
        for i in tasks[:min(20, n_tasks)]:  # Limitar tentativas
            for j in tasks[:min(20, n_tasks)]:
                if i >= j:
                    continue
                
                station_i = solution.task_assignment[i]
                station_j = solution.task_assignment[j]
                
                if station_i == station_j:
                    continue
                
                # Verificar se troca mantém precedências
                if prec_matrix[i][j] == 1 or prec_matrix[j][i] == 1:
                    continue
                
                # Verificar outras precedências
                valid = True
                for k in range(n_tasks):
                    if k == i or k == j:
                        continue
                    
                    station_k = solution.task_assignment[k]
                    
                    # Verificar precedências envolvendo i
                    if prec_matrix[k][i] == 1 and station_k > station_j:
                        valid = False
                        break
                    if prec_matrix[i][k] == 1 and station_j > station_k:
                        valid = False
                        break
                    
                    # Verificar precedências envolvendo j
                    if prec_matrix[k][j] == 1 and station_k > station_i:
                        valid = False
                        break
                    if prec_matrix[j][k] == 1 and station_i > station_k:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Verificar incompatibilidades
                worker_i = solution.worker_assignment[station_i]
                worker_j = solution.worker_assignment[station_j]
                
                if j in self.instance.incompatible_tasks[worker_i]:
                    continue
                if i in self.instance.incompatible_tasks[worker_j]:
                    continue
                
                # Fazer troca
                old_cycle_time = solution.cycle_time
                solution.task_assignment[i] = station_j
                solution.task_assignment[j] = station_i
                solution.calculate_cycle_time()
                
                if solution.cycle_time < old_cycle_time:
                    return True
                else:
                    # Desfazer troca
                    solution.task_assignment[i] = station_i
                    solution.task_assignment[j] = station_j
                    solution.cycle_time = old_cycle_time
        
        return False
    
    def _try_worker_swap(self, solution: ALWABPSolution) -> bool:
        """
        Tenta trocar dois trabalhadores de estações diferentes
        
        Returns:
            True se houve melhoria
        """
        n_stations = self.instance.n_stations
        
        stations = list(range(n_stations))
        random.shuffle(stations)
        
        for s1 in stations[:min(10, n_stations)]:
            for s2 in stations[:min(10, n_stations)]:
                if s1 >= s2:
                    continue
                
                worker1 = solution.worker_assignment[s1]
                worker2 = solution.worker_assignment[s2]
                
                # Verificar incompatibilidades após troca
                tasks_s1 = np.where(solution.task_assignment == s1)[0]
                tasks_s2 = np.where(solution.task_assignment == s2)[0]
                
                valid = True
                for task in tasks_s1:
                    if task in self.instance.incompatible_tasks[worker2]:
                        valid = False
                        break
                
                if valid:
                    for task in tasks_s2:
                        if task in self.instance.incompatible_tasks[worker1]:
                            valid = False
                            break
                
                if not valid:
                    continue
                
                # Fazer troca
                old_cycle_time = solution.cycle_time
                solution.worker_assignment[s1] = worker2
                solution.worker_assignment[s2] = worker1
                solution.calculate_cycle_time()
                
                if solution.cycle_time < old_cycle_time:
                    return True
                else:
                    # Desfazer troca
                    solution.worker_assignment[s1] = worker1
                    solution.worker_assignment[s2] = worker2
                    solution.cycle_time = old_cycle_time
        
        return False
    
    def _try_task_move(self, solution: ALWABPSolution) -> bool:
        """
        Tenta mover uma tarefa para outra estação
        
        Returns:
            True se houve melhoria
        """
        n_tasks = self.instance.n_tasks
        n_stations = self.instance.n_stations
        prec_matrix = self.instance.get_precedence_matrix()
        
        tasks = list(range(n_tasks))
        random.shuffle(tasks)
        
        for task in tasks[:min(20, n_tasks)]:
            old_station = solution.task_assignment[task]
            
            stations = list(range(n_stations))
            random.shuffle(stations)
            
            for new_station in stations:
                if new_station == old_station:
                    continue
                
                # Verificar precedências
                valid = True
                for other_task in range(n_tasks):
                    if other_task == task:
                        continue
                    
                    other_station = solution.task_assignment[other_task]
                    
                    if prec_matrix[other_task][task] == 1 and other_station > new_station:
                        valid = False
                        break
                    if prec_matrix[task][other_task] == 1 and new_station > other_station:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Verificar incompatibilidade
                worker = solution.worker_assignment[new_station]
                if task in self.instance.incompatible_tasks[worker]:
                    continue
                
                # Fazer movimento
                old_cycle_time = solution.cycle_time
                solution.task_assignment[task] = new_station
                solution.calculate_cycle_time()
                
                if solution.cycle_time < old_cycle_time:
                    return True
                else:
                    # Desfazer movimento
                    solution.task_assignment[task] = old_station
                    solution.cycle_time = old_cycle_time
        
        return False
