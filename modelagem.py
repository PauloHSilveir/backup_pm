import sys
from gurobipy import Model, GRB, quicksum
import math

# 1) Ler todas as linhas não vazias (removendo BOM se presente)
lines = [line.strip() for line in sys.stdin if line.strip()]

# ler o número de tarefas (removendo BOM se presente)
n = int(lines[0].lstrip('\ufeff'))
idx = 1

times = []

# ler matriz de tempos
first_row_tokens = lines[idx].split()
k = len(first_row_tokens)

def parse_value(v):
    if v.lower() == "inf": return math.inf
    return float(v)

# ler primeira linha
row = [parse_value(x) for x in first_row_tokens]
times.append(row)
idx += 1

# ler as demais n-1 linhas
for _ in range(n - 1):
    parts = lines[idx].split()
    row = [parse_value(x) for x in parts]
    times.append(row)
    idx += 1

# agora ler precedências
precedence = []

while idx < len(lines):
    parts = lines[idx].split()
    i, j = int(parts[0]), int(parts[1])
    if i == -1 and j == -1:
        break
    precedence.append((i, j))
    idx += 1

N = list(range(1, n+1))
W = list(range(1, k+1))
S = list(range(1, k+1))

# 2) Preparar dados para Gurobi

# T_wi[(w,i)] = tempo
T_wi = {}
for i in N:
    for w in W:
        T_wi[(w, i)] = times[i-1][w-1]

# sem incapacidade
I_w = {w: set() for w in W}

# 3) Modelo 

model = Model("ALWABP")
model.setParam('OutputFlag', 0)

# x[i,s]
x = {(i, s): model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{s}") for i in N for s in S}

# z[w,s]
z = {(w, s): model.addVar(vtype=GRB.BINARY, name=f"z_{w}_{s}") for w in W for s in S}

# y[i,s,w] - apenas para combinações válidas (tempo finito)
y = {}
for i in N:
    for s in S:
        for w in W:
            if T_wi[(w, i)] != math.inf:
                y[(i, s, w)] = model.addVar(vtype=GRB.BINARY, name=f"y_{i}_{s}_{w}")

C = model.addVar(vtype=GRB.CONTINUOUS, lb=0)

model.update()

# 4) Restrições

# cada tarefa exatamente em uma estação
for i in N:
    model.addConstr(quicksum(x[i, s] for s in S) == 1)

# cada trabalhador em exatamente uma estação
for w in W:
    model.addConstr(quicksum(z[w, s] for s in S) == 1)

# cada estação com exatamente 1 trabalhador
for s in S:
    model.addConstr(quicksum(z[w, s] for w in W) == 1)

# ligação y-x-z (apenas para y válidos)
for i in N:
    for s in S:
        for w in W:
            if (i, s, w) in y:
                model.addConstr(y[(i, s, w)] <= x[i, s])
                model.addConstr(y[(i, s, w)] <= z[w, s])
                model.addConstr(y[(i, s, w)] >= x[i, s] + z[w, s] - 1)

# cada tarefa executada por exatamente um trabalhador
for i in N:
    model.addConstr(quicksum(y[(i, s, w)] for s in S for w in W if (i, s, w) in y) == 1)

# carga da estação
for s in S:
    expr = quicksum(T_wi[(w, i)] * y[(i, s, w)] for i in N for w in W if (i, s, w) in y)
    model.addConstr(expr <= C)

# precedências
for (i, j) in precedence:
    model.addConstr(quicksum(s * x[i, s] for s in S) <= quicksum(s * x[j, s] for s in S))

# 5) Objetivo

model.setObjective(C, GRB.MINIMIZE)
model.optimize()

# 6) Output

if model.Status != GRB.OPTIMAL:
    print("Nenhuma solução ótima encontrada.")
    sys.exit(0)

# Estação -> trabalhador
station_worker = {s: None for s in S}
for w in W:
    for s in S:
        if z[w, s].X > 0.5:
            station_worker[s] = w

# Estação -> tarefas
station_tasks = {s: [] for s in S}
station_load = {s: 0.0 for s in S}

for i in N:
    for s in S:
        if x[i, s].X > 0.5:
            station_tasks[s].append(i)
            # calcular carga usando o trabalhador da estação
            w = station_worker[s]
            station_load[s] += T_wi[(w, i)]

# PRINTAR RESULTADO

print("digraph Resultado {")
for s in S:
    w = station_worker[s]
    tasks = station_tasks[s]
    load = station_load[s]

    print(f'  station{s} [label="Estação {s}\\nTrabalhador: {w}\\nCarga: {load:.2f}"];')

    for t in tasks:
        print(f'  task{t} [label="Tarefa {t}"];')
        print(f'  station{s} -> task{t};')

print(f'  C[label="Ciclo ótimo: {C.X:.2f}"];')
print("}")