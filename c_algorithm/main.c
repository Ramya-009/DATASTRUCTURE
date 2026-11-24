#include <stdio.h>
#include <stdlib.h>
#include "water_algorithm.h"

int main() {
    printf("===============================================================\n");
    printf("     INTELLIGENT WATER DISTRIBUTION SYSTEM - C CORE ENGINE     \n");
    printf("===============================================================\n\n");

    /* 1. DEMO: LINKED LIST & REQUESTS SETUP */
    printf("[1] Initializing Request Linked List & Priority Queue...\n");
    RequestLinkedList *list = list_create();

    WaterRequest r1 = {101, 1, 1, PRIORITY_HOUSEHOLD, 500.0, 0.0, "Household daily", 0};
    WaterRequest r2 = {102, 2, 1, PRIORITY_HOSPITAL, 3000.0, 0.0, "General Hospital Emergency", 0};
    WaterRequest r3 = {103, 3, 2, PRIORITY_EMERGENCY, 1500.0, 0.0, "Fire Department Emergency", 0};
    WaterRequest r4 = {104, 4, 3, PRIORITY_COMMERCIAL, 2000.0, 0.0, "Textile Mill", 0};
    WaterRequest r5 = {105, 5, 2, PRIORITY_ESSENTIAL, 1200.0, 0.0, "Community Sanitation Centre", 0};
    WaterRequest r6 = {106, 6, 1, PRIORITY_LOW, 800.0, 0.0, "Public Garden Watering", 0};

    list_append(list, r1);
    list_append(list, r2);
    list_append(list, r3);
    list_append(list, r4);
    list_append(list, r5);
    list_append(list, r6);

    printf("    Loaded %d requests into linked list.\n\n", list->count);

    WaterRequest req_array[10];
    int count = list_to_array(list, req_array, 10);

    /* 2. DEMO: PIPELINE NETWORK GRAPH */
    printf("[2] Constructing Water Pipeline Network Graph...\n");
    WaterNetworkGraph *graph = graph_create(5);
    graph_add_node(graph, 0, "Central Main Tank (Poonamallee)", 1, 45.0);
    graph_add_node(graph, 1, "Junction Alpha (Sector 1)", 3, 30.0);
    graph_add_node(graph, 2, "Junction Beta (Sector 2)", 3, 25.0);
    graph_add_node(graph, 3, "General Hospital Line", 4, 28.0);
    graph_add_node(graph, 4, "Commercial Zone Line", 4, 22.0);

    graph_add_pipeline(graph, 0, 1, 10000.0, 3.5);
    graph_add_pipeline(graph, 0, 2, 8000.0, 4.2);
    graph_add_pipeline(graph, 1, 3, 5000.0, 1.2);
    graph_add_pipeline(graph, 2, 4, 4000.0, 2.8);

    double est_loss = graph_calculate_pipeline_loss(graph, 0, 1, 5000.0);
    printf("    Graph created. Pipeline 0->1 conveyance loss estimation: %.1f L\n\n", est_loss);

    /* 3. DEMO: ALLOCATION UNDER WATER SCARCITY */
    double available_water = 5500.0; /* Demand is 500+3000+1500+2000+1200+800 = 9000 L */
    printf("[3] Running Priority Queue Allocation Engine...\n");
    printf("    Total Available Water: %.1f L\n", available_water);

    AllocationResult results[10];
    AllocationSummary summary;

    int processed = run_water_allocation(available_water, req_array, count, results, &summary);

    printf("\n    --- ALLOCATION RESULTS (Processed by C Priority Queue) ---\n");
    printf("    %-6s | %-10s | %-10s | %-11s | %-6s\n", "ReqID", "Priority", "Demanded", "Allocated", "Status");
    printf("    ----------------------------------------------------------\n");

    const char* prio_names[] = {"", "Emergency", "Hospital", "Essential", "Household", "Commercial", "Low"};
    for (int i = 0; i < processed; i++) {
        int p = results[i].priority;
        const char *p_name = (p >= 1 && p <= 6) ? prio_names[p] : "Unknown";
        const char *st = (results[i].status == 1) ? "ALLOCATED" : "REJECTED";
        printf("    #%-5d | %-10s | %8.1f L | %9.1f L | %s\n",
               results[i].request_id, p_name,
               results[i].requested_quantity,
               results[i].allocated_quantity,
               st);
    }

    printf("\n    --- SUMMARY ---\n");
    printf("    Demanded Water   : %.1f L\n", summary.total_demanded_water);
    printf("    Allocated Water  : %.1f L\n", summary.total_allocated_water);
    printf("    Remaining Water  : %.1f L\n", summary.remaining_water);
    printf("    Approved Requests: %d | Partial: %d | Rejected: %d\n\n",
           summary.approved_requests, summary.partial_requests, summary.rejected_requests);

    /* 4. DEMO: ANOMALY-BASED LEAK DETECTION */
    printf("[4] Testing Anomaly-Based Leakage Detection...\n");
    double tank_out = 10000.0;
    double area_in = 7800.0; /* 2200L missing = 22% loss */
    double normal_threshold = 8.0;
    double leak_vol = 0.0, loss_pct = 0.0;
    int is_leak = 0;

    int severity = detect_leakage_anomaly(tank_out, area_in, normal_threshold, &leak_vol, &loss_pct, &is_leak);
    printf("    Tank Output: %.1f L | Area Received: %.1f L\n", tank_out, area_in);
    printf("    Loss: %.1f L (%.2f%%) | Threshold: %.1f%%\n", leak_vol, loss_pct, normal_threshold);
    if (is_leak) {
        printf("    >>> ALERT: Leakage Anomaly Detected! Severity Level: %d (1:Moderate, 2:High, 3:Critical) <<<\n\n", severity);
    } else {
        printf("    Status: Normal pipeline flow.\n\n");
    }

    /* 5. DEMO: DEMAND PREDICTION */
    printf("[5] Testing Demand Prediction (Weighted Moving Average)...\n");
    double history_7_days[] = {9800.0, 10200.0, 10500.0, 11000.0, 10800.0, 11500.0, 12000.0};
    double predicted = predict_next_day_demand(history_7_days, 7);
    printf("    Historical 7-Day Usage: 9.8k -> 12k L\n");
    printf("    Predicted Next-Day Demand: %.1f L\n\n", predicted);

    /* Clean up */
    list_free(list);
    graph_free(graph);

    printf("===============================================================\n");
    printf("     C ENGINE EXECUTION COMPLETED SUCCESSFULLY                 \n");
    printf("===============================================================\n");
    return 0;
}
