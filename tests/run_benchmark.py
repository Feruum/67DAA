import datetime
import json
import os
import pathlib
import platform
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def cpu_name():
    path = pathlib.Path('/proc/cpuinfo')
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith('model name'):
                return line.split(':', 1)[1].strip()
    return platform.processor() or 'Not reported by this runtime'


def main():
    output = ROOT / '.build' / 'Benchmark'
    output.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / 'src' / 'Java').glob('*.java'))
    build = ['javac', '--release', '17', '-encoding', 'UTF-8', '-d', str(output)]
    build += [str(path) for path in sources]
    build += [str(ROOT / 'tests' / 'Benchmark.java')]
    subprocess.run(build, check=True, timeout=60)
    java_version = subprocess.run(['java', '-version'], check=True, capture_output=True,
                                  text=True, timeout=10)
    run = subprocess.run(['java', '-Xmx384m', '-cp', str(output), 'Benchmark'],
                         check=True, capture_output=True, text=True, timeout=180)
    results = [json.loads(line) for line in run.stdout.splitlines()]
    if len(results) != 3 or not all(row['all_warmup_and_measured_answers_valid'] for row in results):
        raise RuntimeError('Missing benchmark sizes or failed validation')

    data = {
        'command': 'python tests/run_benchmark.py',
        'environment': {
            'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'os': platform.platform(),
            'cpu': cpu_name(),
            'logical_cpus_reported': os.cpu_count(),
            'java': (java_version.stderr or java_version.stdout).strip(),
            'python': sys.version.split()[0],
            'heap_limit': '-Xmx384m',
        },
        'generator': {
            'source': 'tests/Benchmark.java: Graph constructor',
            'random': 'java.util.Random',
            'seeds': [2537, 2538, 2539],
            'description': 'For each vertex v=1..n-1, add one edge from a random vertex below v, '
                           'with weight in [-1000,-1]. Add random endpoint pairs, allowing loops '
                           'and parallel edges, with weights in [0,1000] until m=4n. '
                           'Shuffle all edges using the same Random instance.',
            'independent_optimum': 'The n-1 negative edges form a spanning tree. Every other '
                                   'edge is nonnegative, so any different n-1-edge tree costs '
                                   'strictly more. The expected cost is the sum of the '
                                   'generated negative edges, computed before either algorithm.',
        },
        'protocol': {
            'timer': 'System.nanoTime',
            'unit': 'milliseconds',
            'warmup_calls_per_method_per_size': 3,
            'measured_calls_per_method_per_size': 5,
            'order': 'Kruskal then Prim on even runs; Prim then Kruskal on odd runs',
            'includes': ['Input adapter conversion', 'algorithm adjacency or sorting structures',
                         'algorithm computation', 'result object construction'],
            'excludes': ['compilation', 'JVM startup', 'graph generation', 'JSON parsing',
                         'JSON serialization', 'console or file I/O', 'result validation'],
            'validation': 'Before warm-up, and after every warm-up or measured call: exact '
                          'independent minimum cost, one component, n-1 unique original IDs, '
                          'no loops, selected-weight sum, and BFS connectivity. Connected '
                          'with n-1 edges implies acyclic. All selected edges must be negative.',
            'limitations': 'One connected, sparse, planted-tree distribution; all tree edges '
                          'are lighter than all additional edges. These are not general '
                          'random-weight graphs. Five samples on one shared runtime are '
                          'affected by JIT compilation, allocation, garbage collection and '
                          'machine load. No explicit System.gc calls. Measurements do not '
                          'prove asymptotic complexity or establish a universal winner.',
        },
        'results': results,
    }
    target = ROOT / 'tests' / 'benchmark_results.json'
    target.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

    text = ['# Kruskal and Prim benchmark', '',
            'Command: `python tests/run_benchmark.py`', '',
            'All times are real measurements in milliseconds. Each method had three unmeasured '
            'warm-up calls and five measured calls at each size. Both methods used the same '
            'graph and the same timing boundary. Every result was validated outside the timer.', '',
            '| n | m | Seed | Method | Five timings (ms) | Median (ms) |',
            '|---:|---:|---:|---|---|---:|']
    for row in results:
        for method in ['kruskal', 'prim']:
            values = ', '.join(f'{value:.3f}' for value in row[method + '_ms'])
            text.append(f"| {row['n']} | {row['m']} | {row['seed']} | {method.title()} | "
                        f"{values} | {row[method + '_median_ms']:.3f} |")
    text += ['', '## Inputs and independent validation', '',
             data['generator']['description'], '',
             data['generator']['independent_optimum'], '',
             data['protocol']['validation'], '',
             'The generator source and seeds reproduce the complete ordered input edge lists. '
             'The JSON file records all measured samples and actual returned cost, component '
             'count, selected edge count, selected-weight sum and connectivity evidence.', '',
             '## Timing boundary', '',
             'Timer: `System.nanoTime`. The timed region starts immediately before invoking '
             '`Algorithms.kruskal` or `Algorithms.prim` and ends immediately after its result '
             'returns. It includes input conversion, algorithm data-structure construction, '
             'computation and result construction. Compilation, JVM startup, generator work, '
             'JSON parsing/serialization, I/O and verification are excluded. Order alternates '
             'between the two methods on successive measured runs.', '',
             '## Environment', '',
             f"- OS: {data['environment']['os']}",
             f"- CPU: {data['environment']['cpu']}",
             f"- Logical CPUs reported: {data['environment']['logical_cpus_reported']}",
             f"- Python: {data['environment']['python']}",
             '- JVM heap limit: `-Xmx384m`',
             f"- Recorded at: {data['environment']['recorded_at_utc']}", '',
             '```text', data['environment']['java'], '```', '',
             '## Interpretation and limitations', '',
             data['protocol']['limitations'], '',
             'Both implementations have an O(n + m log(m+1)) worst-case time bound with the '
             'chosen standard sorting and lazy priority queue. Input conversion and '
             'adjacency construction add linear work. The measured medians describe these '
             'three inputs and this runtime; the complexity claim follows from the '
             'algorithm structure, not the timings.', '']
    (ROOT / 'tests' / 'benchmark_results.md').write_text('\n'.join(text), encoding='utf-8')
    print('PASS benchmark: 3 sizes, 5 timings per method per size, all forests valid')
    for row in results:
        print(f"n={row['n']}, m={row['m']}: Kruskal median "
              f"{row['kruskal_median_ms']:.3f} ms; Prim median {row['prim_median_ms']:.3f} ms")


if __name__ == '__main__':
    main()
