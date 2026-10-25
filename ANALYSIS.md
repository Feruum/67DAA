# Assignment 3: Graph Algorithms

Language: Java 17

## Build, run and test

Run these commands from the project root. Install JDK 17 or newer and Python 3.12 or newer first. The solution does not download any Java libraries. Python launches the checks; the graph algorithms are implemented in Java.

```sh
python tools/run.py --setup
python tools/run.py --check
python tools/run.py --input tests/cases.jsonl
python tests/run_tests.py
python tests/run_routes.py
python tests/run_benchmark.py
```

On Windows, `py -3` can replace `python`. The setup/check/input commands compile the Java source automatically. For a direct build and interactive run in a shell that expands wildcards:

```sh
mkdir -p .build/Java
javac --release 17 -encoding UTF-8 -d .build/Java src/Java/*.java
java -Xmx384m -cp .build/Java Main
```

Enter one complete JSON object per line. Every input line produces one JSON result line. There are no menus, prompts or debugging messages on standard output. Stop the direct run with the terminal's end-of-input shortcut or Ctrl+C.

Example input:

```json
{"task":"dag","n":5,"source":0,"edges":[[0,1,3],[0,2,8],[1,2,-7],[2,3,4]]}
```

Expected result:

```json
{"acyclic":true,"distance":[0,3,-4,0,null],"parent_edge":[-1,0,2,3,-1]}
```

The official launcher uses a 384 MiB Java heap, a 60-second compilation limit and a 20-second execution limit per input batch. These limits also apply to the own algorithm tests through the supplied launcher functions.

## Files and shared decisions

`src/Java/Algorithms.java` contains all six algorithms and the route helper. `DisjointSet` stores connectivity information. `Edge` stores its endpoints, weight and original input ID. `emptyGraph`, `outgoingEdges` and `topologicalOrder` share small pieces of graph construction and traversal. `Main.java`, `Input.java` and `Json.java` are the provided adapters; their comments were removed, but their executable behavior was preserved.

The code uses arrays, lists, loops, a hash set, sorting and a priority queue. It uses no recursion, streams, graph libraries or mutable static fields. The original template's other language folders remain as supplied because its transport tests refer to them. `submission.json` selects Java; those unfinished language stubs are not the selected solution.

Vertices, edge IDs and individual weights fit `int`. Costs and distances use `long`. A forest or a simple DAG path has at most 99,999 edges, so its absolute total is at most 99,999,000,000,000 under the assignment limits. This is outside the `int` range but inside the `long` range. `Integer.compare` compares weights without subtraction. SCC pair keys are also calculated as `long`.

Each call creates its own arrays, collections and result map. Nothing from one graph is reused by a later request. The entry point preserves `{"task":"ping"}` and returns `{"status":"ready"}`. The tests send different tasks repeatedly through one JVM to check this behavior.

Let `n` be the number of vertices, `m` the number of edges, `q` the number of union operations, and `L` the number of vertices in a reconstructed route. Memory bounds below include returned results. JSON conversion is linear in the size of the input and does not change these bounds.

## 1. Disjoint-set union

### Steps

Initially `parent[v] = v`, `size[v] = 1`, and there are `n` components. `find` first walks to a root. A second loop sets every parent on that path directly to the root. This is path compression.

For `union(a, b)`, find both roots. If they are equal, return without changing the partition. Otherwise attach the smaller tree to the larger tree, add their sizes, decrease `components`, and update `largest`. After every operation, save `[components, largest]` in the corresponding output row.

### Invariant and correctness

Two vertices have the same root exactly when the processed operations connect them. The size stored at a root equals the number of vertices in its set. Path compression changes the tree shape without changing its members. A successful union joins exactly two sets, so the component count decreases by one and the new size is the sum of both previous sizes. Taking the maximum preserves the largest set size. Therefore every recorded state describes the partition after that operation.

### Boundaries and complexity

Repeated unions and self-unions do not change the state. An empty operation list returns no rows, including when `n > 0`; the initial state is not returned. For `n = 0`, `largest` starts at zero. Time is `O(n + q alpha(n))` amortized with path compression and union by size. Memory is `O(n + q)`: parent/size arrays plus all requested output states.

## 2. Kruskal minimum spanning forest

### Steps

Create an `Edge` object for each input row and remember its original ID. Sort these objects by weight, with ID as a deterministic tie breaker. Start a fresh DSU. Scan the sorted edges and accept an edge only when `union` joins different sets. Add its original ID to `edge_ids` and its weight to a `long` total. Return the DSU component count after the scan.

### Invariant and correctness

The selected edges form a forest, and the DSU components are exactly its trees. Every accepted edge joins two trees, so it cannot create a cycle. Consider the cut around one current tree when an edge is accepted. A lighter edge crossing that cut could not have been rejected earlier: an earlier rejected edge already had both endpoints in the same set, and sets only merge. Thus the accepted edge is a cheapest available crossing edge. The cut property permits adding it to some minimum spanning forest. Applying this argument after every accepted edge gives an optimal forest.

After all edges are processed, every input edge has endpoints in the same DSU component. The result therefore spans every connected component of the input. Isolates remain separate components, and exactly `n - components` edges were accepted.

### Boundaries and complexity

Self-loops fail the union condition. Parallel edges compete normally. Negative weights and ties do not change the argument. For an empty graph, the cost and component count are zero and no IDs are returned. Time is `O(n + m log(m + 1))`; memory is `O(n + m)` for copied edges, sorting, DSU and result IDs.

## 3. Prim minimum spanning forest

### Steps

Build an undirected adjacency list by storing both orientations of every edge, keeping its original ID. For each unvisited vertex, start another component and mark that vertex visited. Put its edges to unvisited endpoints into a priority queue.

Remove the cheapest queued edge. If its destination is already visited, skip it. Otherwise accept the edge, mark the destination visited, and enqueue that vertex's edges to unvisited endpoints. Continue until the queue is empty, then restart from the next unvisited vertex.

### Invariant and correctness

Within the current connected component, the accepted edges form a tree on the visited vertices. Every usable queued edge connects a visited vertex to an unvisited one. All edges crossing this cut have been inserted when their visited endpoint was processed. Stale entries may remain, but they are discarded before acceptance. The first usable edge removed from the priority queue is therefore a minimum edge across the cut. The cut property makes that choice safe for an MST of this component.

When the queue is empty, no edge leads from the visited set to another vertex of that connected component. Restarting processes every remaining component, including individual isolated vertices. Combining the component MSTs gives a minimum spanning forest.

### Boundaries and complexity

Self-loops point to an already visited vertex and are not accepted. Parallel edges, negative weights and ties work through the same queue rule. This implementation is independent of Kruskal and does not call it. The lazy queue may hold `O(m)` entries, so time is `O(n + m log(m + 1))` and memory is `O(n + m)`.

## 4. Kosaraju strongly connected components

### Steps

Build the directed graph and its transpose, which reverses every edge. Run DFS on the original graph from every unvisited vertex. The explicit stack keeps the active vertices. `next[v]` records the next neighbor to inspect. Add a vertex to `finish` only after all its outgoing edges have been examined.

Process vertices in decreasing finish order. For each vertex that has no component label, run another DFS on the transpose and assign the same label to every vertex reached in this traversal. Finally, scan the original edges. For endpoints with different labels, add the pair to `condensation` once.

### Invariant and correctness

In the first pass, a vertex is finished only after its descendants have finished. In the condensation graph, an edge from SCC A to a different SCC B implies that the largest first-pass finish time in A is greater than the largest finish time in B. Decreasing finish order therefore selects a source SCC among the components not yet assigned. On the transpose, it cannot reach another unassigned SCC, but every vertex within its own SCC is still mutually reachable. The second DFS consequently assigns exactly one SCC at a time.

For condensation deduplication, labels lie in `0..n-1`. The key `(long) from * n + to` uniquely identifies an ordered pair within this range. A hash set ensures that each distinct cross-component pair is added exactly once. Internal edges are excluded.

### Boundaries and complexity

Isolates receive separate labels. Self-loops stay inside an SCC. Repeated directed edges cannot duplicate condensation pairs. Empty graphs return two empty arrays. Both passes scan each vertex and edge a constant number of times. Hash-based deduplication gives expected `O(n + m)` time and `O(n + m)` memory.

## 5. Three-state DFS topological order

### Steps

Build adjacency lists of outgoing edge IDs. Each vertex has state `0` for unvisited, `1` for active, or `2` for finished. Start DFS from every still-unvisited vertex. On an edge to an unvisited vertex, push it and mark it active. On an edge to an active vertex, report a cycle. On an edge to a finished vertex, continue normally. When a vertex has no more neighbors, mark it finished and put it into the output array from right to left.

### Invariant and correctness

The active vertices are exactly the vertices currently on the DFS path. An edge to an active vertex closes a directed path into a cycle. If no such edge exists, a vertex reached by an edge is finished before its predecessor finishes, or was already finished earlier. Reversing finish order therefore places the predecessor before the destination for every edge. Every vertex is started and finished once, so the output contains each vertex exactly once.

The outer loop checks every component. An isolated directed cycle is rejected even if the traversal began elsewhere. `topologicalOrder` returns `null` internally for a cycle; the JSON task converts this to `acyclic=false` and `order=[]`.

### Boundaries and complexity

A self-loop finds the same active vertex and is a cycle. Duplicate edges do not create a cycle by themselves. An edge to a finished vertex is not treated as a cycle. The empty graph has a valid empty order. Saved neighbor positions ensure no adjacency list is repeatedly scanned after a child returns. Time and memory are both `O(n + m)`.

## 6. DAG shortest paths

### Steps

Use the same three-state DFS helper to check the entire directed graph and obtain a topological order. If any cycle exists, return `acyclic=false` with empty distance and parent arrays.

Otherwise create a `Long[]` filled with `null` and set the source distance to zero. Fill `parentEdge` with `-1`. Visit vertices in topological order. Skip unreachable vertices. For every outgoing edge of a reachable vertex, compute `candidate = distance[u] + weight` as a `long`. If the destination is unreachable or the candidate is smaller, update its distance and store the original edge ID.

### Invariant and correctness

When a vertex is processed, every possible predecessor has already been processed. Its distance is therefore the minimum over all reachable incoming paths. The induction starts with the source distance zero. Relaxation extends a correct shortest path by one edge and compares it with all competing paths. By induction, every reachable vertex ends with its shortest distance. Negative weights are safe because the graph is acyclic and predecessors are finalized in topological order.

Each stored parent edge ends at the vertex whose distance was updated and extends a real source path. Moving backward through parent edges follows strictly decreasing topological positions, so the parent chain cannot cycle and must end at the source. Equal candidates do not replace the current parent; any such chosen shortest-path witness is valid.

### Boundaries and complexity

Cycles unreachable from the source are still rejected before any relaxation. Unreachable vertices retain distance `null` and parent `-1`. A distance of `-1` is an ordinary finite value, not an unreachable marker. A singleton source has distance zero and no parent. Incoming edges from unreachable vertices cannot change the source. Parallel edges keep their distinct original IDs. Time and memory are both `O(n + m)`.

## Deep graphs and route reconstruction

All graph DFS work uses explicit `int[]` stacks. The first Kosaraju pass and topological DFS save neighbor progress in `next[]`. Every vertex can be on the stack at most once at a time. The second Kosaraju pass assigns a label when pushing a vertex, preventing duplicate pushes. The maximum stack storage is `O(n)`, and a 100,000-vertex chain does not require 100,000 Java method calls.

The helper signature is:

```java
static List<Integer> reconstructPath(int source, int target, int[][] edges,
                                     int[] parentEdge)
```

Call it with the original edge order and a valid parent array returned by an acyclic DAG result. Begin at the target, follow `edges[parentEdge[v]][0]` backward, and reverse the collected vertices. The source returns `[source]`. An unreachable target returns `[]`. Do not call the helper with the empty arrays returned for a cyclic graph. It is a Java helper, not an extra JSON task.

Because a valid parent chain moves toward the source, the helper terminates and returns a directed source-to-target route. It takes `O(L)` time and output space for a reachable route; an unreachable target is recognized immediately by parent `-1`. It allocates no array of size `n`.

## Executed route-helper examples

These are actual results from `python tests/run_routes.py`. The full inputs and parent arrays are in `tests/routes_results.json`; the Java calls and assertions are in `tests/RouteTests.java`.

The ordered input edge arrays used by the examples are:

```java
int[][] baseEdges = {
    {0, 1, 3}, {0, 2, 8}, {1, 2, -7}, {2, 3, 4}, {1, 4, 2}
};
int[][] shiftedEdges = {
    {3, 1, 2}, {1, 4, -3}, {3, 4, 5}, {0, 2, 1}
};
int[][] tiedEdges = {
    {0, 1, 2}, {0, 1, 2}, {0, 2, 2}, {1, 3, 3},
    {2, 3, 3}, {0, 3, 5}, {3, 4, -1}
};
```

The base graph has 6 vertices and source 0; the shifted graph has 5 vertices and source 3; the tied graph has 5 vertices and source 0. The actual parent arrays were:

```text
baseParents = [-1, 0, 2, 3, 4, -1]
shiftedParents = [-1, 0, -1, -1, 1]
tiedParents = [-1, 0, 2, 5, 6]
alternateParallelParents = [-1, 1, 2, 3, 6]
alternateBranchParents = [-1, 0, 2, 4, 6]
```

The last two arrays are explicitly supplied alternative valid shortest-path witnesses for the tied graph.

| Actual helper call | Returned vertices | Original edge IDs | Total weight |
|---|---|---|---:|
| `reconstructPath(0, 3, baseEdges, baseParents)` | `[0, 1, 2, 3]` | `[0, 2, 3]` | 0 |
| `reconstructPath(0, 0, baseEdges, baseParents)` | `[0]` | `[]` | 0 |
| `reconstructPath(0, 5, baseEdges, baseParents)` | `[]` | `[]` | No route |
| `reconstructPath(3, 4, shiftedEdges, shiftedParents)` | `[3, 1, 4]` | `[0, 1]` | -1 |
| `reconstructPath(0, 1, tiedEdges, tiedParents)` | `[0, 1]` | `[0]` | 2 |
| `reconstructPath(0, 4, tiedEdges, tiedParents)` | `[0, 3, 4]` | `[5, 6]` | 4 |
| `reconstructPath(0, 4, tiedEdges, alternateParallelParents)` | `[0, 1, 3, 4]` | `[1, 3, 6]` | 4 |
| `reconstructPath(0, 4, tiedEdges, alternateBranchParents)` | `[0, 2, 3, 4]` | `[2, 4, 6]` | 4 |

For the base route to vertex 3, edge IDs 0, 2 and 3 are directed 0 -> 1, 1 -> 2 and 2 -> 3, with total 3 - 7 + 4 = 0. The source route has no edges and total zero. Vertex 5 is unreachable. The shifted route has weight 2 - 3 = -1, confirming that a finite distance of -1 is preserved.

In the tied graph, original IDs 0 and 1 are parallel edges of weight 2. The actual result reaches vertex 4 by IDs 5 and 6 with cost 5 - 1 = 4. The alternative parent arrays select IDs 1, 3, 6 or 2, 4, 6, both with cost 2 + 3 - 1 = 4. The assertions verify every original edge direction and compare the summed weight with the independently expected shortest distance. All eight helper calls passed.

## Executed tests

| Check | Observed result | Evidence |
|---|---|---|
| Setup and ping | Passed | `tests/evidence/setup.txt` |
| Public cases | 36 of 36 passed | `tests/evidence/public_check.txt` |
| Public state reset | Two complete public batches in one process passed | `tests/evidence/public_check.txt` |
| Own boundary cases | 39 of 39 passed | `tests/actual.jsonl`, `tests/results.txt` |
| Own mixed requests | 117 requests in one JVM passed | `tests/mixed_actual.jsonl` |
| Alternative and invalid witnesses | 17 acceptance/rejection checks passed | `tests/witness_checks.jsonl` |
| Full-limit cases | 9 of 9 passed | `tests/large/cases.json` |
| Route helper | 8 of 8 direct calls passed | `tests/routes_results.json` |
| Benchmark validation | 54 validated method calls across three sizes | `tests/benchmark_results.json` |

`tests/CASES.md` explains every small expected answer. Cases cover empty and disconnected graphs, isolates, self/repeated unions, negative loops, parallel edges, ties, both signs of 64-bit totals, nonzero sources, unreachable vertices, a finite distance of -1, and cycles outside source reachability. `tests/expected.jsonl` contains a valid expected witness for each input; equality of witness arrays is not required.

The supplied semantic validator checks forest edge count, acyclicity, spanning and cost; SCC membership and exact condensation; topological precedence; and shortest distances with correctly directed parent paths. The witness-sensitivity tests accept different optimal forests, relabeled SCCs, an alternative topological order, and alternative shortest-path parents. They also reject cycles or duplicate forest IDs, merged SCCs, missing or duplicated condensation pairs, incorrect orderings, and invalid parent edges.

### Full-limit cases

All nine cases have `n = 100000` and exactly `250000` edges or operations. The generator in `tests/generate_cases.py` is deterministic and needs no seed. Complete inputs, independently expected answers and actual Java outputs are included in `tests/large/inputs.jsonl.gz`, `expected.jsonl.gz` and `actual.jsonl.gz` respectively.

| Case | What establishes the expected answer | Recorded execution (seconds) |
|---|---|---:|
| `dsu_full` | The chain merges the first i+2 vertices after operation i; later self/repeated unions keep [1,100000]. | 0.584 |
| `kruskal_full` | The graph is a chain with loops and more expensive parallel edges. Each cut needs its -1000000000 chain edge; total -99999000000000. | 0.412 |
| `prim_full` | The graph is a chain with loops and more expensive parallel edges. Each cut needs its -1000000000 chain edge; total -99999000000000. | 0.472 |
| `scc_full_chain` | Every non-loop edge moves forward, so every vertex is a separate SCC. Duplicate edges collapse to the chain condensation. | 0.557 |
| `scc_full_cycle` | The first 100000 edges form one directed cycle through all vertices, so there is one SCC. | 0.395 |
| `topo_full_cycle` | The all-vertex directed cycle has no topological order. | 0.317 |
| `topo_full_chain` | The chain requires increasing vertex order; duplicate edges do not introduce cycles. | 0.361 |
| `dag_full_chain` | Every source-to-k route takes exactly k chain steps, giving distance -k*1000000000; duplicate edge IDs provide valid alternative parents. | 0.444 |
| `dag_full_unreachable_cycle` | Vertices 99998 and 99999 form a cycle disconnected from source 0; whole-graph cycle checking must reject it. | 0.352 |

The large executions all used `java -Xmx384m` through the provided launcher. Their recorded wall-clock times include Python JSON serialization, JVM startup, Java parsing, algorithm work, result output and Python decoding. They are scale checks, separate from the algorithm benchmark below. Compiling and writing compressed evidence are outside those recorded execution times. No stack overflow or heap failure occurred in these runs.

## Kruskal versus Prim benchmark

Command: `python tests/run_benchmark.py`. The implementation, seeded generator and validation are in `tests/Benchmark.java`. The complete raw samples and environment are in `tests/benchmark_results.json`.

### Inputs and validation

For each vertex v=1..n-1, add one edge from a random vertex below v, with weight in [-1000,-1]. Add random endpoint pairs, allowing loops and parallel edges, with weights in [0,1000] until m=4n. Shuffle all edges using the same Random instance.

The three seeds are 2537, 2538 and 2539, using `java.util.Random`. The generator and seed reproduce the exact original edge ordering after the shuffle. Both algorithms receive the same already generated graph at each size.

The n-1 negative edges form a spanning tree. Every other edge is nonnegative, so any different n-1-edge tree costs strictly more. The expected cost is the sum of the generated negative edges, computed before either algorithm.

Before warm-up, both implementations are checked against this independent cost. Every later result is also checked outside the timed region: exactly one component, exactly n-1 unique valid original edge IDs, no selected loop, correct weight sum, exactly the known negative tree edges, and BFS connectivity. A connected graph with n-1 edges is a tree. There are nine validated calls per method per size: one initial correctness call, three warm-up calls and five measured calls, for 54 calls in total.

### Measurement protocol

The timer is `System.nanoTime`, converted to milliseconds. The timed region wraps the small `solve` dispatch and its call to `Algorithms.kruskal` or `Algorithms.prim`. It includes `Input.edges` conversion, sorting or adjacency/queue construction, algorithm computation, and result-map construction. It excludes compilation, JVM startup, graph generation, JSON parsing and serialization, console/file I/O, and witness validation. This boundary is the same for both algorithms.

Three explicit warm-up calls per method and per size precede five measured calls. The initial correctness call also executes each method before warm-up. Measured order alternates: Kruskal then Prim on even-numbered runs, Prim then Kruskal on odd-numbered runs. No explicit garbage-collection request is made.

| n | m | Seed | Method | Five measured times (ms) | Median (ms) |
|---:|---:|---:|---|---|---:|
| 1000 | 4000 | 2537 | Kruskal | 1.435, 2.009, 1.392, 1.364, 1.333 | 1.392 |
| 1000 | 4000 | 2537 | Prim | 1.967, 1.292, 1.340, 1.112, 0.966 | 1.292 |
| 10000 | 40000 | 2538 | Kruskal | 26.856, 11.616, 10.730, 27.613, 29.707 | 26.856 |
| 10000 | 40000 | 2538 | Prim | 13.549, 16.563, 11.448, 11.504, 16.114 | 13.549 |
| 50000 | 200000 | 2539 | Kruskal | 46.020, 38.574, 45.532, 41.209, 39.133 | 41.209 |
| 50000 | 200000 | 2539 | Prim | 126.802, 103.270, 98.036, 105.813, 107.007 | 105.813 |

### Environment and observations

Recorded on 2026-10-25 at 02:26:45 in Asia/Qyzylorda (UTC+05:00). OS: `Linux-6.18.55-x86_64-with-glibc2.39`. CPU model reported by the container: AMD EPYC 9V74 80-Core Processor; 9 logical CPUs were visible. Python: 3.12.14. JVM heap limit: `-Xmx384m`.

```text
openjdk version "17.0.20" 2026-07-21
OpenJDK Runtime Environment (build 17.0.20+8-1-24.04-Ubuntu)
OpenJDK 64-Bit Server VM (build 17.0.20+8-1-24.04-Ubuntu, mixed mode, sharing)
```

The preparation runtime supplied the Java 17 compiler module but not a separate `javac` command. A local shell wrapper invoked `java --module jdk.compiler/com.sun.tools.javac.Main` for the standard launcher. This wrapper is an environment detail, not a project dependency; on a normal JDK installation the documented `javac` command works directly.

On the recorded inputs, Prim had the lower median for 1,000 and 10,000 vertices. Kruskal had the lower median for 50,000 vertices. The middle-size Kruskal samples varied substantially, from 10.730 to 29.707 ms. These observations describe this run; JVM compilation, allocation, garbage collection and shared-machine load can affect individual samples and their ordering.

The generator uses one sparse connected graph distribution with a known light spanning tree. All of its tree edges are lighter than all additional edges. The benchmark does not represent every graph density, disconnected structure or weight distribution. Five samples per method and size are enough for the requested comparison, but they do not establish a universal performance ranking.

Both implementations have the stated `O(n + m log(m + 1))` worst-case time bound. That conclusion follows from sorting or heap operations and the code structure, independently of the measured timings.

## Submission

The project includes the selected Java source, `submission.json`, own tests with recorded outputs, this English analysis, and the original public-check workflow. Create your own repository from the course template, copy these files into it, commit and push, then verify its Actions run. Submit the exact commit URL in Moodle and click Submit assignment. Local public checks do not calculate a grade, establish a hosted Actions result, or submit anything to Moodle.

## Sources and AI assistance

The requirements, public examples, Java adapters, launchers and semantic validator come from the [course assignment template](https://github.com/RZhaniya/daa-assignment-3-graphs). The supplied `Assignment_3_EN.pdf` and template `README.md` were used to check the contracts and submission requirements. The template's `tools/public_validate.py` is reused for semantic output checks; it was not rewritten or weakened.

ChatGPT assisted with writing the Java implementation, the own-test generators and runners, the route tests, the benchmark and this analysis. The reported checks and measurements were executed in the preparation environment. Expected values in the own cases are justified separately in `tests/CASES.md` and `tests/large/cases.json`; benchmark expected costs follow from the generated graph construction. No graph-algorithm library was used. These recorded runs describe verification performed during preparation and do not claim that the student has personally repeated them.
