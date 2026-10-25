import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class RouteTests {
    static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }

    static Map<String, Object> request(int n, int source, int[][] edges) {
        List<List<Integer>> rows = new ArrayList<>();
        for (int[] edge : edges) {
            rows.add(Arrays.asList(edge[0], edge[1], edge[2]));
        }
        Map<String, Object> input = new LinkedHashMap<>();
        input.put("task", "dag");
        input.put("n", n);
        input.put("source", source);
        input.put("edges", rows);
        return input;
    }

    static void checkDistances(Map<String, Object> answer, Long[] expected) {
        require(Boolean.TRUE.equals(answer.get("acyclic")), "Graph must be acyclic");
        Long[] distance = (Long[]) answer.get("distance");
        require(Arrays.equals(distance, expected), "Wrong shortest distances");
    }

    static Map<String, Object> checkRoute(String name, String call, int source,
            int target, int[][] edges, int[] parentEdge, Long[] distance) {
        List<Integer> route = Algorithms.reconstructPath(source, target, edges, parentEdge);
        List<Integer> selected = new ArrayList<>();
        List<int[]> directedEdges = new ArrayList<>();
        Long total = null;

        if (distance[target] == null) {
            require(route.isEmpty(), "Unreachable target must return an empty list");
            require(parentEdge[target] == -1, "Unreachable target has a parent");
        } else {
            require(!route.isEmpty(), "Reachable route must not be empty");
            require(route.get(0) == source, "Route must start at source");
            require(route.get(route.size() - 1) == target, "Route must end at target");
            require(route.size() <= distance.length, "Route repeats vertices");
            total = 0L;

            for (int index = 1; index < route.size(); index++) {
                int from = route.get(index - 1);
                int to = route.get(index);
                int edgeId = parentEdge[to];
                require(edgeId >= 0 && edgeId < edges.length, "Invalid parent edge ID");
                int[] edge = edges[edgeId];
                require(edge[0] == from && edge[1] == to, "Wrong parent edge direction");
                selected.add(edgeId);
                directedEdges.add(edge);
                total += edge[2];
            }
            require(total.equals(distance[target]), "Route weight differs from shortest distance");
            if (target == source) {
                require(route.equals(Arrays.asList(source)), "Source route must be a singleton");
                require(parentEdge[source] == -1, "Source must not have a parent");
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("name", name);
        result.put("call", call);
        result.put("source", source);
        result.put("target", target);
        result.put("parent_edge", parentEdge);
        result.put("route", route);
        result.put("selected_edge_ids", selected);
        result.put("directed_edges", directedEdges);
        result.put("total_weight", total);
        result.put("expected_distance", distance[target]);
        result.put("direction_verified", distance[target] != null);
        result.put("passed", true);
        return result;
    }

    public static void main(String[] args) {
        int[][] baseEdges = {
            {0, 1, 3}, {0, 2, 8}, {1, 2, -7}, {2, 3, 4}, {1, 4, 2}
        };
        Map<String, Object> baseInput = request(6, 0, baseEdges);
        Map<String, Object> base = Algorithms.dag(baseInput);
        checkDistances(base, new Long[]{0L, 3L, -4L, 0L, 5L, null});
        Long[] baseDistance = (Long[]) base.get("distance");
        int[] baseParents = (int[]) base.get("parent_edge");

        List<Map<String, Object>> checks = new ArrayList<>();
        checks.add(checkRoute("reachable target", "reconstructPath(0, 3, baseEdges, baseParents)",
                0, 3, baseEdges, baseParents, baseDistance));
        checks.add(checkRoute("source target", "reconstructPath(0, 0, baseEdges, baseParents)",
                0, 0, baseEdges, baseParents, baseDistance));
        checks.add(checkRoute("unreachable target", "reconstructPath(0, 5, baseEdges, baseParents)",
                0, 5, baseEdges, baseParents, baseDistance));

        int[][] shiftedEdges = {{3, 1, 2}, {1, 4, -3}, {3, 4, 5}, {0, 2, 1}};
        Map<String, Object> shiftedInput = request(5, 3, shiftedEdges);
        Map<String, Object> shifted = Algorithms.dag(shiftedInput);
        checkDistances(shifted, new Long[]{null, 2L, null, 0L, -1L});
        checks.add(checkRoute("nonzero source and distance minus one",
                "reconstructPath(3, 4, shiftedEdges, shiftedParents)", 3, 4, shiftedEdges,
                (int[]) shifted.get("parent_edge"), (Long[]) shifted.get("distance")));

        int[][] tiedEdges = {
            {0, 1, 2}, {0, 1, 2}, {0, 2, 2}, {1, 3, 3},
            {2, 3, 3}, {0, 3, 5}, {3, 4, -1}
        };
        Map<String, Object> tiedInput = request(5, 0, tiedEdges);
        Map<String, Object> tied = Algorithms.dag(tiedInput);
        checkDistances(tied, new Long[]{0L, 2L, 2L, 5L, 4L});
        Long[] tiedDistance = (Long[]) tied.get("distance");
        int[] tiedParents = (int[]) tied.get("parent_edge");
        checks.add(checkRoute("parallel edge from actual DAG result",
                "reconstructPath(0, 1, tiedEdges, tiedParents)",
                0, 1, tiedEdges, tiedParents, tiedDistance));
        checks.add(checkRoute("tied route from actual DAG result",
                "reconstructPath(0, 4, tiedEdges, tiedParents)",
                0, 4, tiedEdges, tiedParents, tiedDistance));

        int[] alternateParallelParents = {-1, 1, 2, 3, 6};
        checks.add(checkRoute("alternative valid parallel edge and tied route",
                "reconstructPath(0, 4, tiedEdges, alternateParallelParents)",
                0, 4, tiedEdges, alternateParallelParents, tiedDistance));

        int[] alternateBranchParents = {-1, 0, 2, 4, 6};
        checks.add(checkRoute("alternative valid tied branch",
                "reconstructPath(0, 4, tiedEdges, alternateBranchParents)",
                0, 4, tiedEdges, alternateBranchParents, tiedDistance));

        Map<String, Object> output = new LinkedHashMap<>();
        output.put("base_input", baseInput);
        output.put("base_dag_result", base);
        output.put("shifted_input", shiftedInput);
        output.put("shifted_dag_result", shifted);
        output.put("tied_input", tiedInput);
        output.put("tied_dag_result", tied);
        output.put("helper_calls", checks);
        output.put("passed", checks.size());
        System.out.println(Json.write(output));
    }
}
