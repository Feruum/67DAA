# Own test cases

Each row matches the same line in `cases.jsonl` and `expected.jsonl`. Expected outputs show one valid witness; the runner accepts any witness satisfying the contract.

| Line | Case | Independent expected-answer justification |
|---|---|---|
| 1 | ping | The transport contract returns ready. |
| 2 | dsu_empty | No operations produce no states. |
| 3 | dsu_no_operations | An initial state must not be included. |
| 4 | dsu_repeats_and_self | Self/repeated unions do not merge; the successful merges create sets of size 2, 2, 4 and 5. |
| 5 | dsu_singleton | The only vertex remains one component of size one. |
| 6 | kruskal_empty | The empty forest has zero vertices, edges, cost and components. |
| 7 | kruskal_isolates | Every isolated vertex is a separate component. |
| 8 | kruskal_negative_parallel_loops | The components are {0,1,2}, {3,4}, {5}; their minimum costs are 1, -7 and 0. Loops cannot enter a forest. |
| 9 | kruskal_tied_forest | A connected four-vertex graph needs three edges, each of weight one; many optimal witnesses exist. |
| 10 | kruskal_positive_64bit | The input itself is a tree, so all four billion-weight edges are necessary. |
| 11 | kruskal_negative_64bit | The only spanning tree has four edges with weight minus one billion. |
| 12 | kruskal_loops_only | Loops connect no distinct vertices and are never selected. |
| 13 | prim_empty | The empty forest has zero vertices, edges, cost and components. |
| 14 | prim_isolates | Every isolated vertex is a separate component. |
| 15 | prim_negative_parallel_loops | The components are {0,1,2}, {3,4}, {5}; their minimum costs are 1, -7 and 0. Loops cannot enter a forest. |
| 16 | prim_tied_forest | A connected four-vertex graph needs three edges, each of weight one; many optimal witnesses exist. |
| 17 | prim_positive_64bit | The input itself is a tree, so all four billion-weight edges are necessary. |
| 18 | prim_negative_64bit | The only spanning tree has four edges with weight minus one billion. |
| 19 | prim_loops_only | Loops connect no distinct vertices and are never selected. |
| 20 | scc_empty | There are no components or cross-component edges. |
| 21 | scc_isolates | Each isolated vertex is its own SCC. |
| 22 | scc_partition_and_deduplication | Mutual reachability gives {0,1}, {2,3}, {4}, {5,6}. Only the first-to-second and second-to-third SCC pairs cross components. |
| 23 | scc_one_cycle | The directed cycle reaches every vertex from every other vertex. |
| 24 | topo_empty | The empty order is valid. |
| 25 | topo_isolates | With no dependencies, any permutation is valid. |
| 26 | topo_finished_neighbor | All edges increase vertex numbers; the later edge to a finished vertex is not a back edge. |
| 27 | topo_self_loop | A self-loop is a cycle, even in another component. |
| 28 | topo_disconnected_cycle | The separate 3->4->5->3 cycle prevents a whole-graph order. |
| 29 | topo_multiple_orders | Vertices 0 and 1 can be exchanged; both must occur before 2, then 3. |
| 30 | dag_singleton | The source has distance zero and no parent. |
| 31 | dag_isolated_source | Only the source is reachable. |
| 32 | dag_negative_and_unreachable | The route 0->1->2->3 costs 0. The unrelated negative edge 4->5 cannot make either endpoint reachable. |
| 33 | dag_minus_one_distance | Distance -1 is a finite value; only vertex 2 is unreachable. |
| 34 | dag_nonzero_source | The unreachable predecessor 0 cannot change the source distance; the cheapest route to 3 goes through 1. |
| 35 | dag_ties_and_parallel | Either parallel edge reaches 1, and either path to 3 has total cost 3. |
| 36 | dag_positive_64bit | Unique prefix paths cost k times one billion. |
| 37 | dag_negative_64bit | Unique prefix paths cost minus k times one billion. |
| 38 | dag_unreachable_cycle | The unreachable 2->3->2 cycle still makes the entire graph non-DAG. |
| 39 | dag_unreachable_self_loop | The disconnected self-loop is a cycle. |

## Full limits

All nine large cases use `n=100000` and exactly `250000` edges or union operations. Generation is deterministic; no random seed is needed. `generate_cases.py` is the stored input recipe.

`large/inputs.jsonl.gz`, `large/expected.jsonl.gz` and `large/actual.jsonl.gz` hold the complete inputs, independently derived expected answers and measured Java outputs. The case order and reasons are in `large/cases.json`. Standard gzip decompression gives UTF-8 JSON Lines.

## Commands

Run from the repository root with JDK 17+ and Python 3.12+:

```sh
python tests/run_tests.py
```

This compiles once, runs the small inputs, repeats mixed requests in one process, checks alternative and invalid witnesses, then runs all full-limit cases with the supplied 384 MiB Java heap and a 20-second limit for each input batch. Actual results and `results.txt` are regenerated from real executions.

To run only the small inputs through the provided launcher:

```sh
python tools/run.py --input tests/cases.jsonl
```

The separate route-helper and benchmark commands are documented in `ANALYSIS.md`.
