# Network Motifs in an Email Network

CS1005 Discrete Structures - Fall 2026 Course Project

Finding network motifs (triad isomorphism classes that occur significantly
more or less often than in degree-preserving random graphs) in the SNAP
email-Eu-core dataset, following Milo et al., "Network Motifs: Simple
Building Blocks of Complex Networks".

## Group Members

| Name              | Roll Number | Section |
|-------------------|-------------|---------|
| Ahmed Bin Akhtar  | 25i-0764    | B       |
| Syed Harun Pirzada| 25i-0600    | B       |
| Awkash            | 25i-3205    | B       |
| Hammad Haider     | 25p-3021    | B       |

## Parameters (derived from R)

- Roll suffixes: 764 + 600 + 3205 + 3021
- **R = 7590**
- Pair index = R mod 190 = 180 -> top-20 indices (15, 16)
- Department A = top-20[15] = department 9 (32 nodes, 146 internal edges)
- Department B = top-20[16] = department 8 (19 nodes, 134 internal edges)
- Number of random networks = 20 + (R mod 31) = 46
- Swap attempts per random network = (5 + (R mod 6)) x edges = 5 x edges
- Random seed = R = 7590

The top-20 departments are ranked by internal edge count (edges with both
endpoints in the department), descending, ties broken by smaller
department ID.

## Dataset

SNAP email-Eu-core: 1,005 people, 25,571 directed edges, 42 departments.
Self-loops removed, duplicate edges removed (simple directed graph).
Source: https://snap.stanford.edu/data/email-Eu-core.html

## How to Run

Requires Python 3 with matplotlib.

```
pip install matplotlib
python motif.py
```

The script prints the parameter list, the top-20 departments, observed
triad counts, Z-scores, motifs and anti-motifs for both departments,
and writes `motif_chart.png` (titled with R).

## Method

- Each 3-node subset is encoded as a 6-bit integer over the six possible
  directed edges; the canonical code is the minimum over all 6 node
  orderings. The 13 connected canonical codes map to classes 1-13.
- Triads are counted by enumerating pairs of neighbours around each node
  (every connected triad has a node adjacent to the other two) and
  removing duplicates - no C(|V|, 3) enumeration.
- Null model: double-edge swaps. Two edges (a,b) and (c,d) are replaced
  by (a,d) and (c,b); the swap is rejected if it would create a
  self-loop or a duplicate edge. This preserves every node's in- and
  out-degree exactly (verified by assert).
- Z = (N(G) - mean) / population_std over the 46 random graphs;
  Z = 0 when std = 0. Z > 2 => motif, Z < -2 => anti-motif.

## Results Summary

Both departments show classes 8 and 13 as significant motifs
(Z > 2). See the console output and `motif_chart.png` for the full
tables and the grouped bar chart.

## Contributions

- **Ahmed Bin Akhtar (25i-0764):** project setup, GitHub repository,
  data loading and cleaning, induced subgraph construction, top-20
  department ranking, parameter derivation, main pipeline
  (`motif.py`), README.
- **Syed Harun Pirzada (25i-0600):** triad encoding and canonical
  classification (`triad_class`), connected-triad counting logic.
- **Awkash (25i-3205):** null-model randomization (`randomize`,
  double-edge swaps), degree-preservation verification, Z-score
  computation.
- **Hammad Haider (25p-3021):** results analysis, chart generation,
  video presentation, interpretation of department differences.
