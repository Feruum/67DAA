import gzip
import json
import platform
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path.insert(0, str(ROOT / 'tools'))
from public_validate import check
from run import build, execute
from generate_cases import large_cases, write_jsonl, write_small_files


def witness_tests(cases):
    by_name = {case[0]: case for case in cases}
    records = []

    def verify(name, case_name, answer, wanted):
        _, request, expected, _ = by_name[case_name]
        accepted = check(request, answer, expected)
        if accepted != wanted:
            raise AssertionError(name)
        records.append({'name': name, 'input': request, 'expected': expected, 'witness': answer, 'should_accept': wanted, 'accepted': accepted})

    for task in ('kruskal', 'prim'):
        verify(task + '_alternative_valid', task + '_tied_forest', {'cost': 3, 'edge_ids': [3, 4, 5], 'components': 1}, True)
        verify(task + '_invalid_cycle', task + '_tied_forest', {'cost': 3, 'edge_ids': [0, 1, 4], 'components': 1}, False)
        verify(task + '_invalid_duplicate', task + '_tied_forest', {'cost': 3, 'edge_ids': [0, 0, 2], 'components': 1}, False)

    verify('scc_alternative_labels', 'scc_partition_and_deduplication', {'component': [8, 8, 4, 4, 15, 99, 99], 'condensation': [[4, 15], [8, 4]]}, True)
    verify('scc_invalid_merge', 'scc_partition_and_deduplication', {'component': [0, 0, 0, 0, 2, 3, 3], 'condensation': [[0, 2]]}, False)
    verify('scc_invalid_missing_pair', 'scc_partition_and_deduplication', {'component': [0, 0, 1, 1, 2, 3, 3], 'condensation': [[0, 1]]}, False)
    verify('scc_invalid_duplicate_pair', 'scc_partition_and_deduplication', {'component': [0, 0, 1, 1, 2, 3, 3], 'condensation': [[0, 1], [0, 1], [1, 2]]}, False)

    verify('topo_alternative_valid', 'topo_multiple_orders', {'acyclic': True, 'order': [1, 0, 2, 3]}, True)
    verify('topo_invalid_precedence', 'topo_multiple_orders', {'acyclic': True, 'order': [0, 2, 1, 3]}, False)
    verify('topo_invalid_duplicate', 'topo_multiple_orders', {'acyclic': True, 'order': [0, 0, 2, 3]}, False)

    verify('dag_alternative_valid', 'dag_ties_and_parallel', {'acyclic': True, 'distance': [0, 2, 1, 3], 'parent_edge': [-1, 1, 2, 4]}, True)
    verify('dag_invalid_parent_endpoint', 'dag_ties_and_parallel', {'acyclic': True, 'distance': [0, 2, 1, 3], 'parent_edge': [-1, 2, 2, 3]}, False)
    verify('dag_invalid_missing_parent', 'dag_ties_and_parallel', {'acyclic': True, 'distance': [0, 2, 1, 3], 'parent_edge': [-1, 0, 2, -1]}, False)
    verify('dag_invalid_unreachable_parent', 'dag_negative_and_unreachable', {'acyclic': True, 'distance': [0, 3, -4, 0, None, None], 'parent_edge': [-1, 0, 2, 3, -1, 4]}, False)
    write_jsonl(BASE / 'witness_checks.jsonl', records)
    return len(records)


def main():
    messages = []

    def log(message):
        print(message, flush=True)
        messages.append(message)

    log('Command: python tests/run_tests.py')
    log('Python: ' + platform.python_version())
    log('Java execution: java -Xmx384m -cp .build/Java Main')
    log('Timeout: 20 seconds per Java input batch')
    command = build('Java')
    cases = write_small_files()
    answers = execute(command, [case[1] for case in cases])
    write_jsonl(BASE / 'actual.jsonl', answers)
    for case, answer in zip(cases, answers):
        if not check(case[1], answer, case[2]):
            raise AssertionError('Small case failed: ' + case[0])
    log(f'PASS small cases: {len(cases)}')

    mixed = cases + list(reversed(cases)) + cases
    answers = execute(command, [case[1] for case in mixed])
    write_jsonl(BASE / 'mixed_inputs.jsonl', [case[1] for case in mixed])
    write_jsonl(BASE / 'mixed_expected.jsonl', [case[2] for case in mixed])
    write_jsonl(BASE / 'mixed_actual.jsonl', answers)
    for case, answer in zip(mixed, answers):
        if not check(case[1], answer, case[2]):
            raise AssertionError('Mixed state-reset case failed: ' + case[0])
    log(f'PASS mixed requests in one process: {len(mixed)}')
    log(f'PASS semantic witness acceptance/rejection checks: {witness_tests(cases)}')

    target = BASE / 'large'
    target.mkdir(exist_ok=True)
    records = []
    with gzip.open(target / 'inputs.jsonl.gz', 'wt', encoding='utf-8', compresslevel=6) as inputs, gzip.open(target / 'expected.jsonl.gz', 'wt', encoding='utf-8', compresslevel=6) as expected_file, gzip.open(target / 'actual.jsonl.gz', 'wt', encoding='utf-8', compresslevel=6) as outputs:
        for name, request, expected, reason in large_cases():
            inputs.write(json.dumps(request, separators=(',', ':')) + '\n')
            expected_file.write(json.dumps(expected, separators=(',', ':')) + '\n')
            started = time.perf_counter()
            answer = execute(command, [request])[0]
            seconds = time.perf_counter() - started
            outputs.write(json.dumps(answer, separators=(',', ':')) + '\n')
            if not check(request, answer, expected):
                raise AssertionError('Full-limit case failed: ' + name)
            count = len(request.get('operations', request.get('edges', [])))
            records.append({'name': name, 'n': request['n'], 'count': count, 'justification': reason, 'execution_seconds': seconds, 'status': 'PASS'})
            log(f'PASS full limits: {name}; n={request["n"]}, edges/operations={count}; execution={seconds:.3f}s')
    (target / 'cases.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    log('PASS all own tests')
    log('Scale execution time includes JSON serialization, Java startup, parsing, algorithm, output and JSON decoding; it is not an algorithm benchmark.')
    (BASE / 'results.txt').write_text('\n'.join(messages) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
