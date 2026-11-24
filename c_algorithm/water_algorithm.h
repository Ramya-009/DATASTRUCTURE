#ifndef WATER_ALGORITHM_H
#define WATER_ALGORITHM_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#ifdef _WIN32
  #define ALGO_EXPORT __declspec(dllexport)
#else
  #define ALGO_EXPORT
#endif

/* =========================================================================
   PRIORITY DEFINITIONS
   1 = Emergency (Highest)
   2 = Hospital / Medical
   3 = Essential Public Services
   4 = Household / Domestic
   5 = Commercial / Industrial
   6 = Low Priority (Lowest)
   ========================================================================= */
#define PRIORITY_EMERGENCY    1
#define PRIORITY_HOSPITAL     2
#define PRIORITY_ESSENTIAL    3
#define PRIORITY_HOUSEHOLD    4
#define PRIORITY_COMMERCIAL   5
#define PRIORITY_LOW          6

#define MAX_AREAS             50
#define MAX_PIPELINES         200
#define MAX_NAME_LEN          64

/* Data structure representing a single water distribution request */
typedef struct {
    int request_id;
    int user_id;
    int area_id;
    int priority;               /* 1 (highest) to 6 (lowest) */
    double requested_quantity;   /* in Litres */
    double allocated_quantity;   /* calculated in Litres */
    char reason[128];
    int status;                 /* 0: PENDING, 1: ALLOCATED, 2: REJECTED, 3: COMPLETED */
} WaterRequest;

/* Structure for allocation output per request */
typedef struct {
    int request_id;
    int user_id;
    int area_id;
    int priority;
    double requested_quantity;
    double allocated_quantity;
    double satisfaction_rate;   /* allocated / requested * 100 */
    int status;                 /* 1: ALLOCATED, 2: REJECTED */
} AllocationResult;

/* Summary result returned to Django Backend */
typedef struct {
    double total_available_water;
    double total_demanded_water;
    double total_allocated_water;
    double remaining_water;
    int total_requests;
    int approved_requests;
    int partial_requests;
    int rejected_requests;
} AllocationSummary;

/* =========================================================================
   1. PRIORITY QUEUE (Min-Heap based on priority number; 1 is top priority)
   ========================================================================= */
typedef struct {
    WaterRequest *heap;
    int capacity;
    int size;
} PriorityQueue;

PriorityQueue* pq_create(int capacity);
void pq_push(PriorityQueue *pq, WaterRequest req);
bool pq_pop(PriorityQueue *pq, WaterRequest *out_req);
bool pq_is_empty(PriorityQueue *pq);
void pq_free(PriorityQueue *pq);

/* =========================================================================
   2. LINKED LIST (For dynamic request collection & historical tracking)
   ========================================================================= */
typedef struct RequestNode {
    WaterRequest data;
    struct RequestNode *next;
} RequestNode;

typedef struct {
    RequestNode *head;
    RequestNode *tail;
    int count;
} RequestLinkedList;

RequestLinkedList* list_create(void);
void list_append(RequestLinkedList *list, WaterRequest req);
int list_to_array(RequestLinkedList *list, WaterRequest *arr, int max_size);
void list_free(RequestLinkedList *list);

/* =========================================================================
   3. GRAPH (Pipeline Network Topology)
   Represents: Tanks (Source) -> Junctions / Areas -> Distribution Points
   ========================================================================= */
typedef struct PipelineEdge {
    int to_node;
    double capacity;    /* Pipeline maximum flow capacity in Litres/hour */
    double current_flow;
    double length_km;
    struct PipelineEdge *next;
} PipelineEdge;

typedef struct {
    int node_id;
    char node_name[MAX_NAME_LEN];
    int node_type;      /* 1: Main Tank, 2: Secondary Tank, 3: Area Junction, 4: End Consumer */
    double elevation;
    PipelineEdge *head;
} NetworkNode;

typedef struct {
    int num_nodes;
    NetworkNode nodes[MAX_AREAS];
} WaterNetworkGraph;

WaterNetworkGraph* graph_create(int num_nodes);
void graph_add_node(WaterNetworkGraph *g, int id, const char *name, int type, double elevation);
void graph_add_pipeline(WaterNetworkGraph *g, int from, int to, double capacity, double length);
double graph_calculate_pipeline_loss(WaterNetworkGraph *g, int from, int to, double input_quantity);
void graph_free(WaterNetworkGraph *g);

/* =========================================================================
   4. CORE INTELLIGENCE ALGORITHMS (Exported to Python Django via ctypes)
   ========================================================================= */

#ifdef __cplusplus
extern "C" {
#endif

/* Priority-based water allocation algorithm */
ALGO_EXPORT int run_water_allocation(
    double available_water,
    const WaterRequest *requests,
    int request_count,
    AllocationResult *results,
    AllocationSummary *summary
);

/* Anomaly-based leak detection */
ALGO_EXPORT int detect_leakage_anomaly(
    double tank_output_litres,
    double area_received_litres,
    double normal_loss_percentage_threshold,
    double *leak_volume_litres,
    double *loss_percentage,
    int *is_leak_detected
);

/* Demand prediction moving average algorithm */
ALGO_EXPORT double predict_next_day_demand(
    const double *historical_usage,
    int days_count
);

#ifdef __cplusplus
}
#endif

#endif /* WATER_ALGORITHM_H */
