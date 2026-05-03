#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
    int vertex;
    struct Node *next;
} Node;

/* Function prototypes required by the project */
void degCommand(Node **adjList, int n, int v);
void delCommand(Node **adjList, int u, int v);
void pstCommand(Node **adjList, int n);
void nbhdCommand(Node **adjList, int n, int v);

/* Helper functions */
Node *createNode(int vertex);
void addNeighbor(Node **head, int vertex);
void buildGraphFromFile(FILE *infile, Node **adjList, int *n);
int isValidVertex(int v, int n);
int degreeOfVertex(Node **adjList, int v);
int edgeExists(Node **adjList, int u, int v);
void removeNeighbor(Node **head, int vertex);
int countEdges(Node **adjList, int n);
void writeGraphToFile(FILE *outfile, Node **adjList, int n);
void freeGraph(Node **adjList, int n);

int main(int argc, char *argv[]) {
    FILE *infile, *outfile;
    Node **adjList;
    int n = 0;
    char command[5];

    if (argc != 3) {
        printf("Usage: %s infile outfile\n", argv[0]);
        return 1;
    }

    infile = fopen(argv[1], "r");
    if (infile == NULL) {
        printf("Error opening input file.\n");
        return 1;
    }

    /* Read number of vertices first */
    if (fscanf(infile, "%d", &n) != 1 || n < 0) {
        printf("Error reading graph.\n");
        fclose(infile);
        return 1;
    }

    adjList = (Node **)malloc((n + 1) * sizeof(Node *));
    if (adjList == NULL) {
        printf("Memory allocation failed.\n");
        fclose(infile);
        return 1;
    }

    for (int i = 0; i <= n; i++) {
        adjList[i] = NULL;
    }

    /* Read edges */
    int u, v;
    while (fscanf(infile, "%d,%d", &u, &v) == 2) {
        addNeighbor(&adjList[u], v);
        addNeighbor(&adjList[v], u);
    }

    fclose(infile);

    outfile = fopen(argv[2], "w");
    if (outfile == NULL) {
        printf("Error opening output file.\n");
        freeGraph(adjList, n);
        return 1;
    }

    /* Interactive command loop */
    while (1) {
        printf("Enter command: ");
        scanf("%4s", command);

        if (strcmp(command, "deg") == 0) {
            scanf("%d", &v);
            degCommand(adjList, n, v);
        } else if (strcmp(command, "del") == 0) {
            scanf("%d %d", &u, &v);
            delCommand(adjList, u, v);
        } else if (strcmp(command, "pst") == 0) {
            pstCommand(adjList, n);
        } else if (strcmp(command, "nbhd") == 0) {
            scanf("%d", &v);
            nbhdCommand(adjList, n, v);
        } else if (strcmp(command, "end") == 0) {
            break;
        }
    }

    writeGraphToFile(outfile, adjList, n);

    fclose(outfile);
    freeGraph(adjList, n);

    return 0;
}

Node *createNode(int vertex) {
    Node *newNode = (Node *)malloc(sizeof(Node));
    if (newNode == NULL) {
        printf("Memory allocation failed.\n");
        exit(1);
    }
    newNode->vertex = vertex;
    newNode->next = NULL;
    return newNode;
}

void addNeighbor(Node **head, int vertex) {
    Node *newNode = createNode(vertex);

    if (*head == NULL) {
        *head = newNode;
        return;
    }

    Node *current = *head;
    while (current->next != NULL) {
        current = current->next;
    }
    current->next = newNode;
}

int isValidVertex(int v, int n) {
    return (v >= 1 && v <= n);
}

int degreeOfVertex(Node **adjList, int v) {
    int count = 0;
    Node *current = adjList[v];

    while (current != NULL) {
        count++;
        current = current->next;
    }

    return count;
}

void degCommand(Node **adjList, int n, int v) {
    if (!isValidVertex(v, n)) {
        printf("invalid vertex\n");
        return;
    }

    printf("%d\n", degreeOfVertex(adjList, v));
}

int edgeExists(Node **adjList, int u, int v) {
    Node *current = adjList[u];
    while (current != NULL) {
        if (current->vertex == v) {
            return 1;
        }
        current = current->next;
    }
    return 0;
}

void removeNeighbor(Node **head, int vertex) {
    Node *current = *head;
    Node *prev = NULL;

    while (current != NULL) {
        if (current->vertex == vertex) {
            if (prev == NULL) {
                *head = current->next;
            } else {
                prev->next = current->next;
            }
            free(current);
            return;
        }
        prev = current;
        current = current->next;
    }
}

void delCommand(Node **adjList, int u, int v) {
    removeNeighbor(&adjList[u], v);
    removeNeighbor(&adjList[v], u);
}

int countEdges(Node **adjList, int n) {
    int totalDegrees = 0;

    for (int i = 1; i <= n; i++) {
        totalDegrees += degreeOfVertex(adjList, i);
    }

    return totalDegrees / 2;
}

void pstCommand(Node **adjList, int n) {
    int numVertices = n;
    int numEdges = countEdges(adjList, n);
    int maxDegree = 0;
    int minDegree;
    double avgDegree;

    if (n == 0) {
        printf("Number of vertices: 0\n");
        printf("Number of edges: 0\n");
        printf("Maximum degree: 0\n");
        printf("Minimum degree: 0\n");
        printf("Average degree: 0.00\n");
        return;
    }

    minDegree = degreeOfVertex(adjList, 1);

    for (int i = 1; i <= n; i++) {
        int d = degreeOfVertex(adjList, i);

        if (d > maxDegree) {
            maxDegree = d;
        }
        if (d < minDegree) {
            minDegree = d;
        }
    }

    avgDegree = (2.0 * numEdges) / n;

    printf("Number of vertices: %d\n", numVertices);
    printf("Number of edges: %d\n", numEdges);
    printf("Maximum degree: %d\n", maxDegree);
    printf("Minimum degree: %d\n", minDegree);
    printf("Average degree: %.2f\n", avgDegree);
}

void nbhdCommand(Node **adjList, int n, int v) {
    if (!isValidVertex(v, n)) {
        printf("Invalid vertex\n");
        return;
    }

    Node *current = adjList[v];
    while (current != NULL) {
        printf("%d", current->vertex);
        if (current->next != NULL) {
            printf(" ");
        }
        current = current->next;
    }
    printf("\n");
}

void writeGraphToFile(FILE *outfile, Node **adjList, int n) {
    fprintf(outfile, "%d\n", n);

    for (int i = 1; i <= n; i++) {
        Node *current = adjList[i];
        while (current != NULL) {
            if (i < current->vertex) {
                fprintf(outfile, "%d,%d\n", i, current->vertex);
            }
            current = current->next;
        }
    }
}

void freeGraph(Node **adjList, int n) {
    for (int i = 0; i <= n; i++) {
        Node *current = adjList[i];
        while (current != NULL) {
            Node *temp = current;
            current = current->next;
            free(temp);
        }
    }
    free(adjList);
}