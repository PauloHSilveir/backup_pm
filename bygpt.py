import sys
import random
import math

# ============================================================
# ========= LER INSTÂNCIA (exatamente igual ao gurobi) =======
# ============================================================
lines = [line.strip() for line in sys.stdin if line.strip()]
n = int(lines[0].lstrip('\ufeff'))
idx = 1

times = []
def parse_value(v):
    if v.lower() == "inf": return math.inf
    return float(v)

# Ler matriz de tempos
first_row = lines[idx].split()
k = len(first_row)
row = [parse_value(x) for x in first_row]
times.append(row)
idx += 1
for _ in range(n - 1):
    row = [parse_value(x) for x in lines[idx].split()]
    times.append(row)
    idx += 1

# Ler precedências
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

# ============================================================
# ========== PARÂMETROS DO BRKGA VIA LINHA DE COMANDO ========
# ============================================================
if len(sys.argv) < 4:
    print("Uso: python rko.py output.txt POP_SIZE MAX_GEN BIAS")
    sys.exit(0)

FILE_OUT = sys.argv[1]
POP_SIZE = int(sys.argv[2])
MAX_GEN  = int(sys.argv[3])
BIAS_PROB = float(sys.argv[4])  # prob de pegar gene do elite

ELITE_PERCENT = 0.20
MUTANT_PERCENT = 0.10

DIM = n   # tamanho do vetor random-key = número de tarefas


# ============================================================
# =================== DECODER RKO ============================
# ============================================================

def decoder(chrom):
    """
    chrom: vetor random-key
    Retorna:
      C      = tempo de ciclo
      assign = estação -> [tarefas]
    """

    # 1) Ordena tarefas por chave
    order = sorted(range(n), key=lambda i: chrom[i])

    # 2) Tenta alocar tarefas nas estações
    # Estratégia simples: cada estação pega um bloco em ordem
    # (isso pode ser melhorado depois)
    
    load = [0.0]*k        # carga por estação
    assign = [[] for _ in range(k)]
    station_worker = list(range(k))  # worker = índice igual por enquanto

    st = 0
    for ti in order:
        task = ti+1   # 1..n

        # tenta colocar na estação atual
        w = station_worker[st]
        t = times[task-1][w]

        # se tarefa impossível para este worker, pula
        if t == math.inf:
            # (melhor heurística futura = tentar outra estação)
            return math.inf, None

        # adiciona
        assign[st].append(task)
        load[st] += t

        # muda para próxima estação circular
        st = (st + 1) % k

    C = max(load)
    return C, assign


# ============================================================
# ===================== FITNESS ==============================
# ============================================================
def fitness(chrom):
    C, assign = decoder(chrom)
    return C


# ============================================================
# =================== POPULAÇÃO INICIAL ======================
# ============================================================
def random_chrom():
    return [random.random() for _ in range(DIM)]

population = [random_chrom() for _ in range(POP_SIZE)]


# ============================================================
# ====================== CROSSOVER ===========================
# ============================================================
def crossover(elite, nonelite):
    child = []
    for i in range(DIM):
        if random.random() < BIAS_PROB:
            child.append(elite[i])
        else:
            child.append(nonelite[i])
    return child


# ============================================================
# ====================== MUTATION ============================
# ============================================================
def mutate(chrom):
    pos = random.randrange(DIM)
    chrom[pos] = random.random()


# ============================================================
# ==================== LOOP DO BRKGA =========================
# ============================================================
best_sol = None
best_val = math.inf

for gen in range(MAX_GEN):

    # Avaliar
    scored = []
    for c in population:
        val = fitness(c)
        scored.append((val, c))
        if val < best_val:
            best_val = val
            best_sol = c

    # Ordenar
    scored.sort(key=lambda x: x[0])

    # Elites e não-elites
    num_elite = int(ELITE_PERCENT * POP_SIZE)
    num_mutant = int(MUTANT_PERCENT * POP_SIZE)

    elites = [scored[i][1] for i in range(num_elite)]
    non_elites = [scored[i][1] for i in range(num_elite, POP_SIZE)]

    # Nova população
    newpop = []

    # Elites sobrevivem
    for e in elites:
        newpop.append(e[:])

    # Mutantes (completamente random)
    for _ in range(num_mutant):
        newpop.append(random_chrom())

    # Restante = filhos cruzando elite x nonelite
    while len(newpop) < POP_SIZE:
        elite = random.choice(elites)
        nonel = random.choice(non_elites)
        child = crossover(elite, nonel)
        mutate(child)
        newpop.append(child)

    population = newpop

# ============================================================
# ================ OUTPUT (SALVAR EM ARQUIVO) ================
# ============================================================

C, assign = decoder(best_sol)

with open(FILE_OUT, "w") as f:
    f.write(f"Ciclo encontrado: {C:.4f}\n")
    for s in range(k):
        f.write(f"Estacao {s+1}: {assign[s]}\n")

print(f"Melhor ciclo encontrado: {C:.4f}")
