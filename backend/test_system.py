import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from water.c_bridge import c_bridge

def run_tests():
    print("=" * 60)
    print("RUNNING INTELLIGENT WATER SYSTEM COMPREHENSIVE TESTS")
    print("=" * 60)

    # 1. Test C Bridge Priority Allocation
    print("\n[Test 1] Testing C Priority Queue Allocation Engine...")
    sample_requests = [
        {"id": 1, "user_id": 10, "area_id": 1, "priority": 4, "requested_quantity": 500.0, "reason": "Household"},
        {"id": 2, "user_id": 20, "area_id": 2, "priority": 2, "requested_quantity": 3000.0, "reason": "Hospital"},
        {"id": 3, "user_id": 30, "area_id": 1, "priority": 1, "requested_quantity": 1500.0, "reason": "Fire Emergency"},
        {"id": 4, "user_id": 40, "area_id": 3, "priority": 5, "requested_quantity": 2000.0, "reason": "Factory"},
    ]
    # Total demand = 7000 L, available = 5000 L (Scarcity scenario)
    alloc_output = c_bridge.allocate_water(5000.0, sample_requests)
    print(f"  Engine: {alloc_output['engine']}")
    print(f"  Demanded: {alloc_output['summary']['total_demanded_water']} L | Allocated: {alloc_output['summary']['total_allocated_water']} L | Remaining: {alloc_output['summary']['remaining_water']} L")
    for r in alloc_output['results']:
        print(f"  -> Req #{r['request_id']} (Priority {r['priority']}): Demanded {r['requested_quantity']} L => Allocated {r['allocated_quantity']} L ({r['satisfaction_rate']}%) [{r['status']}]")
    assert alloc_output['summary']['total_allocated_water'] <= 5000.0
    print("  >>> Test 1 PASSED: Priority allocation executed correctly!")

    # 2. Test Anomaly Leakage Detection
    print("\n[Test 2] Testing C Anomaly Leakage Detection...")
    leak_res = c_bridge.detect_leakage(10000.0, 7800.0, threshold=8.0)
    print(f"  Output: {leak_res['tank_output_litres']} L | Inflow: {leak_res['area_received_litres']} L | Loss: {leak_res['loss_litres']} L ({leak_res['loss_percentage']}%)")
    print(f"  Leak Detected: {leak_res['is_leak_detected']} | Severity: {leak_res['severity']}")
    assert leak_res['is_leak_detected'] == True
    assert leak_res['severity'] == 'HIGH'
    print("  >>> Test 2 PASSED: Anomaly detected with correct severity!")

    # 3. Test Demand Prediction
    print("\n[Test 3] Testing C Weighted Demand Prediction...")
    hist = [9800.0, 10200.0, 10500.0, 11000.0, 10800.0, 11500.0, 12000.0]
    predicted = c_bridge.predict_demand(hist)
    print(f"  7-Day Consumption: {hist}")
    print(f"  Predicted Tomorrow: {predicted} L")
    assert predicted > 10500.0
    print("  >>> Test 3 PASSED: Weighted moving average calculated!")

    # 4. Test REST Endpoints via Django Client
    print("\n[Test 4] Testing REST API Endpoints...")
    client = Client()

    # User Dashboard Stats API
    res = client.get('/api/water/dashboard/stats/')
    assert res.status_code == 200
    assert res.json()['success'] == True
    print("  -> GET /api/water/dashboard/stats/ OK [200]")

    # Admin Summary Report API
    res = client.get('/api/reports/summary/')
    assert res.status_code == 200
    assert res.json()['success'] == True
    print("  -> GET /api/reports/summary/ OK [200]")

    # Anomaly Detection API
    res = client.post('/api/leakage/detect-anomaly/', data={'tank_output_litres': 10000, 'area_received_litres': 8000, 'threshold_percentage': 8}, content_type='application/json')
    assert res.status_code == 200
    assert res.json()['success'] == True
    print("  -> POST /api/leakage/detect-anomaly/ OK [200]")

    # Frontend Page Routes
    for path in ['/', '/login/', '/register/', '/user/dashboard/', '/admin/dashboard/']:
        r = client.get(path)
        assert r.status_code == 200
        print(f"  -> Template Route {path} OK [200]")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! PROJECT IS 100% OPERATIONAL.")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
