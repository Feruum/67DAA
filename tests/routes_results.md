# Route helper tests

Command: `python tests/run_routes.py`

Every row below comes from an executed call to the Java helper. Expected shortest distances are written explicitly in `RouteTests.java`. Reachable routes are checked for their endpoints, directed original parent edges and total weight. Unreachable routes return an empty list.

| Check | Helper call | Returned vertices | Edge IDs | Weight |
|---|---|---|---|---:|
| reachable target | `reconstructPath(0, 3, baseEdges, baseParents)` | `[0, 1, 2, 3]` | `[0, 2, 3]` | 0 |
| source target | `reconstructPath(0, 0, baseEdges, baseParents)` | `[0]` | `[]` | 0 |
| unreachable target | `reconstructPath(0, 5, baseEdges, baseParents)` | `[]` | `[]` | No route |
| nonzero source and distance minus one | `reconstructPath(3, 4, shiftedEdges, shiftedParents)` | `[3, 1, 4]` | `[0, 1]` | -1 |
| parallel edge from actual DAG result | `reconstructPath(0, 1, tiedEdges, tiedParents)` | `[0, 1]` | `[0]` | 2 |
| tied route from actual DAG result | `reconstructPath(0, 4, tiedEdges, tiedParents)` | `[0, 3, 4]` | `[5, 6]` | 4 |
| alternative valid parallel edge and tied route | `reconstructPath(0, 4, tiedEdges, alternateParallelParents)` | `[0, 1, 3, 4]` | `[1, 3, 6]` | 4 |
| alternative valid tied branch | `reconstructPath(0, 4, tiedEdges, alternateBranchParents)` | `[0, 2, 3, 4]` | `[2, 4, 6]` | 4 |

## Input and parent evidence

`routes_results.json` stores the complete inputs, actual DAG results, every parent array, selected edge IDs, directed edge rows and verified weights. The alternative parallel and branch cases use explicitly supplied valid shortest-path parents for the same tied graph.

For the base graph, the reachable route to 3 is 0 -> 1 -> 2 -> 3, using edges 0, 2 and 3. Their weights are 3, -7 and 4, so the sum is 0. The route to source 0 is [0] and uses no edges. Vertex 5 is unreachable.

For the shifted graph, the source is 3. The route 3 -> 1 -> 4 uses edges 0 and 1 and has cost 2 - 3 = -1, showing that -1 is a finite distance.

In the tied graph, edge IDs 0 and 1 are separate parallel edges from 0 to 1 with the same weight 2. Routes through vertex 1, through vertex 2, or directly to vertex 3 all have shortest distance 5 to vertex 3 and distance 4 to vertex 4. The helper follows the supplied edge IDs correctly in each tested witness.

Result: all 8 helper calls passed.
