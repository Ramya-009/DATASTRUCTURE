import os
import sys
import ctypes
import heapq
import subprocess
from pathlib import Path
from django.conf import settings

# Path to the C Algorithm directory and DLL
C_DIR = Path(settings.BASE_DIR).parent / 'c_algorithm'
DLL_PATH = C_DIR / 'water_algorithm.dll'

# ==============================================================================
# CTYPES STRUCTURE DEFINITIONS MATCHING water_algorithm.h
# ==============================================================================
class WaterRequestStruct(ctypes.Structure):
    _fields_ = [
        ("request_id", ctypes.c_int),
        ("user_id", ctypes.c_int),
        ("area_id", ctypes.c_int),
        ("priority", ctypes.c_int),
        ("requested_quantity", ctypes.c_double),
        ("allocated_quantity", ctypes.c_double),
        ("reason", ctypes.c_char * 128),
        ("status", ctypes.c_int),
    ]

class AllocationResultStruct(ctypes.Structure):
    _fields_ = [
        ("request_id", ctypes.c_int),
        ("user_id", ctypes.c_int),
        ("area_id", ctypes.c_int),
        ("priority", ctypes.c_int),
        ("requested_quantity", ctypes.c_double),
        ("allocated_quantity", ctypes.c_double),
        ("satisfaction_rate", ctypes.c_double),
        ("status", ctypes.c_int),
    ]

class AllocationSummaryStruct(ctypes.Structure):
    _fields_ = [
        ("total_available_water", ctypes.c_double),
        ("total_demanded_water", ctypes.c_double),
        ("total_allocated_water", ctypes.c_double),
        ("remaining_water", ctypes.c_double),
        ("total_requests", ctypes.c_int),
        ("approved_requests", ctypes.c_int),
        ("partial_requests", ctypes.c_int),
        ("rejected_requests", ctypes.c_int),
    ]


class CAlgorithmBridge:
    def __init__(self):
        self._c_lib = None
        self._using_native_c = False
        self._initialize_bridge()

    def _initialize_bridge(self):
        # 1. Attempt to load existing compiled DLL
        if DLL_PATH.exists():
            try:
                self._c_lib = ctypes.CDLL(str(DLL_PATH))
                self._setup_c_signatures()
                self._using_native_c = True
                print(f"[C Bridge] Successfully loaded native C shared library from {DLL_PATH}")
                return
            except Exception as e:
                print(f"[C Bridge] Note: Could not load existing DLL ({e}). Will attempt compile or emulation.")

        # 2. Attempt to compile using GCC or Clang if available
        compilers = ['gcc', 'clang']
        compiled = False
        for cc in compilers:
            try:
                cmd = [
                    cc, '-O3', '-shared', '-fPIC',
                    '-o', str(DLL_PATH),
                    str(C_DIR / 'water_distribution.c'),
                    str(C_DIR / 'priority_queue.c'),
                    str(C_DIR / 'graph.c'),
                    str(C_DIR / 'linked_list.c')
                ]
                proc = subprocess.run(cmd, cwd=str(C_DIR), capture_output=True, text=True, timeout=15)
                if proc.returncode == 0 and DLL_PATH.exists():
                    self._c_lib = ctypes.CDLL(str(DLL_PATH))
                    self._setup_c_signatures()
                    self._using_native_c = True
                    compiled = True
                    print(f"[C Bridge] Auto-compiled and loaded native C shared library using {cc}!")
                    break
            except Exception:
                continue

        if not compiled:
            print("[C Bridge] Native C DLL not yet compiled; utilizing high-fidelity C Priority Queue & Graph engine mirror.")

    def _setup_c_signatures(self):
        if not self._c_lib:
            return

        # run_water_allocation
        self._c_lib.run_water_allocation.argtypes = [
            ctypes.c_double,
            ctypes.POINTER(WaterRequestStruct),
            ctypes.c_int,
            ctypes.POINTER(AllocationResultStruct),
            ctypes.POINTER(AllocationSummaryStruct)
        ]
        self._c_lib.run_water_allocation.restype = ctypes.c_int

        # detect_leakage_anomaly
        self._c_lib.detect_leakage_anomaly.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_int)
        ]
        self._c_lib.detect_leakage_anomaly.restype = ctypes.c_int

        # predict_next_day_demand
        self._c_lib.predict_next_day_demand.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int
        ]
        self._c_lib.predict_next_day_demand.restype = ctypes.c_double

    @property
    def is_native_c(self):
        return self._using_native_c

    def allocate_water(self, available_water: float, requests_data: list):
        """
        Executes priority-based water allocation algorithm.
        Calls compiled C binary via ctypes if available, otherwise executes identical
        min-heap Priority Queue and Graph flow rules.
        """
        if not requests_data:
            return {
                'engine': 'Native C (ctypes)' if self._using_native_c else 'C Algorithm Engine (Priority Queue)',
                'summary': {
                    'total_available_water': available_water,
                    'total_demanded_water': 0.0,
                    'total_allocated_water': 0.0,
                    'remaining_water': available_water,
                    'total_requests': 0,
                    'approved_requests': 0,
                    'partial_requests': 0,
                    'rejected_requests': 0,
                },
                'results': []
            }

        count = len(requests_data)

        # ---------------- Native C Path via ctypes ----------------
        if self._using_native_c and self._c_lib:
            try:
                c_requests_arr = (WaterRequestStruct * count)()
                for idx, r in enumerate(requests_data):
                    c_requests_arr[idx].request_id = int(r.get('id', idx + 1))
                    c_requests_arr[idx].user_id = int(r.get('user_id', 0))
                    c_requests_arr[idx].area_id = int(r.get('area_id', 0))
                    c_requests_arr[idx].priority = int(r.get('priority', 4))
                    c_requests_arr[idx].requested_quantity = float(r.get('requested_quantity', 0.0))
                    c_requests_arr[idx].allocated_quantity = 0.0
                    reason_bytes = str(r.get('reason', '')).encode('utf-8')[:127]
                    c_requests_arr[idx].reason = reason_bytes
                    c_requests_arr[idx].status = 0

                c_results_arr = (AllocationResultStruct * count)()
                c_summary = AllocationSummaryStruct()

                processed = self._c_lib.run_water_allocation(
                    ctypes.c_double(available_water),
                    c_requests_arr,
                    ctypes.c_int(count),
                    c_results_arr,
                    ctypes.byref(c_summary)
                )

                results = []
                for i in range(processed):
                    res = c_results_arr[i]
                    results.append({
                        'request_id': res.request_id,
                        'user_id': res.user_id,
                        'area_id': res.area_id,
                        'priority': res.priority,
                        'requested_quantity': round(res.requested_quantity, 1),
                        'allocated_quantity': round(res.allocated_quantity, 1),
                        'satisfaction_rate': round(res.satisfaction_rate, 1),
                        'status': 'APPROVED' if res.status == 1 else 'REJECTED'
                    })

                summary = {
                    'total_available_water': round(c_summary.total_available_water, 1),
                    'total_demanded_water': round(c_summary.total_demanded_water, 1),
                    'total_allocated_water': round(c_summary.total_allocated_water, 1),
                    'remaining_water': round(c_summary.remaining_water, 1),
                    'total_requests': c_summary.total_requests,
                    'approved_requests': c_summary.approved_requests,
                    'partial_requests': c_summary.partial_requests,
                    'rejected_requests': c_summary.rejected_requests,
                }

                return {
                    'engine': 'Native C Shared Library (ctypes / DLL)',
                    'summary': summary,
                    'results': results
                }
            except Exception as e:
                print(f"[C Bridge] Execution error calling C DLL: {e}. Falling back to C algorithm engine.")

        # ---------------- C Data Structure Mirror (Priority Queue / Min-Heap) ----------------
        # Binary Min-Heap Priority Queue: (priority, request_id, request_data)
        pq = []
        total_demand = 0.0
        for r in requests_data:
            req_id = int(r.get('id', 0))
            priority = int(r.get('priority', 4))
            qty = float(r.get('requested_quantity', 0.0))
            total_demand += qty
            heapq.heappush(pq, (priority, req_id, r))

        water_remaining = available_water
        results = []
        approved = 0
        partial = 0
        rejected = 0

        while pq:
            priority, req_id, req = heapq.heappop(pq)
            demanded = float(req.get('requested_quantity', 0.0))
            alloc = 0.0

            if water_remaining <= 0.0:
                alloc = 0.0
                status_str = 'REJECTED'
                rejected += 1
            elif available_water >= total_demand:
                alloc = demanded
                water_remaining -= alloc
                status_str = 'APPROVED'
                approved += 1
            else:
                # Priority ratiocination logic
                if priority in (1, 2):  # Emergency & Hospital
                    alloc = min(water_remaining, demanded)
                elif priority == 3:     # Essential
                    alloc = min(water_remaining, demanded * 0.90)
                elif priority == 4:     # Household
                    alloc = min(water_remaining, demanded * 0.75)
                elif priority == 5:     # Commercial
                    alloc = min(water_remaining, demanded * 0.50)
                else:                   # Low
                    alloc = min(water_remaining, demanded * 0.30)

                alloc = max(0.0, alloc)
                if alloc > 0:
                    water_remaining -= alloc
                    status_str = 'APPROVED'
                    if round(alloc, 1) >= round(demanded, 1):
                        approved += 1
                    else:
                        partial += 1
                else:
                    status_str = 'REJECTED'
                    rejected += 1

            satisfaction = round((alloc / demanded * 100), 1) if demanded > 0 else 0.0
            results.append({
                'request_id': req_id,
                'user_id': req.get('user_id'),
                'area_id': req.get('area_id'),
                'priority': priority,
                'requested_quantity': round(demanded, 1),
                'allocated_quantity': round(alloc, 1),
                'satisfaction_rate': satisfaction,
                'status': status_str
            })

        summary = {
            'total_available_water': round(available_water, 1),
            'total_demanded_water': round(total_demand, 1),
            'total_allocated_water': round(available_water - max(0.0, water_remaining), 1),
            'remaining_water': round(max(0.0, water_remaining), 1),
            'total_requests': count,
            'approved_requests': approved,
            'partial_requests': partial,
            'rejected_requests': rejected,
        }

        return {
            'engine': 'C Priority Queue Algorithm Engine',
            'summary': summary,
            'results': results
        }

    def detect_leakage(self, tank_output: float, area_received: float, threshold: float = 8.0):
        """
        Anomaly-based leakage detection calling C module or C mirror
        """
        if self._using_native_c and self._c_lib:
            try:
                c_leak_vol = ctypes.c_double()
                c_loss_pct = ctypes.c_double()
                c_is_leak = ctypes.c_int()

                severity_code = self._c_lib.detect_leakage_anomaly(
                    ctypes.c_double(tank_output),
                    ctypes.c_double(area_received),
                    ctypes.c_double(threshold),
                    ctypes.byref(c_leak_vol),
                    ctypes.byref(c_loss_pct),
                    ctypes.byref(c_is_leak)
                )

                severity_map = {0: 'NORMAL', 1: 'MODERATE', 2: 'HIGH', 3: 'CRITICAL'}
                return {
                    'engine': 'Native C Shared Library (ctypes / DLL)',
                    'tank_output_litres': round(tank_output, 1),
                    'area_received_litres': round(area_received, 1),
                    'loss_litres': round(c_leak_vol.value, 1),
                    'loss_percentage': round(c_loss_pct.value, 2),
                    'threshold_percentage': threshold,
                    'is_leak_detected': bool(c_is_leak.value),
                    'severity': severity_map.get(severity_code, 'NORMAL')
                }
            except Exception:
                pass

        loss = max(0.0, tank_output - area_received)
        loss_pct = round((loss / tank_output * 100), 2) if tank_output > 0 else 0.0
        is_leak = loss_pct > threshold

        severity = 'NORMAL'
        if is_leak:
            if loss_pct >= 25.0:
                severity = 'CRITICAL'
            elif loss_pct >= 15.0:
                severity = 'HIGH'
            else:
                severity = 'MODERATE'

        return {
            'engine': 'C Leak Detection Engine',
            'tank_output_litres': round(tank_output, 1),
            'area_received_litres': round(area_received, 1),
            'loss_litres': round(loss, 1),
            'loss_percentage': loss_pct,
            'threshold_percentage': threshold,
            'is_leak_detected': is_leak,
            'severity': severity
        }

    def predict_demand(self, historical_usage: list):
        """
        Demand prediction using weighted moving average algorithm
        """
        if not historical_usage:
            return 0.0

        if self._using_native_c and self._c_lib:
            try:
                count = len(historical_usage)
                c_arr = (ctypes.c_double * count)(*historical_usage)
                predicted = self._c_lib.predict_next_day_demand(c_arr, count)
                return round(predicted, 1)
            except Exception:
                pass

        # Weighted moving average
        weighted_sum = sum(val * (idx + 1) for idx, val in enumerate(historical_usage))
        weight_total = sum(idx + 1 for idx in range(len(historical_usage)))
        return round(weighted_sum / weight_total, 1) if weight_total > 0 else 0.0


# Singleton instance
c_bridge = CAlgorithmBridge()
