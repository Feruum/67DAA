import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

public final class Algorithms {
    static class DisjointSet {
        int[] parent;
        int[] size;
        int components;
        int largest;

        DisjointSet(int n) {
            parent = new int[n];
            size = new int[n];
            components = n;
            largest = n == 0 ? 0 : 1;

            for (int i = 0; i < n; i++) {
                parent[i] = i;
                size[i] = 1;
            }
        }

        int find(int vertex) {
            int root = vertex;
            while (parent[root] != root) {
                root = parent[root];
            }

            while (vertex != root) {
                int next = parent[vertex];
                parent[vertex] = root;
                vertex = next;
            }
            return root;
        }

        boolean union(int first, int second) {
            int firstRoot = find(first);
            int secondRoot = find(second);
            if (firstRoot == secondRoot) {
                return false;
            }

            if (size[firstRoot] < size[secondRoot]) {
                int temp = firstRoot;
                firstRoot = secondRoot;
                secondRoot = temp;
            }

            parent[secondRoot] = firstRoot;
            size[firstRoot] += size[secondRoot];
            components--;
            largest = Math.max(largest, size[firstRoot]);
            return true;
        }
    }

    static class Edge implements Comparable<Edge> {
        int from;
        int to;
        int weight;
        int id;

        Edge(int from, int to, int weight, int id) {
            this.from = from;
            this.to = to;
            this.weight = weight;
            this.id = id;
        }

        public int compareTo(Edge other) {
            int byWeight = Integer.compare(weight, other.weight);
            if (byWeight != 0) {
                return byWeight;
            }
            return Integer.compare(id, other.id);
        }
    }

    static Map<String, Object> dsu(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] operations = Input.operations(input);
        DisjointSet sets = new DisjointSet(n);
        int[][] states = new int[operations.length][2];

        for (int i = 0; i < operations.length; i++) {
            sets.union(operations[i][0], operations[i][1]);
            states[i][0] = sets.components;
            states[i][1] = sets.largest;
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("states", states);
        return result;
    }

    static Map<String, Object> kruskal(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);
        Edge[] sortedEdges = new Edge[edges.length];

        for (int i = 0; i < edges.length; i++) {
            sortedEdges[i] = new Edge(edges[i][0], edges[i][1], edges[i][2], i);
        }
        Arrays.sort(sortedEdges);

        DisjointSet sets = new DisjointSet(n);
        List<Integer> selected = new ArrayList<>();
        long cost = 0;

        for (Edge edge : sortedEdges) {
            if (sets.union(edge.from, edge.to)) {
                selected.add(edge.id);
                cost += edge.weight;
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("cost", cost);
        result.put("edge_ids", selected);
        result.put("components", sets.components);
        return result;
    }

    static Map<String, Object> prim(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);
        List<List<Edge>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }

        for (int i = 0; i < edges.length; i++) {
            int from = edges[i][0];
            int to = edges[i][1];
            int weight = edges[i][2];
            graph.get(from).add(new Edge(from, to, weight, i));
            graph.get(to).add(new Edge(to, from, weight, i));
        }

        boolean[] visited = new boolean[n];
        PriorityQueue<Edge> queue = new PriorityQueue<>();
        List<Integer> selected = new ArrayList<>();
        long cost = 0;
        int components = 0;

        for (int start = 0; start < n; start++) {
            if (visited[start]) {
                continue;
            }

            components++;
            visited[start] = true;
            for (Edge edge : graph.get(start)) {
                if (!visited[edge.to]) {
                    queue.add(edge);
                }
            }

            while (!queue.isEmpty()) {
                Edge edge = queue.remove();
                if (visited[edge.to]) {
                    continue;
                }

                visited[edge.to] = true;
                selected.add(edge.id);
                cost += edge.weight;

                for (Edge next : graph.get(edge.to)) {
                    if (!visited[next.to]) {
                        queue.add(next);
                    }
                }
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("cost", cost);
        result.put("edge_ids", selected);
        result.put("components", components);
        return result;
    }

    static List<List<Integer>> emptyGraph(int n) {
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        return graph;
    }

    static Map<String, Object> scc(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);
        List<List<Integer>> graph = emptyGraph(n);
        List<List<Integer>> transpose = emptyGraph(n);

        for (int[] edge : edges) {
            graph.get(edge[0]).add(edge[1]);
            transpose.get(edge[1]).add(edge[0]);
        }

        boolean[] visited = new boolean[n];
        int[] next = new int[n];
        int[] stack = new int[n];
        int[] finish = new int[n];
        int finished = 0;

        for (int start = 0; start < n; start++) {
            if (visited[start]) {
                continue;
            }

            int stackSize = 0;
            stack[stackSize++] = start;
            visited[start] = true;

            while (stackSize > 0) {
                int vertex = stack[stackSize - 1];
                if (next[vertex] < graph.get(vertex).size()) {
                    int neighbour = graph.get(vertex).get(next[vertex]++);
                    if (!visited[neighbour]) {
                        visited[neighbour] = true;
                        stack[stackSize++] = neighbour;
                    }
                } else {
                    stackSize--;
                    finish[finished++] = vertex;
                }
            }
        }

        int[] component = new int[n];
        Arrays.fill(component, -1);
        int label = 0;

        for (int i = n - 1; i >= 0; i--) {
            int start = finish[i];
            if (component[start] != -1) {
                continue;
            }

            int stackSize = 0;
            stack[stackSize++] = start;
            component[start] = label;

            while (stackSize > 0) {
                int vertex = stack[--stackSize];
                for (int neighbour : transpose.get(vertex)) {
                    if (component[neighbour] == -1) {
                        component[neighbour] = label;
                        stack[stackSize++] = neighbour;
                    }
                }
            }
            label++;
        }

        Set<Long> seen = new HashSet<>();
        List<int[]> condensation = new ArrayList<>();
        for (int[] edge : edges) {
            int from = component[edge[0]];
            int to = component[edge[1]];
            if (from != to) {
                long key = (long) from * n + to;
                if (seen.add(key)) {
                    condensation.add(new int[] {from, to});
                }
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("component", component);
        result.put("condensation", condensation);
        return result;
    }

    static List<List<Integer>> outgoingEdges(int n, int[][] edges) {
        List<List<Integer>> graph = emptyGraph(n);
        for (int i = 0; i < edges.length; i++) {
            graph.get(edges[i][0]).add(i);
        }
        return graph;
    }

    static int[] topologicalOrder(int n, int[][] edges, List<List<Integer>> graph) {
        int[] state = new int[n];
        int[] next = new int[n];
        int[] stack = new int[n];
        int[] order = new int[n];
        int position = n - 1;

        for (int start = 0; start < n; start++) {
            if (state[start] != 0) {
                continue;
            }

            int stackSize = 0;
            stack[stackSize++] = start;
            state[start] = 1;

            while (stackSize > 0) {
                int vertex = stack[stackSize - 1];
                if (next[vertex] < graph.get(vertex).size()) {
                    int edgeId = graph.get(vertex).get(next[vertex]++);
                    int neighbour = edges[edgeId][1];

                    if (state[neighbour] == 1) {
                        return null;
                    }
                    if (state[neighbour] == 0) {
                        state[neighbour] = 1;
                        stack[stackSize++] = neighbour;
                    }
                } else {
                    stackSize--;
                    state[vertex] = 2;
                    order[position--] = vertex;
                }
            }
        }
        return order;
    }

    static Map<String, Object> topo(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);
        List<List<Integer>> graph = outgoingEdges(n, edges);
        int[] order = topologicalOrder(n, edges, graph);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("acyclic", order != null);
        result.put("order", order == null ? new int[0] : order);
        return result;
    }

    static Map<String, Object> dag(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int source = Input.source(input);
        int[][] edges = Input.edges(input);
        List<List<Integer>> graph = outgoingEdges(n, edges);
        int[] order = topologicalOrder(n, edges, graph);

        Map<String, Object> result = new LinkedHashMap<>();
        if (order == null) {
            result.put("acyclic", false);
            result.put("distance", new Long[0]);
            result.put("parent_edge", new int[0]);
            return result;
        }

        Long[] distance = new Long[n];
        int[] parentEdge = new int[n];
        Arrays.fill(parentEdge, -1);
        distance[source] = 0L;

        for (int vertex : order) {
            if (distance[vertex] == null) {
                continue;
            }

            for (int edgeId : graph.get(vertex)) {
                int to = edges[edgeId][1];
                long candidate = distance[vertex] + edges[edgeId][2];
                if (distance[to] == null || candidate < distance[to]) {
                    distance[to] = candidate;
                    parentEdge[to] = edgeId;
                }
            }
        }

        result.put("acyclic", true);
        result.put("distance", distance);
        result.put("parent_edge", parentEdge);
        return result;
    }

    static List<Integer> reconstructPath(int source, int target, int[][] edges,
                                         int[] parentEdge) {
        List<Integer> path = new ArrayList<>();
        int vertex = target;

        while (vertex != source) {
            int edgeId = parentEdge[vertex];
            if (edgeId == -1) {
                return new ArrayList<>();
            }
            path.add(vertex);
            vertex = edges[edgeId][0];
        }

        path.add(source);
        Collections.reverse(path);
        return path;
    }
}
