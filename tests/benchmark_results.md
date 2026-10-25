# Kruskal and Prim benchmark

Command: `python tests/run_benchmark.py`

All times are real measurements in milliseconds. Each method had three unmeasured warm-up calls and five measured calls at each size. Both methods used the same graph and the same timing boundary. Every result was validated outside the timer.

| n | m | Seed | Method | Five timings (ms) | Median (ms) |
|---:|---:|---:|---|---|---:|
| 1000 | 4000 | 2537 | Kruskal | 1.435, 2.009, 1.392, 1.364, 1.333 | 1.392 |
| 1000 | 4000 | 2537 | Prim | 1.967, 1.292, 1.340, 1.112, 0.966 | 1.292 |
| 10000 | 40000 | 2538 | Kruskal | 26.856, 11.616, 10.730, 27.613, 29.707 | 26.856 |
| 10000 | 40000 | 2538 | Prim | 13.549, 16.563, 11.448, 11.504, 16.114 | 13.549 |
| 50000 | 200000 | 2539 | Kruskal | 46.020, 38.574, 45.532, 41.209, 39.133 | 41.209 |
| 50000 | 200000 | 2539 | Prim | 126.802, 103.270, 98.036, 105.813, 107.007 | 105.813 |

## Inputs and independent validation

For each vertex v=1..n-1, add one edge from a random vertex below v, with weight in [-1000,-1]. Add random endpoint pairs, allowing loops and parallel edges, with weights in [0,1000] until m=4n. Shuffle all edges using the same Random instance.

The n-1 negative edges form a spanning tree. Every other edge is nonnegative, so any different n-1-edge tree costs strictly more. The expected cost is the sum of the generated negative edges, computed before either algorithm.

Before warm-up, and after every warm-up or measured call: exact independent minimum cost, one component, n-1 unique original IDs, no loops, selected-weight sum, and BFS connectivity. Connected with n-1 edges implies acyclic. All selected edges must be negative.

The generator source and seeds reproduce the complete ordered input edge lists. The JSON file records all measured samples and actual returned cost, component count, selected edge count, selected-weight sum and connectivity evidence.

## Timing boundary

Timer: `System.nanoTime`. The timed region starts immediately before invoking `Algorithms.kruskal` or `Algorithms.prim` and ends immediately after its result returns. It includes input conversion, algorithm data-structure construction, computation and result construction. Compilation, JVM startup, generator work, JSON parsing/serialization, I/O and verification are excluded. Order alternates between the two methods on successive measured runs.

## Environment

- OS: Linux-6.18.55-x86_64-with-glibc2.39
- CPU: AMD EPYC 9V74 80-Core Processor
- Logical CPUs reported: 9
- Python: 3.12.14
- JVM heap limit: `-Xmx384m`
- Recorded at: 2026-10-24T21:26:45.602507+00:00

```text
openjdk version "17.0.20" 2026-07-21
OpenJDK Runtime Environment (build 17.0.20+8-1-24.04-Ubuntu)
OpenJDK 64-Bit Server VM (build 17.0.20+8-1-24.04-Ubuntu, mixed mode, sharing)
```

## Interpretation and limitations

One connected, sparse, planted-tree distribution; all tree edges are lighter than all additional edges. These are not general random-weight graphs. Five samples on one shared runtime are affected by JIT compilation, allocation, garbage collection and machine load. No explicit System.gc calls. Measurements do not prove asymptotic complexity or establish a universal winner.

Both implementations have an O(n + m log(m+1)) worst-case time bound with the chosen standard sorting and lazy priority queue. Input conversion and adjacency construction add linear work. The measured medians describe these three inputs and this runtime; the complexity claim follows from the algorithm structure, not the timings.
