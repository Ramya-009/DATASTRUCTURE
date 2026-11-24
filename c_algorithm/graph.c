#include "water_algorithm.h"

WaterNetworkGraph* graph_create(int num_nodes) {
    if (num_nodes <= 0 || num_nodes > MAX_AREAS) num_nodes = MAX_AREAS;
    WaterNetworkGraph *g = (WaterNetworkGraph*)malloc(sizeof(WaterNetworkGraph));
    if (!g) return NULL;
    g->num_nodes = num_nodes;
    for (int i = 0; i < num_nodes; i++) {
        g->nodes[i].node_id = i;
        g->nodes[i].node_name[0] = '\0';
        g->nodes[i].node_type = 3; /* Area default */
        g->nodes[i].elevation = 0.0;
        g->nodes[i].head = NULL;
    }
    return g;
}

void graph_add_node(WaterNetworkGraph *g, int id, const char *name, int type, double elevation) {
    if (!g || id < 0 || id >= g->num_nodes) return;
    g->nodes[id].node_id = id;
    if (name) {
        strncpy(g->nodes[id].node_name, name, MAX_NAME_LEN - 1);
        g->nodes[id].node_name[MAX_NAME_LEN - 1] = '\0';
    }
    g->nodes[id].node_type = type;
    g->nodes[id].elevation = elevation;
}

void graph_add_pipeline(WaterNetworkGraph *g, int from, int to, double capacity, double length) {
    if (!g || from < 0 || from >= g->num_nodes || to < 0 || to >= g->num_nodes) return;

    PipelineEdge *edge = (PipelineEdge*)malloc(sizeof(PipelineEdge));
    if (!edge) return;
    edge->to_node = to;
    edge->capacity = capacity;
    edge->current_flow = 0.0;
    edge->length_km = length;
    edge->next = g->nodes[from].head;
    g->nodes[from].head = edge;
}

/* Calculates natural friction loss percentage along a pipeline based on distance */
double graph_calculate_pipeline_loss(WaterNetworkGraph *g, int from, int to, double input_quantity) {
    if (!g || from < 0 || from >= g->num_nodes) return 0.0;
    PipelineEdge *curr = g->nodes[from].head;
    while (curr) {
        if (curr->to_node == to) {
            /* Typical friction/evaporation loss coefficient: ~0.5% per km */
            double loss_pct = curr->length_km * 0.005;
            if (loss_pct > 0.08) loss_pct = 0.08; /* Max expected normal conveyance loss 8% */
            return input_quantity * loss_pct;
        }
        curr = curr->next;
    }
    return input_quantity * 0.02; /* Default 2% */
}

void graph_free(WaterNetworkGraph *g) {
    if (!g) return;
    for (int i = 0; i < g->num_nodes; i++) {
        PipelineEdge *curr = g->nodes[i].head;
        while (curr) {
            PipelineEdge *next = curr->next;
            free(curr);
            curr = next;
        }
    }
    free(g);
}
