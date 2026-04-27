from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import MongoCollections, get_mongo_db
from app.utils.mongo import serialize_mongo

router = APIRouter(prefix="/api/clinics", tags=["Gestion de Clinicas"])


def _clinic_filter(clinic_id: str) -> dict:
    if ObjectId.is_valid(clinic_id):
        return {"_id": ObjectId(clinic_id)}
    return {"clinic_id": clinic_id}


@router.get("", summary="Listar clinicas con filtros y paginacion")
async def list_clinics(
    search: str | None = None,
    tier: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "name",
    sort_order: str = "asc",
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    clauses: list[dict] = []
    if search:
        clauses.append({"$or": [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"contact.email": {"$regex": search, "$options": "i"}},
        ]})
    if tier:
        clauses.append({"tier": tier})
    if status:
        clauses.append({"$or": [{"status": status}, {"state": status}]})
    filters: dict = {"$and": clauses} if clauses else {}

    collection = mongo[MongoCollections.CLINICS]
    total = await collection.count_documents(filters)
    direction = -1 if sort_order == "desc" else 1
    cursor = (
        collection.find(filters)
        .sort(sort_by, direction)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    data = [serialize_mongo(doc) async for doc in cursor]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": page * page_size < total,
        "data": data,
    }


@router.post("", summary="Registro de una nueva clinica en el sistema", status_code=status.HTTP_201_CREATED)
async def create_clinic(body: dict = Body(...), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    now = datetime.now(timezone.utc)
    document = {
        **body,
        "state": body.get("state", body.get("status", "active")),
        "created_at": body.get("created_at", now),
        "updated_at": now,
    }
    result = await mongo[MongoCollections.CLINICS].insert_one(document)
    created = await mongo[MongoCollections.CLINICS].find_one({"_id": result.inserted_id})
    return {"status": "success", "message": "Clinica registrada correctamente", "data": serialize_mongo(created)}


@router.post("/bulk/email", summary="Envio de comunicaciones masivas a encargados de clinicas")
async def bulk_email(body: dict = Body(...), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    now = datetime.now(timezone.utc)
    clinic_ids = body.get("clinic_ids", [])
    docs = [
        {
            "recipients": clinic_id,
            "channel": "email",
            "status": 0,
            "metadata": {"subject": body.get("subject"), "body": body.get("body"), "clinic_id": clinic_id},
            "created_at": now,
            "updated_at": now,
        }
        for clinic_id in clinic_ids
    ]
    if docs:
        await mongo[MongoCollections.COMMUNICATIONS_LOG].insert_many(docs)
    return {"status": "success", "message": f"Correos encolados para {len(docs)} clinicas.", "subject": body.get("subject")}


@router.get("/export", summary="Exportacion de lista de clinicas")
async def export_clinics(format: str = Query("csv", description="Formato: csv o excel")):
    return {
        "status": "success",
        "download_url": f"https://storage.wellq.co/exports/clinics_export_2026.{format}",
        "expires_in": "3600s",
    }


@router.get("/{clinic_id}", summary="Obtener detalle de una clinica")
async def get_clinic(clinic_id: str = Path(...), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    clinic = await mongo[MongoCollections.CLINICS].find_one(_clinic_filter(clinic_id))
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinica no encontrada")
    return serialize_mongo(clinic)


@router.patch("/{clinic_id}", summary="Actualizar campos de una clinica")
async def update_clinic(
    clinic_id: str = Path(...),
    updates: dict = Body(...),
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    updates.pop("_id", None)
    updates["updated_at"] = datetime.now(timezone.utc)
    result = await mongo[MongoCollections.CLINICS].update_one(_clinic_filter(clinic_id), {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Clinica no encontrada")
    clinic = await mongo[MongoCollections.CLINICS].find_one(_clinic_filter(clinic_id))
    return {"status": "success", "message": "Clinica actualizada correctamente", "data": serialize_mongo(clinic)}


@router.get("/{clinic_id}/contact", summary="Informacion de contacto y facturacion de la clinica")
async def get_clinic_contact(clinic_id: str = Path(...), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    clinic = await mongo[MongoCollections.CLINICS].find_one(_clinic_filter(clinic_id), {"contact": 1, "billing": 1, "email": 1, "phone": 1})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinica no encontrada")
    return {"clinic_id": clinic_id, "contact_info": serialize_mongo(clinic.get("contact", {})), "billing_info": serialize_mongo(clinic.get("billing", {}))}


@router.get("/{clinic_id}/subscription", summary="Detalles del plan de suscripcion contratado")
async def get_clinic_subscription(clinic_id: str = Path(...), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    clinic = await mongo[MongoCollections.CLINICS].find_one(_clinic_filter(clinic_id), {"subscription": 1, "tier": 1, "state": 1})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinica no encontrada")
    return {"clinic_id": clinic_id, "subscription": serialize_mongo(clinic.get("subscription", {"tier": clinic.get("tier"), "state": clinic.get("state")}))}


@router.get("/{clinic_id}/usage", summary="Estadisticas de uso de la plataforma por la clinica")
async def get_clinic_usage(clinic_id: str = Path(...), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    patient_count = await mongo[MongoCollections.PATIENTS].count_documents({"clinic_ids": {"$in": [clinic_id]}})
    clinician_count = await mongo[MongoCollections.CLINICIANS].count_documents({"clinic_ids": {"$in": [clinic_id]}})
    return {"clinic_id": clinic_id, "metrics": {"patients": patient_count, "clinicians": clinician_count}}


@router.get("/{clinic_id}/license", summary="Monitoreo de utilizacion de licencias de pacientes")
async def get_clinic_license(clinic_id: str = Path(...), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    clinic = await mongo[MongoCollections.CLINICS].find_one(_clinic_filter(clinic_id), {"licenses": 1})
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinica no encontrada")
    return {"clinic_id": clinic_id, "licenses": serialize_mongo(clinic.get("licenses", {}))}


@router.get("/{clinic_id}/invoices", summary="Historial de facturas emitidas a la clinica")
async def get_clinic_invoices(clinic_id: str = Path(...)):
    return {"clinic_id": clinic_id, "pending_balance": 0, "invoices": []}


@router.post("/{clinic_id}/impersonate", summary="Ingreso como soporte tecnico", status_code=status.HTTP_201_CREATED)
async def impersonate_clinic(
    clinic_id: str = Path(...),
    body: dict = Body(...),
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    reason = body.get("reason", "")
    if len(reason) < 10:
        raise HTTPException(status_code=400, detail="La justificacion debe tener mas de 10 caracteres.")

    now = datetime.now(timezone.utc)
    audit_doc = {
        "type": "clinic.impersonate",
        "metadata": {"clinic_id": clinic_id, "reason": reason},
        "updated_at": now,
        "updated_by": body.get("admin_id", "system"),
    }
    result = await mongo[MongoCollections.ACTIONS_LOG].insert_one(audit_doc)
    return {
        "success": True,
        "message": "Impersonation session started successfully.",
        "session_id": str(result.inserted_id),
        "clinic_id": clinic_id,
        "reason_logged": reason,
    }
