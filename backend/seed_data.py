import os
import django
from datetime import date, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser
from tanks.models import Tank
from water.models import Area, WaterRequest, WaterUsage, Feedback
from distribution.models import DistributionSchedule
from leakage.models import LeakageReport
from notifications.models import Notification

def seed_database():
    print("Seeding Intelligent Water Distribution System Database...")

    # 1. Areas
    areas_data = [
        {"name": "Poonamallee", "loc": "Chennai West", "pop": 8500, "prio": 4, "quota": 85000.0},
        {"name": "Avadi", "loc": "Chennai Northwest", "pop": 12000, "prio": 3, "quota": 110000.0},
        {"name": "Porur", "loc": "Chennai Southwest", "pop": 9500, "prio": 4, "quota": 90000.0},
        {"name": "Ambattur", "loc": "Chennai North", "pop": 15000, "prio": 4, "quota": 130000.0},
        {"name": "Guindy Industrial", "loc": "Chennai South", "pop": 6000, "prio": 5, "quota": 60000.0},
        {"name": "Govt Hospital Zone", "loc": "Central Health Campus", "pop": 4000, "prio": 2, "quota": 45000.0},
    ]

    area_objs = {}
    for a in areas_data:
        area, created = Area.objects.get_or_create(
            area_name=a["name"],
            defaults={
                "location": a["loc"],
                "population": a["pop"],
                "priority": a["prio"],
                "daily_quota_litres": a["quota"],
                "status": "ACTIVE"
            }
        )
        area_objs[a["name"]] = area

    print(f"-> Created {len(area_objs)} distribution areas.")

    # 2. Users
    # Admin User
    admin_user, _ = CustomUser.objects.get_or_create(
        email="admin@water.gov",
        defaults={
            "username": "admin",
            "name": "System Administrator",
            "mobile": "9988776655",
            "role": "ADMIN",
            "is_staff": True,
            "is_superuser": True
        }
    )
    admin_user.set_password("admin123")
    admin_user.save()

    # Citizen User (Ramya M)
    user_ramya, _ = CustomUser.objects.get_or_create(
        email="ramya@gmail.com",
        defaults={
            "username": "ramya",
            "name": "Ramya M",
            "mobile": "9876543210",
            "address": "25, Lakeview Avenue, Poonamallee",
            "area": area_objs.get("Poonamallee"),
            "house_number": "25",
            "role": "USER",
            "daily_water_quota_litres": 350.0
        }
    )
    user_ramya.set_password("ramya123")
    user_ramya.save()

    # Additional Citizen Users
    user_hospital, _ = CustomUser.objects.get_or_create(
        email="hospital@chennaimedical.org",
        defaults={
            "username": "hospital_incharge",
            "name": "Dr. V. Raman (Civil Hospital)",
            "mobile": "9840123456",
            "address": "Emergency Medical Complex, Sector 2",
            "area": area_objs.get("Govt Hospital Zone"),
            "house_number": "Block A",
            "role": "USER",
            "daily_water_quota_litres": 5000.0
        }
    )
    user_hospital.set_password("user123")
    user_hospital.save()

    user_karthik, _ = CustomUser.objects.get_or_create(
        email="karthik@gmail.com",
        defaults={
            "username": "karthik",
            "name": "Karthik Subramanian",
            "mobile": "9123456789",
            "address": "12, Gandhi Nagar, Avadi",
            "area": area_objs.get("Avadi"),
            "house_number": "12B",
            "role": "USER",
            "daily_water_quota_litres": 350.0
        }
    )
    user_karthik.set_password("user123")
    user_karthik.save()

    print("-> Created Admin and Citizen users.")

    # 3. Tanks
    tanks_data = [
        {"code": "T001", "name": "Main Reservoir Tank 1", "loc": "Poonamallee Hill", "cap": 100000.0, "cur": 72000.0},
        {"code": "T002", "name": "Sector 4 Elevated Tank", "loc": "Avadi Water Works", "cap": 80000.0, "cur": 64000.0},
        {"code": "T003", "name": "Porur Tower Reservoir", "loc": "Porur Junction", "cap": 60000.0, "cur": 37200.0},
        {"code": "T004", "name": "Ambattur Industrial Tank", "loc": "Ambattur Estate", "cap": 50000.0, "cur": 22500.0},
    ]

    tank_objs = []
    for t in tanks_data:
        tank, _ = Tank.objects.get_or_create(
            tank_id=t["code"],
            defaults={
                "tank_name": t["name"],
                "location": t["loc"],
                "capacity": t["cap"],
                "current_level": t["cur"],
                "status": "ACTIVE"
            }
        )
        tank_objs.append(tank)

    print(f"-> Created {len(tank_objs)} Water Storage Tanks.")

    # 4. Water Requests
    req_date = date.today() + timedelta(days=1)
    requests_data = [
        {"user": user_ramya, "area": area_objs["Poonamallee"], "qty": 500.0, "prio": 4, "reason": "Household domestic requirement", "status": "PENDING"},
        {"user": user_hospital, "area": area_objs["Govt Hospital Zone"], "qty": 3500.0, "prio": 2, "reason": "ICU and Surgical Ward continuous supply", "status": "APPROVED"},
        {"user": user_karthik, "area": area_objs["Avadi"], "qty": 450.0, "prio": 4, "reason": "Residential storage refill", "status": "PENDING"},
    ]

    for r in requests_data:
        WaterRequest.objects.get_or_create(
            user=r["user"],
            area=r["area"],
            requested_quantity=r["qty"],
            defaults={
                "request_date": req_date,
                "priority": r["prio"],
                "reason": r["reason"],
                "status": r["status"]
            }
        )

    print("-> Created sample water requests.")

    # 5. Distribution Schedules
    today = date.today()
    DistributionSchedule.objects.get_or_create(
        area=area_objs["Poonamallee"],
        tank=tank_objs[0],
        scheduled_date=today + timedelta(days=1),
        defaults={
            "start_time": time(6, 0),
            "end_time": time(8, 0),
            "allocated_quantity": 25000.0,
            "status": "SCHEDULED"
        }
    )

    DistributionSchedule.objects.get_or_create(
        area=area_objs["Avadi"],
        tank=tank_objs[1],
        scheduled_date=today + timedelta(days=1),
        defaults={
            "start_time": time(8, 30),
            "end_time": time(10, 30),
            "allocated_quantity": 30000.0,
            "status": "SCHEDULED"
        }
    )

    print("-> Created distribution schedules.")

    # 6. Usage Records (Last 7 days for Ramya)
    for i in range(7):
        u_date = today - timedelta(days=i)
        usage_qty = 85.0 + (i * 12.5) if i != 2 else 520.0 # Day 2 was high consumption
        WaterUsage.objects.get_or_create(
            user=user_ramya,
            area=area_objs["Poonamallee"],
            usage_date=u_date,
            defaults={"quantity": usage_qty, "source": "TAP_SUPPLY"}
        )

    print("-> Created 7-day usage history.")

    # 7. Leakage Reports
    LeakageReport.objects.get_or_create(
        area=area_objs["Porur"],
        location="Near Porur Lake Pipeline Junction #14",
        defaults={
            "user": user_ramya,
            "description": "Continuous underground water bubbling and surface pooling along sidewalk.",
            "severity": "HIGH",
            "loss_volume_litres": 1800.0,
            "status": "UNDER_REVIEW"
        }
    )

    LeakageReport.objects.get_or_create(
        area=area_objs["Avadi"],
        location="Sector 3 Main Distribution Valve",
        defaults={
            "user": user_karthik,
            "description": "Pressure valve leakage with audible hissing sound.",
            "severity": "MODERATE",
            "loss_volume_litres": 450.0,
            "status": "REPORTED"
        }
    )

    # 8. Notifications
    Notification.objects.get_or_create(
        user=user_ramya,
        title="Distribution Scheduled",
        defaults={
            "message": "Water distribution scheduled for your area (Poonamallee) tomorrow from 6:00 AM to 8:00 AM.",
            "notification_type": "SCHEDULE",
            "is_read": False
        }
    )

    Notification.objects.get_or_create(
        user=user_ramya,
        title="Water Conservation Tip",
        defaults={
            "message": "Peak summer rationing protocol in effect. Please store only daily needed quota and check domestic taps.",
            "notification_type": "INFO",
            "is_read": True
        }
    )

    print("-> Seed complete! System is fully primed and ready.")

if __name__ == "__main__":
    seed_database()
