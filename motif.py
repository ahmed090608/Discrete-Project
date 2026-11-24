import math
import random
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
EDGES_FILE = DATA_DIR / "email-Eu-core.txt"
LABELS_FILE = DATA_DIR / "email-Eu-core-department-labels.txt"

# Last-4 digits of each group member's roll number (25X prefix ignored).
ROLL_SUFFIXES = [764, 600, 3205, 3021]

R = sum(ROLL_SUFFIXES)
NUM_RANDOM = 20 + (R % 31)
SWAP_FACTOR = 5 + (R % 6)
SEED = R

CLASS_CODES = [3, 6, 7, 10, 11, 15, 21, 23, 25, 27, 30, 31, 63]
CODE_TO_CLASS = {code: i + 1 for i, code in enumerate(CLASS_CODES)}

PAIRS = [(i, j) for i in range(20) for j in range(i + 1, 20)]
PAIR_INDEX = R % 190
DEPT_A_INDEX, DEPT_B_INDEX = PAIRS[PAIR_INDEX]


def load_edges(path):
    edges = set()
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            u, v = int(parts[0]), int(parts[1])
            if u != v:
                edges.add((u, v))
    return edges


def load_labels(path):
    labels = {}
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                labels[int(parts[0])] = int(parts[1])
    return labels


def induced_subgraph(nodes, edges):
    node_set = set(nodes)
    sub_edges = {(u, v) for u, v in edges if u in node_set and v in node_set}
    return sorted(node_set), sorted(sub_edges)


def triad_code(order, adj):
    x0, x1, x2 = order
    code = 0
    if x1 in adj[x0]:
        code |= 1
    if x2 in adj[x0]:
        code |= 2
    if x0 in adj[x1]:
        code |= 4
    if x2 in adj[x1]:
        code |= 8
    if x0 in adj[x2]:
        code |= 16
    if x1 in adj[x2]:
        code |= 32
    return code


def triad_class(a, b, c, adj):
    import itertools
    best = 64
    for perm in itertools.permutations((a, b, c)):
        code = triad_code(perm, adj)
        if code < best:
            best = code
    return CODE_TO_CLASS.get(best, 0)


def count_triads(nodes, edges):
    adj = defaultdict(set)
    neighbors = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        neighbors[u].add(v)
        neighbors[v].add(u)
    counts = [0] * 14
    seen = set()
    for v in nodes:
        nbrs = sorted(neighbors[v])
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                triad = tuple(sorted((v, nbrs[i], nbrs[j])))
                if triad in seen:
                    continue
                seen.add(triad)
                cls = triad_class(*triad, adj)
                if cls:
                    counts[cls] += 1
    return counts[1:]


def randomize(edges, attempts, rng):
    edge_list = list(edges)
    edge_set = set(edges)
    for _ in range(attempts):
        i = rng.randrange(len(edge_list))
        j = rng.randrange(len(edge_list))
        a, b = edge_list[i]
        c, d = edge_list[j]
        if a == d or c == b:
            continue
        if (a, d) in edge_set or (c, b) in edge_set:
            continue
        edge_set.discard((a, b))
        edge_set.discard((c, d))
        edge_set.add((a, d))
        edge_set.add((c, b))
        edge_list[i] = (a, d)
        edge_list[j] = (c, b)
    return edge_list


def check_degrees_preserved(original, randomized):
    def degrees(edge_list):
        indeg = defaultdict(int)
        outdeg = defaultdict(int)
        for u, v in edge_list:
            outdeg[u] += 1
            indeg[v] += 1
        return indeg, outdeg
    oi, oo = degrees(original)
    ri, ro = degrees(randomized)
    assert dict(oi) == dict(ri) and dict(oo) == dict(ro), "degree sequence changed!"


def zscores(observed, random_counts):
    result = []
    for k in range(13):
        vals = [counts[k] for counts in random_counts]
        mean = sum(vals) / len(vals)
        var = sum((x - mean) ** 2 for x in vals) / len(vals)
        std = math.sqrt(var)
        z = 0.0 if std == 0 else (observed[k] - mean) / std
        result.append(z)
    return result


def main():
    print("=" * 60)
    print("NETWORK MOTIF ANALYSIS - email-Eu-core")
    print("=" * 60)
    print(f"Group roll suffixes : {ROLL_SUFFIXES}")
    print(f"R                   : {R}")
    print(f"Pair index (R mod 190): {PAIR_INDEX} -> indices ({DEPT_A_INDEX}, {DEPT_B_INDEX})")
    print(f"Random networks    : {NUM_RANDOM}")
    print(f"Swap factor        : {SWAP_FACTOR} x edges")
    print(f"Seed               : {SEED}")
    print("=" * 60)

    edges = load_edges(EDGES_FILE)
    labels = load_labels(LABELS_FILE)
    print(f"Loaded {len(edges)} unique directed edges, {len(labels)} labeled nodes")

    dept_edges = defaultdict(int)
    dept_nodes = defaultdict(set)
    for node, dept in labels.items():
        dept_nodes[dept].add(node)
    for u, v in edges:
        if u in labels and v in labels and labels[u] == labels[v]:
            dept_edges[labels[u]] += 1

    top20 = sorted(dept_edges, key=lambda d: (-dept_edges[d], d))[:20]
    for idx, d in enumerate(top20):
        print(f"  top20[{idx:2d}] = dept {d:3d}  internal_edges={dept_edges[d]}")

    dept_a, dept_b = top20[DEPT_A_INDEX], top20[DEPT_B_INDEX]
    print(f"\nDepartment A = top20[{DEPT_A_INDEX}] = dept {dept_a}")
    print(f"Department B = top20[{DEPT_B_INDEX}] = dept {dept_b}")

    results = {}
    for name, dept in (("A", dept_a), ("B", dept_b)):
        nodes, sub_edges = induced_subgraph(dept_nodes[dept], edges)
        print(f"\nDepartment {name} (dept {dept}): {len(nodes)} nodes, {len(sub_edges)} edges")

        observed = count_triads(nodes, sub_edges)
        print("Observed triad counts (class 1-13):")
        print(" ", observed)

        attempts = SWAP_FACTOR * len(sub_edges)
        rng = random.Random(SEED)
        random_counts = []
        for _ in range(NUM_RANDOM):
            rand_edges = randomize(sub_edges, attempts, rng)
            check_degrees_preserved(sub_edges, rand_edges)
            random_counts.append(count_triads(nodes, rand_edges))

        z = zscores(observed, random_counts)
        results[name] = (dept, observed, z)
        print("Z-scores (class 1-13):")
        print(" ", [round(x, 3) for x in z])
        motifs = [i + 1 for i, x in enumerate(z) if x > 2]
        antimotifs = [i + 1 for i, x in enumerate(z) if x < -2]
        print(f"  Motifs (Z>2): {motifs}")
        print(f"  Anti-motifs (Z<-2): {antimotifs}")

    plot_results(results)
    print("\nChart saved to motif_chart.png")


def plot_results(results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    za = results["A"][2]
    zb = results["B"][2]
    x = range(1, 14)
    width = 0.35
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([i - width / 2 for i in x], za, width, label=f"Dept A ({results['A'][0]})")
    ax.bar([i + width / 2 for i in x], zb, width, label=f"Dept B ({results['B'][0]})")
    ax.axhline(2, color="red", linestyle="--", linewidth=1)
    ax.axhline(-2, color="red", linestyle="--", linewidth=1)
    ax.set_xlabel("Triad class")
    ax.set_ylabel("Z-score")
    ax.set_title(f"Motif Z-scores by department (R={R})")
    ax.set_xticks(list(x))
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig("motif_chart.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
