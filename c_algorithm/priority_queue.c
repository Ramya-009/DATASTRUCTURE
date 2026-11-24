#include "water_algorithm.h"

PriorityQueue* pq_create(int capacity) {
    if (capacity <= 0) capacity = 64;
    PriorityQueue *pq = (PriorityQueue*)malloc(sizeof(PriorityQueue));
    if (!pq) return NULL;
    pq->heap = (WaterRequest*)malloc(sizeof(WaterRequest) * capacity);
    pq->capacity = capacity;
    pq->size = 0;
    return pq;
}

static void swap_requests(WaterRequest *a, WaterRequest *b) {
    WaterRequest temp = *a;
    *a = *b;
    *b = temp;
}

/* Returns true if 'a' has higher priority than 'b' */
static bool has_higher_priority(const WaterRequest *a, const WaterRequest *b) {
    if (a->priority < b->priority) return true;
    if (a->priority > b->priority) return false;
    /* Tie-breaker: earlier request_id gets priority (FIFO) */
    return a->request_id < b->request_id;
}

void pq_push(PriorityQueue *pq, WaterRequest req) {
    if (!pq) return;
    if (pq->size >= pq->capacity) {
        pq->capacity *= 2;
        pq->heap = (WaterRequest*)realloc(pq->heap, sizeof(WaterRequest) * pq->capacity);
    }

    int current = pq->size++;
    pq->heap[current] = req;

    /* Heapify Up */
    while (current > 0) {
        int parent = (current - 1) / 2;
        if (has_higher_priority(&pq->heap[current], &pq->heap[parent])) {
            swap_requests(&pq->heap[current], &pq->heap[parent]);
            current = parent;
        } else {
            break;
        }
    }
}

bool pq_pop(PriorityQueue *pq, WaterRequest *out_req) {
    if (!pq || pq->size == 0) return false;
    if (out_req) *out_req = pq->heap[0];

    pq->size--;
    if (pq->size > 0) {
        pq->heap[0] = pq->heap[pq->size];

        /* Heapify Down */
        int current = 0;
        while (true) {
            int left = 2 * current + 1;
            int right = 2 * current + 2;
            int best = current;

            if (left < pq->size && has_higher_priority(&pq->heap[left], &pq->heap[best])) {
                best = left;
            }
            if (right < pq->size && has_higher_priority(&pq->heap[right], &pq->heap[best])) {
                best = right;
            }

            if (best != current) {
                swap_requests(&pq->heap[current], &pq->heap[best]);
                current = best;
            } else {
                break;
            }
        }
    }
    return true;
}

bool pq_is_empty(PriorityQueue *pq) {
    return (!pq || pq->size == 0);
}

void pq_free(PriorityQueue *pq) {
    if (pq) {
        if (pq->heap) free(pq->heap);
        free(pq);
    }
}
