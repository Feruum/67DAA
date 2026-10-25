import json
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    output = ROOT / '.build' / 'Routes'
    output.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / 'src' / 'Java').glob('*.java'))
    build = ['javac', '--release', '17', '-encoding', 'UTF-8', '-d', str(output)]
    build += [str(path) for path in sources]
    build += [str(ROOT / 'tests' / 'RouteTests.java')]
    subprocess.run(build, check=True, timeout=60)
    run = subprocess.run(['java', '-Xmx384m', '-cp', str(output), 'RouteTests'],
                         check=True, capture_output=True, text=True, timeout=20)
    result = json.loads(run.stdout)
    if result['passed'] != 8 or not all(item['passed'] for item in result['helper_calls']):
        raise RuntimeError('Missing or failed route-helper checks')
    result['command'] = 'python tests/run_routes.py'
    (ROOT / 'tests' / 'routes_results.json').write_text(json.dumps(result, indent=2) + '\n',
                                                      encoding='utf-8')
    text = ['# Route helper tests', '', 'Command: `python tests/run_routes.py`', '',
            'Every row below comes from an executed call to the Java helper. Expected shortest '
            'distances are written explicitly in `RouteTests.java`. Reachable routes are '
            'checked for their endpoints, directed original parent edges and total weight. '
            'Unreachable routes return an empty list.', '',
            '| Check | Helper call | Returned vertices | Edge IDs | Weight |',
            '|---|---|---|---|---:|']
    for item in result['helper_calls']:
        weight = 'No route' if item['total_weight'] is None else str(item['total_weight'])
        text.append(f"| {item['name']} | `{item['call']}` | `{item['route']}` | "
                    f"`{item['selected_edge_ids']}` | {weight} |")
    text += ['', '## Input and parent evidence', '',
             '`routes_results.json` stores the complete inputs, actual DAG results, every '
             'parent array, selected edge IDs, directed edge rows and verified weights. '
             'The alternative parallel and branch cases use explicitly supplied valid '
             'shortest-path parents for the same tied graph.', '',
             'For the base graph, the reachable route to 3 is 0 -> 1 -> 2 -> 3, using '
             'edges 0, 2 and 3. Their weights are 3, -7 and 4, so the sum is 0. '
             'The route to source 0 is [0] and uses no edges. Vertex 5 is unreachable.', '',
             'For the shifted graph, the source is 3. The route 3 -> 1 -> 4 uses edges '
             '0 and 1 and has cost 2 - 3 = -1, showing that -1 is a finite distance.', '',
             'In the tied graph, edge IDs 0 and 1 are separate parallel edges from 0 to 1 '
             'with the same weight 2. Routes through vertex 1, through vertex 2, or directly '
             'to vertex 3 all have shortest distance 5 to vertex 3 and distance 4 to vertex 4. '
             'The helper follows the supplied edge IDs correctly in each tested witness.', '',
             'Result: all 8 helper calls passed.', '']
    (ROOT / 'tests' / 'routes_results.md').write_text('\n'.join(text), encoding='utf-8')
    print('PASS route helper: 8 calls with directed edge and weight verification')


if __name__ == '__main__':
    main()
