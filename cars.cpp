// Program to find Dijkstra's shortest path using 
// priority_queue in STL 
#include<bits/stdc++.h> 
#include <sstream>
#include <string>
#include <random>

using namespace std; 
# define INF 0x3f3f3f3f

const int MAX_DEGREE = 100;
  
typedef pair<int, int> iPair; 
  
struct Edge {
public:
    int n1, n2;

    int count;

    double time() { return length * (1.0 + count * 0.01 / length); }
    int lanes;
    double length;
    Edge(string line) {
        count = 0;
        sscanf(line.c_str(), "%d %d %lf %d", &n1, &n2, &length, &lanes);
    }
};

struct Driver {
    int start, end;
};

// This class represents a directed graph using 
// adjacency list representation 
class Graph 
{ 
    int V;    // No. of vertices 
    vector< vector<Edge> > edges;
    vector<Driver> drivers;
public: 
    Graph(const string& filename);  // Constructor 
  
    // function to add an edge to graph 
    void addEdge(const Edge& e);
  
    // prints shortest path from s 
    double shortestPath(int src, int dest, vector<Edge*>& path);
    double energy();
}; 
  
// Allocates memory for adjacency list 
Graph::Graph(const string& filename)
{
    ifstream infile(filename);
    string line;

    getline(infile, line);

    istringstream iss(line);
    iss >> V;

    for (int i = 0; i < V; i++) {
        vector<Edge> v;
        v.reserve(MAX_DEGREE);
        edges.push_back(v);
    }

    while (getline(infile, line))
    {
        addEdge(Edge(line));
    }
}
  
void Graph::addEdge(const Edge& e) 
{
    edges[e.n1].push_back(e);
}


double Graph::energy() {

    double e = 0;

    for (Driver d : drivers) {

        vector<Edge*> p;

        e += shortestPath(d.start, d.end, p);
    }

    return e;
}
  
// Prints shortest paths from src to all other vertices 
double Graph::shortestPath(int src, int dest, vector<Edge*>& path)
{ 
    // Create a priority queue to store vertices that 
    // are being preprocessed. This is weird syntax in C++. 
    // Refer below link for details of this syntax 
    // https://www.geeksforgeeks.org/implement-min-heap-using-stl/ 
    priority_queue< double, vector <iPair> , greater<iPair> > pq; 
  
    const int V = edges.size();

    // Create a vector for distances and initialize all 
    // distances as infinite (INF) 
    vector<double> dist(V, INF);
    vector<int> backward(V, -1);
    vector<Edge*> backward_edges(V, nullptr);
  
    // Insert source itself in priority queue and initialize 
    // its distance as 0. 
    pq.push(make_pair(0, src));
    dist[src] = 0; 
  
    /* Looping till priority queue becomes empty (or all 
      distances are not finalized) */
    while (!pq.empty()) 
    {
        // The first vertex in pair is the minimum distance 
        // vertex, extract it from priority queue. 
        // vertex label is stored in second of pair (it 
        // has to be done this way to keep the vertices 
        // sorted distance (distance must be first item 
        // in pair)
        int u = pq.top().second; 
        pq.pop();

        if (u == dest) {
            int i = dest;

            double cost = 0;

            while (i != src) {
                if (backward_edges[i] != nullptr) {
                    path.push_back(backward_edges[i]);
                    cost += backward_edges[i]->time();
                    i = backward[i];
                }
            }
            return cost;
        }
  
        // 'i' is used to get all adjacent vertices of a vertex 
        for (auto& edge : edges[u])
        { 
            //  If there is shorted path to v through u. 
            if (dist[edge.n1] > dist[edge.n2] + edge.time()) 
            {
                // Updating distance of v
                dist[edge.n2] = dist[edge.n1] + edge.time();
                backward[edge.n2] = edge.n1;
                backward_edges[edge.n2] = &edge;
                pq.push(make_pair(dist[edge.n2], edge.n2)); 
            }
        }
    }

    return numeric_limits<double>::infinity();
} 
  
// Driver program to test methods of graph class 
int main() 
{
    Graph g("graph.txt");

    const int EQUILIBRIUM_ITERATIONS = 100;
    const int NUM_DRIVERS = 100;

    vector<int> srcs;
    vector<int> dests;
    std::default_random_engine generator;
    std::uniform_int_distribution<int> distribution(0,NUM_DRIVERS-1);
    vector< vector<Edge*> > paths;

    for (int i = 0; i < NUM_DRIVERS;i++) {
        srcs.push_back(distribution(generator));
        dests.push_back(distribution(generator));
        paths.push_back(vector<Edge*>());
    }

    for (int i = 0; i < EQUILIBRIUM_ITERATIONS; i++) {
        for (int j = 0; j < NUM_DRIVERS; j++) {
            vector<Edge*> shortest;
            g.shortestPath(srcs[j], dests[j], shortest);
            for (Edge* e : paths[j]) {
                if (e->count > 0) {
                    e->count--;
                }
            }
            for (Edge* e : shortest) {
                e->count++;
            }
        }
        cout << g.energy() << endl;
    }

    return 0; 
} 