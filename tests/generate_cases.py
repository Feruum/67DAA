import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def small_cases():
    cases = []

    def add(name, request, expected, reason):
        cases.append((name, request, expected, reason))

    add('ping', {'task': 'ping'}, {'status': 'ready'}, 'The transport contract returns ready.')
    add('dsu_empty', {'task': 'dsu', 'n': 0, 'operations': []}, {'states': []}, 'No operations produce no states.')
    add('dsu_no_operations', {'task': 'dsu', 'n': 5, 'operations': []}, {'states': []}, 'An initial state must not be included.')
    add('dsu_repeats_and_self', {'task': 'dsu', 'n': 5, 'operations': [[0, 0], [0, 1], [1, 0], [2, 3], [1, 2], [4, 4], [3, 4]]}, {'states': [[5, 1], [4, 2], [4, 2], [3, 2], [2, 4], [2, 4], [1, 5]]}, 'Self/repeated unions do not merge; the successful merges create sets of size 2, 2, 4 and 5.')
    add('dsu_singleton', {'task': 'dsu', 'n': 1, 'operations': [[0, 0], [0, 0]]}, {'states': [[1, 1], [1, 1]]}, 'The only vertex remains one component of size one.')

    for task in ('kruskal', 'prim'):
        add(task + '_empty', {'task': task, 'n': 0, 'edges': []}, {'cost': 0, 'edge_ids': [], 'components': 0}, 'The empty forest has zero vertices, edges, cost and components.')
        add(task + '_isolates', {'task': task, 'n': 4, 'edges': []}, {'cost': 0, 'edge_ids': [], 'components': 4}, 'Every isolated vertex is a separate component.')
        add(task + '_negative_parallel_loops', {'task': task, 'n': 6, 'edges': [[0, 0, -100], [0, 1, 5], [0, 1, -2], [1, 2, 3], [0, 2, 9], [3, 4, -7], [4, 4, -20]]}, {'cost': -6, 'edge_ids': [2, 3, 5], 'components': 3}, 'The components are {0,1,2}, {3,4}, {5}; their minimum costs are 1, -7 and 0. Loops cannot enter a forest.')
        add(task + '_tied_forest', {'task': task, 'n': 4, 'edges': [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 0, 1], [0, 2, 1], [0, 1, 1]]}, {'cost': 3, 'edge_ids': [0, 1, 2], 'components': 1}, 'A connected four-vertex graph needs three edges, each of weight one; many optimal witnesses exist.')
        add(task + '_positive_64bit', {'task': task, 'n': 5, 'edges': [[0, 1, 1000000000], [1, 2, 1000000000], [2, 3, 1000000000], [3, 4, 1000000000]]}, {'cost': 4000000000, 'edge_ids': [0, 1, 2, 3], 'components': 1}, 'The input itself is a tree, so all four billion-weight edges are necessary.')
        add(task + '_negative_64bit', {'task': task, 'n': 5, 'edges': [[0, 1, -1000000000], [1, 2, -1000000000], [2, 3, -1000000000], [3, 4, -1000000000]]}, {'cost': -4000000000, 'edge_ids': [0, 1, 2, 3], 'components': 1}, 'The only spanning tree has four edges with weight minus one billion.')
        add(task + '_loops_only', {'task': task, 'n': 2, 'edges': [[0, 0, -8], [1, 1, -9]]}, {'cost': 0, 'edge_ids': [], 'components': 2}, 'Loops connect no distinct vertices and are never selected.')

    add('scc_empty', {'task': 'scc', 'n': 0, 'edges': []}, {'component': [], 'condensation': []}, 'There are no components or cross-component edges.')
    add('scc_isolates', {'task': 'scc', 'n': 4, 'edges': []}, {'component': [0, 1, 2, 3], 'condensation': []}, 'Each isolated vertex is its own SCC.')
    add('scc_partition_and_deduplication', {'task': 'scc', 'n': 7, 'edges': [[0, 1], [1, 0], [0, 2], [1, 2], [1, 2], [2, 3], [3, 2], [3, 4], [4, 4], [5, 6], [6, 5]]}, {'component': [0, 0, 1, 1, 2, 3, 3], 'condensation': [[0, 1], [1, 2]]}, 'Mutual reachability gives {0,1}, {2,3}, {4}, {5,6}. Only the first-to-second and second-to-third SCC pairs cross components.')
    add('scc_one_cycle', {'task': 'scc', 'n': 4, 'edges': [[0, 1], [1, 2], [2, 3], [3, 0], [1, 1]]}, {'component': [0, 0, 0, 0], 'condensation': []}, 'The directed cycle reaches every vertex from every other vertex.')

    add('topo_empty', {'task': 'topo', 'n': 0, 'edges': []}, {'acyclic': True, 'order': []}, 'The empty order is valid.')
    add('topo_isolates', {'task': 'topo', 'n': 4, 'edges': []}, {'acyclic': True, 'order': [0, 1, 2, 3]}, 'With no dependencies, any permutation is valid.')
    add('topo_finished_neighbor', {'task': 'topo', 'n': 4, 'edges': [[0, 1], [0, 2], [1, 2], [1, 2], [2, 3]]}, {'acyclic': True, 'order': [0, 1, 2, 3]}, 'All edges increase vertex numbers; the later edge to a finished vertex is not a back edge.')
    add('topo_self_loop', {'task': 'topo', 'n': 2, 'edges': [[1, 1]]}, {'acyclic': False, 'order': []}, 'A self-loop is a cycle, even in another component.')
    add('topo_disconnected_cycle', {'task': 'topo', 'n': 6, 'edges': [[0, 1], [1, 2], [3, 4], [4, 5], [5, 3]]}, {'acyclic': False, 'order': []}, 'The separate 3->4->5->3 cycle prevents a whole-graph order.')
    add('topo_multiple_orders', {'task': 'topo', 'n': 4, 'edges': [[0, 2], [1, 2], [2, 3]]}, {'acyclic': True, 'order': [0, 1, 2, 3]}, 'Vertices 0 and 1 can be exchanged; both must occur before 2, then 3.')

    add('dag_singleton', {'task': 'dag', 'n': 1, 'source': 0, 'edges': []}, {'acyclic': True, 'distance': [0], 'parent_edge': [-1]}, 'The source has distance zero and no parent.')
    add('dag_isolated_source', {'task': 'dag', 'n': 4, 'source': 2, 'edges': []}, {'acyclic': True, 'distance': [None, None, 0, None], 'parent_edge': [-1, -1, -1, -1]}, 'Only the source is reachable.')
    add('dag_negative_and_unreachable', {'task': 'dag', 'n': 6, 'source': 0, 'edges': [[0, 1, 3], [0, 2, 8], [1, 2, -7], [2, 3, 4], [4, 5, -100]]}, {'acyclic': True, 'distance': [0, 3, -4, 0, None, None], 'parent_edge': [-1, 0, 2, 3, -1, -1]}, 'The route 0->1->2->3 costs 0. The unrelated negative edge 4->5 cannot make either endpoint reachable.')
    add('dag_minus_one_distance', {'task': 'dag', 'n': 3, 'source': 0, 'edges': [[0, 1, -1]]}, {'acyclic': True, 'distance': [0, -1, None], 'parent_edge': [-1, 0, -1]}, 'Distance -1 is a finite value; only vertex 2 is unreachable.')
    add('dag_nonzero_source', {'task': 'dag', 'n': 5, 'source': 2, 'edges': [[0, 2, -9], [2, 1, 7], [1, 3, -2], [2, 3, 8]]}, {'acyclic': True, 'distance': [None, 7, 0, 5, None], 'parent_edge': [-1, 1, -1, 2, -1]}, 'The unreachable predecessor 0 cannot change the source distance; the cheapest route to 3 goes through 1.')
    add('dag_ties_and_parallel', {'task': 'dag', 'n': 4, 'source': 0, 'edges': [[0, 1, 2], [0, 1, 2], [0, 2, 1], [1, 3, 1], [2, 3, 2]]}, {'acyclic': True, 'distance': [0, 2, 1, 3], 'parent_edge': [-1, 0, 2, 3]}, 'Either parallel edge reaches 1, and either path to 3 has total cost 3.')
    add('dag_positive_64bit', {'task': 'dag', 'n': 5, 'source': 0, 'edges': [[0, 1, 1000000000], [1, 2, 1000000000], [2, 3, 1000000000], [3, 4, 1000000000]]}, {'acyclic': True, 'distance': [0, 1000000000, 2000000000, 3000000000, 4000000000], 'parent_edge': [-1, 0, 1, 2, 3]}, 'Unique prefix paths cost k times one billion.')
    add('dag_negative_64bit', {'task': 'dag', 'n': 5, 'source': 0, 'edges': [[0, 1, -1000000000], [1, 2, -1000000000], [2, 3, -1000000000], [3, 4, -1000000000]]}, {'acyclic': True, 'distance': [0, -1000000000, -2000000000, -3000000000, -4000000000], 'parent_edge': [-1, 0, 1, 2, 3]}, 'Unique prefix paths cost minus k times one billion.')
    add('dag_unreachable_cycle', {'task': 'dag', 'n': 5, 'source': 0, 'edges': [[0, 1, 7], [2, 3, -2], [3, 2, 2]]}, {'acyclic': False, 'distance': [], 'parent_edge': []}, 'The unreachable 2->3->2 cycle still makes the entire graph non-DAG.')
    add('dag_unreachable_self_loop', {'task': 'dag', 'n': 3, 'source': 0, 'edges': [[0, 1, 1], [2, 2, -4]]}, {'acyclic': False, 'distance': [], 'parent_edge': []}, 'The disconnected self-loop is a cycle.')
    return cases


def large_cases():
    n = 100000
    count = 250000
    operations = [[i, i + 1] for i in range(n - 1)]
    operations.extend([[i % n, i % n] if i % 2 else [0, n - 1] for i in range(count - len(operations))])
    states = [[n - i - 1, i + 2] for i in range(n - 1)]
    states.extend([[1, n] for _ in range(count - len(states))])
    yield ('dsu_full', {'task': 'dsu', 'n': n, 'operations': operations}, {'states': states}, 'The chain merges the first i+2 vertices after operation i; later self/repeated unions keep [1,100000].')
    del operations, states

    edges = [[i, i + 1, -1000000000] for i in range(n - 1)]
    edges.extend([[i, i, -1000000000] for i in range(n)])
    edges.extend([[i, i + 1, -999999999] for i in range(count - len(edges))])
    expected = {'cost': -(n - 1) * 1000000000, 'edge_ids': list(range(n - 1)), 'components': 1}
    for task in ('kruskal', 'prim'):
        yield (task + '_full', {'task': task, 'n': n, 'edges': edges}, expected, 'The graph is a chain with loops and more expensive parallel edges. Each cut needs its -1000000000 chain edge; total -99999000000000.')
    del edges, expected

    edges = [[i, i + 1] for i in range(n - 1)]
    edges.extend([[i, i] for i in range(n)])
    edges.extend([[i, i + 1] for i in range(count - len(edges))])
    yield ('scc_full_chain', {'task': 'scc', 'n': n, 'edges': edges}, {'component': list(range(n)), 'condensation': [[i, i + 1] for i in range(n - 1)]}, 'Every non-loop edge moves forward, so every vertex is a separate SCC. Duplicate edges collapse to the chain condensation.')
    del edges

    edges = [[i, (i + 1) % n] for i in range(n)]
    edges.extend([[i % n, (i + 1) % n] for i in range(count - len(edges))])
    yield ('scc_full_cycle', {'task': 'scc', 'n': n, 'edges': edges}, {'component': [0] * n, 'condensation': []}, 'The first 100000 edges form one directed cycle through all vertices, so there is one SCC.')
    yield ('topo_full_cycle', {'task': 'topo', 'n': n, 'edges': edges}, {'acyclic': False, 'order': []}, 'The all-vertex directed cycle has no topological order.')
    del edges

    edges = [[i % (n - 1), i % (n - 1) + 1] for i in range(count)]
    yield ('topo_full_chain', {'task': 'topo', 'n': n, 'edges': edges}, {'acyclic': True, 'order': list(range(n))}, 'The chain requires increasing vertex order; duplicate edges do not introduce cycles.')
    del edges

    edges = [[i % (n - 1), i % (n - 1) + 1, -1000000000] for i in range(count)]
    yield ('dag_full_chain', {'task': 'dag', 'n': n, 'source': 0, 'edges': edges}, {'acyclic': True, 'distance': [-i * 1000000000 for i in range(n)], 'parent_edge': [-1] + list(range(n - 1))}, 'Every source-to-k route takes exactly k chain steps, giving distance -k*1000000000; duplicate edge IDs provide valid alternative parents.')
    del edges

    edges = [[i, i + 1, 1] for i in range(n - 3)]
    edges.extend([[n - 2, n - 1, 1], [n - 1, n - 2, -1]])
    edges.extend([[i % (n - 3), i % (n - 3) + 1, 1] for i in range(count - len(edges))])
    yield ('dag_full_unreachable_cycle', {'task': 'dag', 'n': n, 'source': 0, 'edges': edges}, {'acyclic': False, 'distance': [], 'parent_edge': []}, 'Vertices 99998 and 99999 form a cycle disconnected from source 0; whole-graph cycle checking must reject it.')


def write_jsonl(path, values):
    with path.open('w', encoding='utf-8') as output:
        for value in values:
            output.write(json.dumps(value, separators=(',', ':')) + '\n')


def write_small_files():
    cases = small_cases()
    write_jsonl(BASE / 'cases.jsonl', [case[1] for case in cases])
    write_jsonl(BASE / 'expected.jsonl', [case[2] for case in cases])
    lines = ['# Own test cases', '', 'Each row matches the same line in `cases.jsonl` and `expected.jsonl`. Expected outputs show one valid witness; the runner accepts any witness satisfying the contract.', '', '| Line | Case | Independent expected-answer justification |', '|---|---|---|']
    for index, (name, request, expected, reason) in enumerate(cases, 1):
        lines.append(f'| {index} | {name} | {reason} |')
    lines.extend(['', '## Full limits', '', 'All nine large cases use `n=100000` and exactly `250000` edges or union operations. Generation is deterministic; no random seed is needed. `generate_cases.py` is the stored input recipe.', '', '`large/inputs.jsonl.gz`, `large/expected.jsonl.gz` and `large/actual.jsonl.gz` hold the complete inputs, independently derived expected answers and measured Java outputs. The case order and reasons are in `large/cases.json`. Standard gzip decompression gives UTF-8 JSON Lines.', '', '## Commands', '', 'Run from the repository root with JDK 17+ and Python 3.12+:', '', '```sh', 'python tests/run_tests.py', '```', '', 'This compiles once, runs the small inputs, repeats mixed requests in one process, checks alternative and invalid witnesses, then runs all full-limit cases with the supplied 384 MiB Java heap and a 20-second limit for each input batch. Actual results and `results.txt` are regenerated from real executions.', '', 'To run only the small inputs through the provided launcher:', '', '```sh', 'python tools/run.py --input tests/cases.jsonl', '```', '', 'The separate route-helper and benchmark commands are documented in `ANALYSIS.md`.', ''])
    (BASE / 'CASES.md').write_text('\n'.join(lines), encoding='utf-8')
    return cases


if __name__ == '__main__':
    cases = write_small_files()
    print(f'Wrote {len(cases)} small input/expected pairs.')
