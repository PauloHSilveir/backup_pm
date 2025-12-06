"""
Módulo com decodificadores de chaves aleatórias para soluções do ALWABP
"""

import numpy as np
from typing import List
from .alwabp_instance import ALWABPInstance
from .alwabp_solution import ALWABPSolution
from .repair import repair_solution


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
        
        # Decodificar atribuição de trabalhadores
        # IMPORTANTE: garantir que TODOS os workers sejam atribuídos exatamente uma vez
        worker_priority = np.argsort(worker_keys)[::-1]
        
        # Se n_workers == n_stations, atribuir diretamente
        if n_workers == n_stations:
            solution.worker_assignment = worker_priority.copy()
        else:
            # Se n_workers > n_stations, pegar os top n_stations
            # Se n_workers < n_stations, repetir workers (menos comum)
            solution.worker_assignment = worker_priority[:n_stations] % n_workers
        
        # Decodificar atribuição de tarefas respeitando precedências
        solution.task_assignment = self._decode_tasks_with_precedence(task_keys, solution.worker_assignment)
        
        # Aplicar repair para garantir factibilidade (resolve violações de precedência)
        solution = repair_solution(solution)
        
        return solution
    
    def _decode_tasks_with_precedence(self, task_keys: np.ndarray, worker_assignment: np.ndarray) -> np.ndarray:
        """
        Decodifica tarefas usando ordem topológica.
        O repair posterior garante 100% de factibilidade.
        
        Args:
            task_keys: chaves aleatórias (definem prioridade das tarefas)
            worker_assignment: workers atribuídos às estações
            
        Returns:
            Atribuição inicial de tarefas (pode ter violações de precedência)
        """
        n_tasks = self.instance.n_tasks
        n_stations = self.instance.n_stations
        prec_matrix = self.instance.get_precedence_matrix()
        in_degree = np.sum(prec_matrix, axis=0).astype(int)
        
        task_assignment = np.zeros(n_tasks, dtype=int)
        ready = [t for t in range(n_tasks) if in_degree[t] == 0]
        
        while ready:
            # Ordenar por prioridade (task_keys maiores = maior prioridade)
            ready.sort(key=lambda t: task_keys[t], reverse=True)
            task = ready.pop(0)
            
            # Estação mínima (respeitando predecessoras já atribuídas)
            preds = np.where(prec_matrix[:, task] == 1)[0]
            min_st = max(task_assignment[p] for p in preds) if len(preds) > 0 else 0
            
            # Procurar primeira estação compatível
            assigned = False
            for st in range(min_st, n_stations):
                w = worker_assignment[st]
                if task not in self.instance.incompatible_tasks[w] and not np.isinf(self.instance.execution_times[w][task]):
                    task_assignment[task] = st
                    assigned = True
                    break
            
            # Se não achou respeitando precedências, atribuir a qualquer estação compatível
            if not assigned:
                for st in range(n_stations):
                    w = worker_assignment[st]
                    if task not in self.instance.incompatible_tasks[w] and not np.isinf(self.instance.execution_times[w][task]):
                        task_assignment[task] = st
                        break
            
            # Atualizar sucessoras
            for succ in np.where(prec_matrix[task, :] == 1)[0]:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    ready.append(succ)
        
        return task_assignment
    
    def encode(self, solution: ALWABPSolution) -> np.ndarray:
        """
        Codifica uma solução de volta em um cromossomo de chaves aleatórias
        
        Args:
            solution: solução a ser codificada
            
        Returns:
            Cromossomo (chaves aleatórias)
        """
        n_tasks = self.instance.n_tasks
        n_workers = self.instance.n_workers
        
        chromosome = np.zeros(n_tasks + n_workers)
        
        # Codificar tarefas: atribuir chaves baseadas na ordem de estação e posição
        # Tarefas em estações menores recebem chaves maiores
        for task in range(n_tasks):
            station = solution.task_assignment[task]
            # Chave inversamente proporcional à estação (estação 0 = chave alta)
            base_key = 1.0 - (station / self.instance.n_stations)
            # Adicionar pequena perturbação para manter ordem dentro da estação
            chromosome[task] = base_key + np.random.uniform(-0.1, 0.1) / self.instance.n_stations
        
        # Codificar trabalhadores: ordem de atribuição às estações
        for station in range(self.instance.n_stations):
            worker = solution.worker_assignment[station]
            # Trabalhador na estação 0 tem chave maior
            chromosome[n_tasks + worker] = 1.0 - (station / self.instance.n_stations)
        
        # Normalizar para [0, 1]
        chromosome = np.clip(chromosome, 0.0, 1.0)
        
        return chromosome
