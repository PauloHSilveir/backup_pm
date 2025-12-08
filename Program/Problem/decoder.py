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
        
        # Estratégias adaptativas (0=balanced, 1=forward, 2=backward)
        self.strategy_weights = np.ones(3)
        self.strategy_success = np.zeros(3)
        self.strategy_attempts = np.zeros(3)
        
    def decode(self, chromosome: np.ndarray, strategy: int = None) -> ALWABPSolution:
        """
        Decodifica um cromossomo (chaves aleatórias) em uma solução do ALWABP
        Usa múltiplas estratégias adaptativas para melhor exploração
        
        O cromossomo possui:
        - n_tasks genes para ordem de atribuição das tarefas
        - n_workers genes para ordem de atribuição dos trabalhadores
        
        Args:
            chromosome: array com chaves aleatórias [0, 1]
            strategy: estratégia específica (0=balanced, 1=forward, 2=backward, None=adaptativa)
            
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
        worker_priority = np.argsort(worker_keys)[::-1]
        if n_workers == n_stations:
            solution.worker_assignment = worker_priority.copy()
        else:
            solution.worker_assignment = worker_priority[:n_stations] % n_workers
        
        # Selecionar estratégia (adaptativa se não especificada)
        if strategy is None:
            strategy_probs = self.strategy_weights / np.sum(self.strategy_weights)
            strategy = np.random.choice(3, p=strategy_probs)
        
        self.strategy_attempts[strategy] += 1
        
        # Decodificar tarefas com estratégia selecionada
        if strategy == 0:
            task_assignment, priorities = self._decode_balanced(task_keys, solution.worker_assignment)
            solution.task_assignment = task_assignment
        elif strategy == 1:
            task_assignment, priorities = self._decode_forward(task_keys, solution.worker_assignment)
            solution.task_assignment = task_assignment
        else:  # strategy == 2
            task_assignment, priorities = self._decode_backward(task_keys, solution.worker_assignment)
            solution.task_assignment = task_assignment
        
        # Aplicar reparo para garantir factibilidade, preservando prioridades
        solution = repair_solution(solution, task_priorities=priorities)
        
        return solution
    
    def _decode_balanced(self, task_keys: np.ndarray, worker_assignment: np.ndarray) -> np.ndarray:
        """
        Estratégia 0: Balanceamento de carga entre estações
        Considera tempos de execução para distribuir carga uniformemente
        
        Args:
            task_keys: chaves aleatórias (definem prioridade das tarefas)
            worker_assignment: workers atribuídos às estações
            
        Returns:
            Atribuição de tarefas
        """
        n_tasks = self.instance.n_tasks
        n_stations = self.instance.n_stations
        prec_matrix = self.instance.get_precedence_matrix()
        in_degree = np.sum(prec_matrix, axis=0).astype(int)
        
        task_assignment = np.zeros(n_tasks, dtype=int)
        station_loads = np.zeros(n_stations)  # Rastrear carga de cada estação
        ready = [t for t in range(n_tasks) if in_degree[t] == 0]
        
        while ready:
            # Ordenar por prioridade (task_keys maiores = maior prioridade)
            ready.sort(key=lambda t: task_keys[t], reverse=True)
            task = ready.pop(0)
            
            # Estação mínima (respeitando predecessoras já atribuídas)
            preds = np.where(prec_matrix[:, task] == 1)[0]
            min_st = max(task_assignment[p] for p in preds) if len(preds) > 0 else 0
            
            # Procurar estação com menor carga
            best_station = -1
            best_load = float('inf')
            
            for st in range(min_st, n_stations):
                w = worker_assignment[st]
                if task in self.instance.incompatible_tasks[w] or np.isinf(self.instance.execution_times[w][task]):
                    continue
                
                task_time = self.instance.execution_times[w][task]
                new_load = station_loads[st] + task_time
                
                if new_load < best_load:
                    best_load = new_load
                    best_station = st
            
            # Fallback: qualquer estação compatível
            if best_station == -1:
                for st in range(n_stations):
                    w = worker_assignment[st]
                    if task not in self.instance.incompatible_tasks[w] and not np.isinf(self.instance.execution_times[w][task]):
                        best_station = st
                        break
            
            if best_station == -1:
                best_station = n_stations - 1  # Última estação como último recurso
            
            task_assignment[task] = best_station
            w = worker_assignment[best_station]
            if not np.isinf(self.instance.execution_times[w][task]):
                station_loads[best_station] += self.instance.execution_times[w][task]
            
            # Atualizar sucessoras
            for succ in np.where(prec_matrix[task, :] == 1)[0]:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    ready.append(succ)
        
        # Retornar assignment E prioridades (task_keys)
        return task_assignment, task_keys
    
    def _decode_forward(self, task_keys: np.ndarray, worker_assignment: np.ndarray) -> tuple:
        """
        Estratégia 1: Alocação forward gulosa  
        Considera precedências fortemente, aloca da frente para trás
        Retorna assignment inicial E prioridades baseadas em nível topológico
        """
        n_tasks = self.instance.n_tasks
        prec_matrix = self.instance.get_precedence_matrix()
        in_degree = np.sum(prec_matrix, axis=0).astype(int)
        
        # Calcular nível topológico de cada tarefa
        topological_level = np.zeros(n_tasks, dtype=int)
        temp_in_degree = in_degree.copy()
        ready = [t for t in range(n_tasks) if temp_in_degree[t] == 0]
        
        while ready:
            task = ready.pop(0)
            for succ in np.where(prec_matrix[task, :] == 1)[0]:
                topological_level[succ] = max(topological_level[succ], topological_level[task] + 1)
                temp_in_degree[succ] -= 1
                if temp_in_degree[succ] == 0:
                    ready.append(succ)
        
        # Prioridades: combinar nível topológico (normalizado) com task_keys
        # Tarefas no início da cadeia têm maior prioridade
        max_level = np.max(topological_level) if np.max(topological_level) > 0 else 1
        priorities = (1.0 - topological_level / max_level) + task_keys
        
        # Gerar assignment inicial simples
        task_assignment = np.zeros(n_tasks, dtype=int)
        ready = [t for t in range(n_tasks) if in_degree[t] == 0]
        ready.sort(key=lambda t: task_keys[t], reverse=True)
        
        while ready:
            task = ready.pop(0)
            preds = np.where(prec_matrix[:, task] == 1)[0]
            min_st = max(task_assignment[p] for p in preds) if len(preds) > 0 else 0
            
            for st in range(min_st, self.instance.n_stations):
                w = worker_assignment[st]
                if task not in self.instance.incompatible_tasks[w] and not np.isinf(self.instance.execution_times[w][task]):
                    task_assignment[task] = st
                    break
            
            for succ in np.where(prec_matrix[task, :] == 1)[0]:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    ready.append(succ)
                    ready.sort(key=lambda t: task_keys[t], reverse=True)
        
        return task_assignment, priorities
    
    def _decode_backward(self, task_keys: np.ndarray, worker_assignment: np.ndarray) -> tuple:
        """
        Estratégia 2: Alocação backward
        Aloca de trás para frente considerando sucessores
        Retorna assignment inicial E prioridades baseadas em nível reverso
        """
        n_tasks = self.instance.n_tasks
        prec_matrix = self.instance.get_precedence_matrix()
        in_degree = np.sum(prec_matrix, axis=0).astype(int)
        
        # Calcular nível reverso (distância do final)
        reverse_level = np.zeros(n_tasks, dtype=int)
        # Começar das tarefas sem sucessores
        has_successors = np.sum(prec_matrix, axis=1) > 0
        
        # Algoritmo de nível reverso
        for task in range(n_tasks):
            successors = np.where(prec_matrix[task, :] == 1)[0]
            if len(successors) > 0:
                reverse_level[task] = max(reverse_level[s] for s in successors) + 1
        
        # Prioridades: tarefas no final da cadeia têm maior prioridade
        max_level = np.max(reverse_level) if np.max(reverse_level) > 0 else 1
        priorities = (reverse_level / max_level) + (1.0 - task_keys)
        
        # Gerar assignment inicial simples
        task_assignment = np.zeros(n_tasks, dtype=int)
        ready = [t for t in range(n_tasks) if in_degree[t] == 0]
        ready.sort(key=lambda t: task_keys[t])
        
        while ready:
            task = ready.pop(0)
            preds = np.where(prec_matrix[:, task] == 1)[0]
            min_st = max(task_assignment[p] for p in preds) if len(preds) > 0 else 0
            
            for st in range(min_st, self.instance.n_stations):
                w = worker_assignment[st]
                if task not in self.instance.incompatible_tasks[w] and not np.isinf(self.instance.execution_times[w][task]):
                    task_assignment[task] = st
                    break
            
            for succ in np.where(prec_matrix[task, :] == 1)[0]:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    ready.append(succ)
                    ready.sort(key=lambda t: task_keys[t])
        
        return task_assignment, priorities
    
    def update_strategy_weights(self, improved: bool, strategy: int):
        """Atualiza pesos das estratégias baseado em sucesso"""
        if improved:
            self.strategy_success[strategy] += 1
        
        # Recalcular pesos periodicamente
        if np.sum(self.strategy_attempts) % 50 == 0 and np.sum(self.strategy_attempts) > 0:
            success_rates = self.strategy_success / (self.strategy_attempts + 1e-10)
            self.strategy_weights = 0.7 * self.strategy_weights + 0.3 * success_rates
            self.strategy_weights = np.maximum(self.strategy_weights, 0.1)
    
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
