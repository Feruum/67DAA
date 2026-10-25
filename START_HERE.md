# Java solution

The completed algorithms are in `src/Java/Algorithms.java`. All Java code is compatible with Java 17 and contains no comments.

## Run

Install JDK 17 or newer and Python 3.12 or newer. Open a terminal in this project folder and run:

```sh
python tools/run.py --setup
python tools/run.py --check
python tools/run.py --input tests/cases.jsonl
```

On Windows, `py -3` can replace `python`.

The program reads one JSON object per line. Example:

```json
{"task":"dsu","n":4,"operations":[[0,1],[1,2],[0,2],[3,3]]}
```

Result:

```json
{"states":[[3,2],[2,3],[2,3],[2,3]]}
```

`Main.java` reads the input and chooses the task. `Input.java` converts JSON values into Java arrays. `Algorithms.java` solves the graph problem. `Json.java` writes the result. The entry point and the input/output adapters were supplied with the course template.

## Files to read

| File | Purpose |
|---|---|
| `src/Java/Algorithms.java` | DSU, Kruskal, Prim, Kosaraju SCC, DFS topological sort, DAG shortest paths and route reconstruction. |
| `ANALYSIS.md` | English explanations, correctness arguments, complexity, actual tests, route examples and benchmark. |
| `tests/CASES.md` | Own test cases with independently justified expected answers. |
| `tests/results.txt` | Actual own-test and full-limit results. |
| `tests/evidence/public_check.txt` | Actual public-check output. |
| `tests/routes_results.md` | Actual route-helper calls and edge IDs. |
| `tests/benchmark_results.md` | Five measured runs per method at each of three sizes. |
| `submission.json` | Selects Java. |

## Run all own checks

```sh
python tests/run_tests.py
python tests/run_routes.py
python tests/run_benchmark.py
```

These commands rebuild the Java classes as needed. Full-size inputs, expected answers and actual outputs are included under `tests/large/` as gzip-compressed JSON Lines. The test generator reproduces them.

## Submit

1. Open the [course template](https://github.com/RZhaniya/daa-assignment-3-graphs) and choose **Use this template -> Create a new repository**.
2. Copy the contents of this project into your new repository, including `.github/workflows/public.yml`, `src`, `tests`, `tools`, `submission.json` and `ANALYSIS.md`.
3. Commit and push the files. Check **Actions -> Public checks** in your repository.
4. Open the completed commit and copy its exact URL. It has the form `https://github.com/USERNAME/REPOSITORY/commit/COMMIT_HASH`.
5. Paste that commit URL into Moodle Online text and click **Submit assignment**. Give the teacher access if the repository is private.

The recorded results are local checks. A GitHub repository has not been created or pushed, and the assignment has not been submitted to Moodle from this project preparation.
