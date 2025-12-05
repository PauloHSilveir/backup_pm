"""
Módulo para representação e leitura de instâncias do ALWABP
(Assembly Line Worker Assignment and Balancing Problem)
"""

import numpy as np
from typing import List, Set, Tuple


class ALWABPInstance:
    """Classe para representar uma instância do ALWABP"""
    
    def __init__(self, n_tasks: int, n_stations: int, n_workers: int):
        """
        Inicializa uma instância do ALWABP
        
        Args:
            n_tasks: número de tarefas
            n_stations: número de estações
            n_workers: número de trabalhadores
        """
        self.n_tasks = n_tasks
        self.n_stations = n_stations
        self.n_workers = n_workers
        
        # Matriz de tempos de execução: execution_times[w][i] = tempo do trabalhador w na tarefa i
        self.execution_times = np.zeros((n_workers, n_tasks))
        
        # Precedências: lista de tuplas (i, j) onde i precede j
        self.precedences: List[Tuple[int, int]] = []
        
        # Tarefas que cada trabalhador não pode executar
        self.incompatible_tasks: List[Set[int]] = [set() for _ in range(n_workers)]
        
    def add_precedence(self, task_i: int, task_j: int):
        """Adiciona uma relação de precedência entre tarefas"""
        self.precedences.append((task_i, task_j))
        
    def set_execution_time(self, worker: int, task: int, time: float):
        """Define o tempo de execução de uma tarefa por um trabalhador"""
        self.execution_times[worker][task] = time
        
    def set_incompatible_task(self, worker: int, task: int):
        """Marca uma tarefa como incompatível com um trabalhador"""
        self.incompatible_tasks[worker].add(task)
        self.execution_times[worker][task] = np.inf
        
    def get_precedence_matrix(self) -> np.ndarray:
        """
        Retorna matriz de precedências onde prec[i][j] = 1 se i precede j
        """
        prec_matrix = np.zeros((self.n_tasks, self.n_tasks), dtype=int)
        for i, j in self.precedences:
            prec_matrix[i][j] = 1
        
        # Calcular fechamento transitivo
        for k in range(self.n_tasks):
            for i in range(self.n_tasks):
                for j in range(self.n_tasks):
                    prec_matrix[i][j] = prec_matrix[i][j] or (prec_matrix[i][k] and prec_matrix[k][j])
        
        return prec_matrix
    
    def read_from_file(self, filename: str):
        """Lê instância de um arquivo"""
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Implementar leitura conforme formato do arquivo
        # Este é um exemplo básico que precisa ser adaptado ao formato real
        pass
