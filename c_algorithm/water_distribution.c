#include "water_algorithm.h"

/* =========================================================================
   CORE INTELLIGENCE: Priority-Based Water Allocation
   ========================================================================= */
ALGO_EXPORT int run_water_allocation(
    double available_water,
    const WaterRequest *requests,
    int request_count,
    AllocationResult *results,
    AllocationSummary *summary
) {
    if (!requests || request_count <= 0 || !results) {
        return -1;
    }

    /* Calculate total demanded water */
    double total_demand = 0.0;
    for (int i = 0; i < request_count; i++) {
        total_demand += requests[i].requested_quantity;
    }

    /* Initialize summary */
    if (summary) {
        summary->total_available_water = available_water;
        summary->total_demanded_water = total_demand;
        summary->total_allocated_water = 0.0;
        summary->remaining_water = available_water;
        summary->total_requests = request_count;
        summary->approved_requests = 0;
        summary->partial_requests = 0;
        summary->rejected_requests = 0;
    }

    /* Step 1: Push all incoming requests into Priority Queue (Min-Heap by priority) */
    PriorityQueue *pq = pq_create(request_count + 10);
    for (int i = 0; i < request_count; i++) {
        pq_push(pq, requests[i]);
    }

    double water_remaining = available_water;
    int processed_count = 0;

    /* Step 2: Pop requests in priority order and allocate according to rules */
    while (!pq_is_empty(pq) && processed_count < request_count) {
        WaterRequest req;
        pq_pop(pq, &req);

        AllocationResult res;
        res.request_id = req.request_id;
        res.user_id = req.user_id;
        res.area_id = req.area_id;
        res.priority = req.priority;
        res.requested_quantity = req.requested_quantity;
        res.allocated_quantity = 0.0;
        res.satisfaction_rate = 0.0;
        res.status = 2; /* Default REJECTED */

        if (water_remaining <= 0.0) {
            /* No water left */
            res.allocated_quantity = 0.0;
            res.satisfaction_rate = 0.0;
            res.status = 2; /* REJECTED */
            if (summary) summary->rejected_requests++;
        } else if (available_water >= total_demand) {
            /* Abundant scenario: 100% full allocation */
            res.allocated_quantity = req.requested_quantity;
            res.satisfaction_rate = 100.0;
            res.status = 1; /* ALLOCATED */
            water_remaining -= req.requested_quantity;
            if (summary) summary->approved_requests++;
        } else {
            /* Scarcity scenario: Priority-driven intelligent rationing */
            double alloc = 0.0;

            if (req.priority == PRIORITY_EMERGENCY || req.priority == PRIORITY_HOSPITAL) {
                /* Tier 1: Emergency & Hospital get 100% full allocation if water exists */
                if (water_remaining >= req.requested_quantity) {
                    alloc = req.requested_quantity;
                } else {
                    alloc = water_remaining;
                }
            } else if (req.priority == PRIORITY_ESSENTIAL) {
                /* Tier 2: Essential public services get up to 90% */
                double ideal = req.requested_quantity * 0.90;
                alloc = (water_remaining >= ideal) ? ideal : water_remaining;
            } else if (req.priority == PRIORITY_HOUSEHOLD) {
                /* Tier 3: Domestic households get up to 75% or remaining fair share */
                double ideal = req.requested_quantity * 0.75;
                alloc = (water_remaining >= ideal) ? ideal : water_remaining;
            } else if (req.priority == PRIORITY_COMMERCIAL) {
                /* Tier 4: Commercial gets up to 50% under scarcity */
                double ideal = req.requested_quantity * 0.50;
                alloc = (water_remaining >= ideal) ? ideal : water_remaining;
            } else {
                /* Tier 5: Low priority gets residual 30% if water is above buffer */
                double ideal = req.requested_quantity * 0.30;
                alloc = (water_remaining >= ideal) ? ideal : water_remaining;
            }

            if (alloc > 0.0) {
                res.allocated_quantity = alloc;
                res.satisfaction_rate = (alloc / req.requested_quantity) * 100.0;
                res.status = 1; /* ALLOCATED */
                water_remaining -= alloc;

                if (summary) {
                    if (res.satisfaction_rate >= 99.9) {
                        summary->approved_requests++;
                    } else {
                        summary->partial_requests++;
                    }
                }
            } else {
                res.allocated_quantity = 0.0;
                res.satisfaction_rate = 0.0;
                res.status = 2; /* REJECTED */
                if (summary) summary->rejected_requests++;
            }
        }

        results[processed_count++] = res;
    }

    pq_free(pq);

    if (summary) {
        summary->total_allocated_water = available_water - water_remaining;
        summary->remaining_water = (water_remaining > 0.0) ? water_remaining : 0.0;
    }

    return processed_count;
}

/* =========================================================================
   CORE INTELLIGENCE: Anomaly-Based Leakage Detection
   ========================================================================= */
ALGO_EXPORT int detect_leakage_anomaly(
    double tank_output_litres,
    double area_received_litres,
    double normal_loss_percentage_threshold,
    double *leak_volume_litres,
    double *loss_percentage,
    int *is_leak_detected
) {
    if (tank_output_litres <= 0.0) {
        if (leak_volume_litres) *leak_volume_litres = 0.0;
        if (loss_percentage) *loss_percentage = 0.0;
        if (is_leak_detected) *is_leak_detected = 0;
        return 0;
    }

    double loss = tank_output_litres - area_received_litres;
    if (loss < 0.0) loss = 0.0; /* Measurement safety */

    double loss_pct = (loss / tank_output_litres) * 100.0;

    if (leak_volume_litres) *leak_volume_litres = loss;
    if (loss_percentage) *loss_percentage = loss_pct;

    /* If loss exceeds normal threshold (e.g. 8-10%), flag as leak */
    if (loss_pct > normal_loss_percentage_threshold) {
        if (is_leak_detected) *is_leak_detected = 1;
        /* Severity rating: 1 = Minor, 2 = High, 3 = Critical Emergency */
        if (loss_pct >= 25.0) return 3; /* Critical */
        if (loss_pct >= 15.0) return 2; /* High */
        return 1; /* Moderate */
    } else {
        if (is_leak_detected) *is_leak_detected = 0;
        return 0; /* Normal */
    }
}

/* =========================================================================
   CORE INTELLIGENCE: Demand Prediction (Weighted Moving Average)
   ========================================================================= */
ALGO_EXPORT double predict_next_day_demand(
    const double *historical_usage,
    int days_count
) {
    if (!historical_usage || days_count <= 0) return 0.0;
    if (days_count == 1) return historical_usage[0];

    /* Weighted moving average giving higher weight to recent days */
    double weighted_sum = 0.0;
    double weight_total = 0.0;

    for (int i = 0; i < days_count; i++) {
        double weight = (double)(i + 1); /* Day 1 has wt 1, Day 7 has wt 7 */
        weighted_sum += historical_usage[i] * weight;
        weight_total += weight;
    }

    return (weighted_sum / weight_total);
}
