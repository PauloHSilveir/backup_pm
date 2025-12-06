"""
Módulo para representação de soluções do ALWABP
"""

import numpy as np
from typing import List
from .alwabp_instance import ALWABPInstance


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
        
    def is_feasible(self, verbose=False) -> bool:
        """
        Verifica se a solução é factível (todas as restrições do modelo)
        
        Args:
            verbose: se True, imprime detalhes das violações
            
        Returns:
            True se a solução é factível, False caso contrário
        """
        
        # RESTRIÇÃO 1: Cada tarefa em exatamente uma estação
        # Equivalente: sum(x[i,s] for s in S) == 1
        for i in range(self.instance.n_tasks):
            if self.task_assignment[i] < 0 or self.task_assignment[i] >= self.instance.n_stations:
                if verbose:
                    print(f"[R1] Tarefa {i} não atribuída ou fora dos limites: {self.task_assignment[i]}")
                return False
        
        # Verificar se cada tarefa aparece exatamente uma vez
        task_counts = np.bincount(self.task_assignment, minlength=self.instance.n_stations)
        if len(self.task_assignment) != self.instance.n_tasks:
            if verbose:
                print(f"[R1] Número de tarefas incorreto: {len(self.task_assignment)} != {self.instance.n_tasks}")
            return False
        
        # RESTRIÇÃO 2: Cada trabalhador em exatamente uma estação
        # Equivalente: sum(z[w,s] for s in S) == 1
        if len(self.worker_assignment) != self.instance.n_stations:
            if verbose:
                print(f"[R2] Número de atribuições de trabalhadores incorreto: {len(self.worker_assignment)} != {self.instance.n_stations}")
            return False
        
        # RESTRIÇÃO 3: Cada estação com exatamente 1 trabalhador
        # Equivalente: sum(z[w,s] for w in W) == 1
        if len(set(self.worker_assignment)) != self.instance.n_workers:
            if verbose:
                unique_workers = set(self.worker_assignment)
                print(f"[R3] Trabalhadores duplicados ou faltando: {len(unique_workers)} únicos de {self.instance.n_workers}")
                print(f"     Workers atribuídos: {self.worker_assignment}")
            return False
        
        # Verificar se todos os workers estão no range válido
        for w in self.worker_assignment:
            if w < 0 or w >= self.instance.n_workers:
                if verbose:
                    print(f"[R3] Trabalhador {w} fora dos limites")
                return False
        
        # RESTRIÇÃO 4: Ligação y-x-z e cada tarefa executada por exatamente um trabalhador
        # Equivalente: sum(y[i,s,w] for s,w) == 1 e y[i,s,w] válido apenas se x[i,s]=1 e z[w,s]=1
        for i in range(self.instance.n_tasks):
            station = self.task_assignment[i]
            worker = self.worker_assignment[station]
            
            # Verificar se tempo é finito (tarefa pode ser executada pelo trabalhador)
            if np.isinf(self.instance.execution_times[worker][i]):
                if verbose:
                    print(f"[R4] Tempo infinito: trabalhador {worker} (estação {station}) não pode executar tarefa {i}")
                return False
            
            # Verificar incompatibilidades
            if i in self.instance.incompatible_tasks[worker]:
                if verbose:
                    print(f"[R4] Incompatibilidade: trabalhador {worker} na estação {station} não pode executar tarefa {i}")
                return False
        
        # RESTRIÇÃO 5: Precedências
        # Equivalente: sum(s*x[i,s]) <= sum(s*x[j,s]) para i precede j
        prec_matrix = self.instance.get_precedence_matrix()
        for i in range(self.instance.n_tasks):
            for j in range(self.instance.n_tasks):
                if prec_matrix[i][j] == 1:
                    if self.task_assignment[i] > self.task_assignment[j]:
                        if verbose:
                            print(f"[R5] Precedência violada: tarefa {i} (estação {self.task_assignment[i]}) deve vir antes de tarefa {j} (estação {self.task_assignment[j]})")
                        return False
        
        # RESTRIÇÃO 6: Carga da estação <= C (tempo de ciclo)
        # Verificado implicitamente no calculate_cycle_time, mas vamos garantir consistência
        self.calculate_cycle_time()
        for station in range(self.instance.n_stations):
            if self.station_times[station] > self.cycle_time + 1e-6:  # tolerância numérica
                if verbose:
                    print(f"[R6] Carga da estação {station} ({self.station_times[station]:.2f}) > tempo de ciclo ({self.cycle_time:.2f})")
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
