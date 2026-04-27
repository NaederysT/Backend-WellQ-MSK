"""
Seed demo data for local/API testing against MongoDB.

Run from the repo root:
    python -m app.scripts.seed_demo_data
"""

import asyncio
from datetime import datetime, timezone

from app.db.mongodb import MongoCollections as C
from app.db.mongodb import close_mongodb, get_mongo_db, init_mongodb


NOW = datetime.now(timezone.utc)


async def main() -> None:
    init_mongodb()
    db = get_mongo_db()

    clinics = [
        {
            "clinic_id": "CL-001",
            "name": "Clinica San Jose",
            "address": "Av. Providencia 1234, Santiago",
            "phone": "+56911111111",
            "email": "contacto@clinicasanjose.com",
            "state": "active",
            "status": "active",
            "tier": "enterprise",
            "contact": {
                "primary_name": "Juan Perez",
                "primary_email": "admin@clinicasanjose.com",
                "primary_phone": "+56911111111",
            },
            "billing": {
                "company_name": "Inversiones San Jose SpA",
                "tax_id": "77.123.456-7",
                "billing_email": "facturacion@clinicasanjose.com",
                "address": "Av. Providencia 1234, Santiago",
            },
            "subscription": {
                "plan_name": "Enterprise Anual",
                "status": "active",
                "mrr_value": 1500,
                "currency": "USD",
                "started_at": NOW,
            },
            "licenses": {
                "total_limit": 5000,
                "currently_active": 2,
                "available": 4998,
                "utilization_percentage": 0.04,
            },
            "created_at": NOW,
            "updated_at": NOW,
        },
        {
            "clinic_id": "CL-002",
            "name": "Centro Medico Integral",
            "address": "Las Condes 456, Santiago",
            "phone": "+56922222222",
            "email": "hola@centromedico.com",
            "state": "active",
            "status": "active",
            "tier": "pro",
            "created_at": NOW,
            "updated_at": NOW,
        },
    ]

    clinicians = [
        {
            "clinician_id": "DR-001",
            "first_name": "Ana",
            "last_name": "Morales",
            "ids": {"tm3": "TM3-DR-001"},
            "contact": {"email": "ana.morales@clinicasanjose.com", "phone": "+56933333333"},
            "specialties": ["physiotherapy", "msk"],
            "clinic_id": "CL-001",
            "clinic_ids": ["CL-001"],
            "state": "active",
            "created_at": NOW,
            "updated_at": NOW,
        }
    ]

    patients = [
        {
            "patient_id": "P-DEMO-001",
            "first_name": "Maria",
            "last_name": "Gonzalez",
            "dob": datetime(1988, 5, 12, tzinfo=timezone.utc),
            "gender": "female",
            "contact": {"phone": "+56944444444", "email": "maria.demo@example.com"},
            "ids": {"tm3": "TM3-P-001"},
            "care_clinician_id": "DR-001",
            "authorized_clinicians": ["DR-001"],
            "clinic_ids": ["CL-001"],
            "state": "active",
            "status": "stable",
            "created_at": NOW,
            "updated_at": NOW,
        },
        {
            "patient_id": "P-DEMO-002",
            "first_name": "Pedro",
            "last_name": "Rojas",
            "contact": {"phone": "+56955555555", "email": "pedro.demo@example.com"},
            "clinic_ids": ["CL-001"],
            "state": "active",
            "status": "at_risk",
            "created_at": NOW,
            "updated_at": NOW,
        },
    ]

    alerts = [
        {
            "patient_id": "P-DEMO-002",
            "alert_type": "risk",
            "created_at": NOW,
            "read_at": None,
            "action_taken": None,
        }
    ]

    for clinic in clinics:
        await db[C.CLINICS].update_one({"clinic_id": clinic["clinic_id"]}, {"$set": clinic}, upsert=True)

    for clinician in clinicians:
        await db[C.CLINICIANS].update_one({"clinician_id": clinician["clinician_id"]}, {"$set": clinician}, upsert=True)

    for patient in patients:
        await db[C.PATIENTS].update_one({"patient_id": patient["patient_id"]}, {"$set": patient}, upsert=True)

    for alert in alerts:
        await db[C.ALERTS].update_one(
            {"patient_id": alert["patient_id"], "alert_type": alert["alert_type"]},
            {"$set": alert},
            upsert=True,
        )

    await close_mongodb()
    print("Demo data seeded: clinics=2 clinicians=1 patients=2 alerts=1")


if __name__ == "__main__":
    asyncio.run(main())
