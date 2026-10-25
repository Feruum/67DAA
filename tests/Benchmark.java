import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public class Benchmark {
    static final int WARMUP = 3;
    static final int RUNS = 5;

    static class Graph {
        int n;
        int[][] edges;
        long expectedCost;
        Map<String, Object> input;

        Graph(int n, int m, long seed) {
            this.n = n;
            Random random = new Random(seed);
            List<int[]> rows = new ArrayList<>();

            for (int vertex = 1; vertex < n; vertex++) {
                int weight = -1 - random.nextInt(1000);
                rows.add(new int[]{random.nextInt(vertex), vertex, weight});
                expectedCost += weight;
            }

            while (rows.size() < m) {
                rows.add(new int[]{random.nextInt(n), random.nextInt(n),
                        random.nextInt(1001)});
            }
            Collections.shuffle(rows, random);
            edges = rows.toArray(new int[0][]);

            List<List<Integer>> inputEdges = new ArrayList<>();
            for (int[] edge : edges) {
                inputEdges.add(Arrays.asList(edge[0], edge[1], edge[2]));
            }
            input = new LinkedHashMap<>();
            input.put("n", n);
            input.put("edges", inputEdges);
        }
    }

    static Map<String, Object> solve(String method, Graph graph) {
        if (method.equals("kruskal")) {
            return Algorithms.kruskal(graph.input);
        }
        return Algorithms.prim(graph.input);
    }

    static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }

    static Map<String, Object> validateForest(Graph graph, Map<String, Object> answer) {
        long cost = ((Number) answer.get("cost")).longValue();
        int components = ((Number) answer.get("components")).intValue();
        List<?> ids = (List<?>) answer.get("edge_ids");
        require(cost == graph.expectedCost, "Wrong minimum cost");
        require(components == 1, "Generated graph must be connected");
        require(ids.size() == graph.n - 1, "Wrong number of forest edges");

        boolean[] selected = new boolean[graph.edges.length];
        List<List<Integer>> adjacency = new ArrayList<>();
        for (int vertex = 0; vertex < graph.n; vertex++) {
            adjacency.add(new ArrayList<>());
        }

        long sum = 0;
        for (Object value : ids) {
            int id = ((Number) value).intValue();
            require(id >= 0 && id < graph.edges.length, "Invalid edge ID");
            require(!selected[id], "Repeated edge ID");
            selected[id] = true;
            int[] edge = graph.edges[id];
            require(edge[0] != edge[1], "A forest cannot select a loop");
            require(edge[2] < 0, "The unique minimum tree uses only negative edges");
            adjacency.get(edge[0]).add(edge[1]);
            adjacency.get(edge[1]).add(edge[0]);
            sum += edge[2];
        }
        require(sum == cost, "Selected weights do not match cost");

        boolean[] visited = new boolean[graph.n];
        int[] queue = new int[graph.n];
        int head = 0;
        int tail = 1;
        queue[0] = 0;
        visited[0] = true;
        while (head < tail) {
            int vertex = queue[head++];
            for (int next : adjacency.get(vertex)) {
                if (!visited[next]) {
                    visited[next] = true;
                    queue[tail++] = next;
                }
            }
        }
        require(tail == graph.n, "Selected forest does not span the graph");

        Map<String, Object> evidence = new LinkedHashMap<>();
        evidence.put("cost", cost);
        evidence.put("components", components);
        evidence.put("selected_edge_count", ids.size());
        evidence.put("selected_weight_sum", sum);
        evidence.put("vertices_reached", tail);
        evidence.put("unique_original_ids", true);
        evidence.put("no_loops", true);
        evidence.put("acyclic", true);
        evidence.put("contains_exactly_the_known_minimum_tree", true);
        return evidence;
    }

    static double measure(String method, Graph graph) {
        long start = System.nanoTime();
        Map<String, Object> answer = solve(method, graph);
        long elapsed = System.nanoTime() - start;
        validateForest(graph, answer);
        return elapsed / 1_000_000.0;
    }

    static double median(double[] times) {
        double[] sorted = times.clone();
        Arrays.sort(sorted);
        return sorted[sorted.length / 2];
    }

    public static void main(String[] args) {
        int[] sizes = {1000, 10000, 50000};
        for (int index = 0; index < sizes.length; index++) {
            int n = sizes[index];
            int m = n * 4;
            long seed = 2537L + index;
            Graph graph = new Graph(n, m, seed);

            Map<String, Object> kruskalCheck = validateForest(graph, solve("kruskal", graph));
            Map<String, Object> primCheck = validateForest(graph, solve("prim", graph));

            for (int run = 0; run < WARMUP; run++) {
                if (run % 2 == 0) {
                    validateForest(graph, solve("kruskal", graph));
                    validateForest(graph, solve("prim", graph));
                } else {
                    validateForest(graph, solve("prim", graph));
                    validateForest(graph, solve("kruskal", graph));
                }
            }

            double[] kruskalTimes = new double[RUNS];
            double[] primTimes = new double[RUNS];
            for (int run = 0; run < RUNS; run++) {
                if (run % 2 == 0) {
                    kruskalTimes[run] = measure("kruskal", graph);
                    primTimes[run] = measure("prim", graph);
                } else {
                    primTimes[run] = measure("prim", graph);
                    kruskalTimes[run] = measure("kruskal", graph);
                }
            }

            Map<String, Object> result = new LinkedHashMap<>();
            result.put("n", n);
            result.put("m", m);
            result.put("seed", seed);
            result.put("expected_cost", graph.expectedCost);
            result.put("warmup_per_method", WARMUP);
            result.put("measured_runs_per_method", RUNS);
            result.put("validated_calls_per_method", 1 + WARMUP + RUNS);
            result.put("kruskal_ms", kruskalTimes);
            result.put("prim_ms", primTimes);
            result.put("kruskal_median_ms", median(kruskalTimes));
            result.put("prim_median_ms", median(primTimes));
            result.put("kruskal_validation", kruskalCheck);
            result.put("prim_validation", primCheck);
            result.put("all_warmup_and_measured_answers_valid", true);
            System.out.println(Json.write(result));
        }
    }
}
