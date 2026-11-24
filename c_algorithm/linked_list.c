#include "water_algorithm.h"

RequestLinkedList* list_create(void) {
    RequestLinkedList *list = (RequestLinkedList*)malloc(sizeof(RequestLinkedList));
    if (!list) return NULL;
    list->head = NULL;
    list->tail = NULL;
    list->count = 0;
    return list;
}

void list_append(RequestLinkedList *list, WaterRequest req) {
    if (!list) return;
    RequestNode *node = (RequestNode*)malloc(sizeof(RequestNode));
    if (!node) return;
    node->data = req;
    node->next = NULL;

    if (!list->head) {
        list->head = node;
        list->tail = node;
    } else {
        list->tail->next = node;
        list->tail = node;
    }
    list->count++;
}

int list_to_array(RequestLinkedList *list, WaterRequest *arr, int max_size) {
    if (!list || !arr || max_size <= 0) return 0;
    int index = 0;
    RequestNode *curr = list->head;
    while (curr && index < max_size) {
        arr[index++] = curr->data;
        curr = curr->next;
    }
    return index;
}

void list_free(RequestLinkedList *list) {
    if (!list) return;
    RequestNode *curr = list->head;
    while (curr) {
        RequestNode *next = curr->next;
        free(curr);
        curr = next;
    }
    free(list);
}
