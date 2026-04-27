"""
MongoDB schema bootstrap for the WellQ data model.

The PDF model is represented as collection validators plus indexes. Validators
only make the required contract strict; optional clinical payloads stay flexible
for imports and incremental backend work.
"""

from dataclasses import dataclass, field
from typing import Any

import structlog
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT, IndexModel
from pymongo.errors import CollectionInvalid, OperationFailure

from app.db.mongodb import MongoCollections as C

logger = structlog.get_logger(__name__)

JsonSchema = dict[str, Any]


@dataclass(frozen=True)
class CollectionSchema:
    name: str
    required: tuple[str, ...] = ()
    properties: JsonSchema = field(default_factory=dict)
    indexes: tuple[IndexModel, ...] = ()

    @property
    def validator(self) -> JsonSchema:
        schema: JsonSchema = {"bsonType": "object", "additionalProperties": True}
        if self.required:
            schema["required"] = list(self.required)
        if self.properties:
            schema["properties"] = self.properties
        return {"$jsonSchema": schema}


def _idx(*fields: tuple[str, Any], unique: bool = False, sparse: bool = False, name: str | None = None) -> IndexModel:
    return IndexModel(list(fields), unique=unique, sparse=sparse, name=name)


def _string() -> JsonSchema:
    return {"bsonType": "string"}


def _array() -> JsonSchema:
    return {"bsonType": "array"}


def _date() -> JsonSchema:
    return {"bsonType": "date"}


def _bool() -> JsonSchema:
    return {"bsonType": "bool"}


def _number() -> JsonSchema:
    return {"bsonType": ["int", "long", "double", "decimal"]}


def _object() -> JsonSchema:
    return {"bsonType": "object"}


MONGO_SCHEMAS: tuple[CollectionSchema, ...] = (
    CollectionSchema(C.USUARIOS, ("email", "hashed_password", "roles"), {"email": _string(), "hashed_password": _string(), "roles": _array()}, (_idx(("email", ASCENDING), unique=True), _idx(("jti", ASCENDING), sparse=True))),
    CollectionSchema(C.INVITATIONS, ("token_hash", "email_norm", "expires_at"), {"token_hash": _string(), "email_norm": _string(), "expires_at": _date()}, (_idx(("token_hash", ASCENDING), unique=True), _idx(("email_norm", ASCENDING)), _idx(("expires_at", ASCENDING)), _idx(("used", ASCENDING), ("expires_at", ASCENDING)))),
    CollectionSchema(C.PUSH_TOKENS, ("user_id", "fcm_token"), {"user_id": _string(), "fcm_token": _string()}, (_idx(("user_id", ASCENDING), ("fcm_token", ASCENDING), unique=True), _idx(("user_id", ASCENDING)), _idx(("is_active", ASCENDING)), _idx(("updated_at", DESCENDING)))),
    CollectionSchema(C.CLINICS, ("name",), {"name": _string()}, (_idx(("name", ASCENDING)), _idx(("state", ASCENDING)), _idx(("email", ASCENDING), sparse=True))),
    CollectionSchema(C.CLINICIANS, (), {"first_name": _string(), "last_name": _string(), "ids": _object(), "contact": _object()}, (_idx(("clinician_id", ASCENDING), unique=True, sparse=True), _idx(("contact.email", ASCENDING), sparse=True), _idx(("last_name", ASCENDING), ("first_name", ASCENDING)), _idx(("clinic_id", ASCENDING), sparse=True), _idx(("clinic_ids", ASCENDING), sparse=True))),
    CollectionSchema(C.SPECIALITIES_CATALOG, ("name",), {"name": _string(), "code": _string()}),
    CollectionSchema(C.PATIENTS, (), {"patient_id": _string(), "first_name": _string(), "last_name": _string(), "contact": _object()}, (_idx(("patient_id", ASCENDING), unique=True, sparse=True), _idx(("ids.patient_id", ASCENDING), sparse=True), _idx(("last_name", ASCENDING)), _idx(("contact.phone", ASCENDING), sparse=True), _idx(("contact.email", ASCENDING), sparse=True), _idx(("care_clinician_id", ASCENDING), ("state", ASCENDING)))),
    CollectionSchema(C.CASES, ("patient_id", "status", "title", "start_date"), {"status": _string(), "title": _string(), "start_date": _date()}, (_idx(("patient_id", ASCENDING)), _idx(("status", ASCENDING)), _idx(("primary_provider_id", ASCENDING), sparse=True))),
    CollectionSchema(C.INTAKES, ("type",), {"patient_id": _string(), "type": _string(), "data": _object()}, (_idx(("patient_id", ASCENDING)), _idx(("type", ASCENDING)), _idx(("created_at", DESCENDING)))),
    CollectionSchema(C.CONSENTS, ("patient_id", "type", "version", "state", "signed_at"), {"patient_id": _string(), "type": _string(), "version": _string(), "state": _string(), "signed_at": _date()}, (_idx(("patient_id", ASCENDING), ("state", ASCENDING)),)),
    CollectionSchema(C.HISTORIAL_MEDICO, ("paciente_id",), {"paciente_id": _string()}, (_idx(("paciente_id", ASCENDING), unique=True), _idx(("created_at", DESCENDING)), _idx(("estado_act.est_act_nom", ASCENDING)))),
    CollectionSchema(C.CHECKINS, ("check_in_id", "user_id", "timestamp", "type", "mood"), {"check_in_id": _string(), "user_id": _string(), "timestamp": _date(), "type": _string(), "mood": _number()}, (_idx(("user_id", ASCENDING)), _idx(("timestamp", DESCENDING)), _idx(("user_id", ASCENDING), ("timestamp", DESCENDING)))),
    CollectionSchema(C.METRICS, ("user_id", "from_ts"), {"user_id": _string(), "from_ts": _date(), "to_ts": _date(), "source": _string(), "sensors": _object()}, (_idx(("user_id", ASCENDING)), _idx(("from_ts", DESCENDING)), _idx(("user_id", ASCENDING), ("from_ts", DESCENDING)))),
    CollectionSchema(C.MAP_STRUCTINTEG, ("session_id", "user_id", "timestamp", "type", "created_by", "points", "summary"), {"session_id": _string(), "user_id": _string(), "timestamp": _date(), "type": _string(), "created_by": _string(), "points": _array(), "summary": _object()}, (_idx(("user_id", ASCENDING)), _idx(("session_id", ASCENDING)), _idx(("timestamp", DESCENDING)), _idx(("case_id", ASCENDING), sparse=True))),
    CollectionSchema(C.APPOINTMENTS, (), {"status": _string(), "start_time": _date(), "end_time": _date()}, (_idx(("patient_id", ASCENDING)), _idx(("case_id", ASCENDING)), _idx(("provider_id", ASCENDING)), _idx(("clinic_id", ASCENDING)), _idx(("start_time", DESCENDING)), _idx(("status", ASCENDING)), _idx(("external_id", ASCENDING), sparse=True))),
    CollectionSchema(C.CLINICAL_NOTES, ("template_name", "content"), {"template_name": _string(), "content": _object()}, (_idx(("patient_id", ASCENDING)), _idx(("case_id", ASCENDING)), _idx(("appointment_id", ASCENDING)), _idx(("created_at", DESCENDING)))),
    CollectionSchema(C.EJERCICIOS_CATALOGO, ("exercise_id", "eje_cod", "eje_nom"), {"exercise_id": _string(), "eje_cod": _string(), "eje_nom": _string()}, (_idx(("eje_cod", ASCENDING), unique=True), _idx(("eje_nom", ASCENDING), unique=True), _idx(("eje_nom", TEXT), name="eje_nom_text"), _idx(("tags", ASCENDING)), _idx(("external_ids.wibbi", ASCENDING), sparse=True))),
    CollectionSchema(C.PROGRAM_TEMPLATES, ("template_id", "name"), {"template_id": _string(), "name": _string()}, (_idx(("template_ids.wibbi", ASCENDING), sparse=True), _idx(("clinician_id", ASCENDING), sparse=True), _idx(("clinic_id", ASCENDING), sparse=True), _idx(("tags", ASCENDING)), _idx(("name", TEXT), name="program_template_name_text"))),
    CollectionSchema(C.PATIENT_PROGRAMS, ("patient_id", "template_ids"), {"patient_id": _string(), "template_ids": _array()}, (_idx(("patient_id", ASCENDING)), _idx(("template_ids", ASCENDING)), _idx(("patient_id", ASCENDING), ("active_until", ASCENDING)))),
    CollectionSchema(C.CLINICAL_PROGRAMS, ("program_id", "patient_id", "clinician_id", "name"), {"program_id": _string(), "patient_id": _string(), "clinician_id": _string(), "name": _string()}, (_idx(("wibbi_program_id", ASCENDING), sparse=True), _idx(("patient_id", ASCENDING)), _idx(("clinician_id", ASCENDING)))),
    CollectionSchema(C.SCHEDULED_EXERCISES, ("patient_id",), {"patient_id": _string()}, (_idx(("patient_id", ASCENDING)), _idx(("exercise_id", ASCENDING), sparse=True))),
    CollectionSchema(C.PATIENT_ROUTINES, ("patient_id",), {"patient_id": _string()}, (_idx(("patient_id", ASCENDING)),)),
    CollectionSchema(C.PATIENT_WORKOUT_LOGS, ("patient_id",), {"patient_id": _string()}, (_idx(("patient_id", ASCENDING)), _idx(("routine_id", ASCENDING), sparse=True))),
    CollectionSchema(C.PATIENT_CUSTOM_EXERCISES, ("patient_id",), {"patient_id": _string()}, (_idx(("patient_id", ASCENDING)),)),
    CollectionSchema(C.PATIENT_GOALS, ("patient_id",), {"patient_id": _string()}, (_idx(("patient_id", ASCENDING), unique=True),)),
    CollectionSchema(C.PATIENT_COMMITMENTS, ("patient_id",), {"patient_id": _string()}, (_idx(("patient_id", ASCENDING), unique=True),)),
    CollectionSchema(C.ALERTS, ("patient_id", "alert_type"), {"patient_id": _string(), "alert_type": _string()}, (_idx(("patient_id", ASCENDING)), _idx(("alert_type", ASCENDING)), _idx(("read_at", ASCENDING), sparse=True), _idx(("action_taken", ASCENDING), sparse=True), _idx(("created_at", DESCENDING)), _idx(("patient_id", ASCENDING), ("read_at", ASCENDING)))),
    CollectionSchema(C.COMMUNICATIONS_LOG, ("recipients", "channel", "status"), {"recipients": _string(), "channel": _string(), "status": _number()}, (_idx(("recipients", ASCENDING)), _idx(("created_at", DESCENDING)))),
    CollectionSchema(C.ACTIONS_LOG, ("type",), {"type": _string(), "metadata": _object()}, (_idx(("type", ASCENDING)), _idx(("read_at", ASCENDING), sparse=True), _idx(("updated_at", DESCENDING)), _idx(("metadata.care_clinician_id", ASCENDING), ("read_at", ASCENDING)))),
    CollectionSchema(C.DIAGNOSTIC_CODES, ("diag_id", "diag_name"), {"diag_id": _string(), "diag_name": _string()}, (_idx(("diag_id", ASCENDING), unique=True), _idx(("diag_name", ASCENDING)))),
    CollectionSchema(C.DIAGNOSES_SECTIONS, ("section_id", "diag_ids"), {"section_id": _string(), "diag_ids": _array()}, (_idx(("section_id", ASCENDING), unique=True),)),
    CollectionSchema(C.STATE_RULE_CONFIGS, ("name", "thresholds"), {"name": _string(), "clinic_id": _string(), "is_default": _bool(), "thresholds": _object()}, (_idx(("clinic_id", ASCENDING), sparse=True), _idx(("is_default", ASCENDING)))),
    CollectionSchema(C.CREDENTIALS, ("patient_id", "connection_type", "username", "password_encrypted"), {"patient_id": _string(), "connection_type": _string(), "username": _string(), "password_encrypted": _string()}, (_idx(("patient_id", ASCENDING)), _idx(("connection_type", ASCENDING)), _idx(("is_active", ASCENDING)))),
    CollectionSchema(C.LEGAL_DOCS, ("type", "version"), {"type": _string(), "version": _string()}, (_idx(("type", ASCENDING), ("version", ASCENDING), unique=True),)),
    CollectionSchema(C.TICKET, ("title", "description", "status", "reported_at", "reporter"), {"title": _string(), "description": _string(), "status": _string(), "reported_at": _date(), "reporter": _object()}, (_idx(("reported_at", DESCENDING)), _idx(("status", ASCENDING)), _idx(("responder_id", ASCENDING), sparse=True))),
    CollectionSchema(C.TICKET_CATEGORIES, ("campaign", "category"), {"campaign": _string(), "category": _string()}, (_idx(("campaign", ASCENDING), ("category", ASCENDING), unique=True),)),
    CollectionSchema(C.CHANNELS, ("channel",), {"channel": _string()}, (_idx(("channel", ASCENDING), unique=True),)),
    CollectionSchema(C.RESPONDER, ("name", "group", "user", "password"), {"name": _string(), "group": _string(), "user": _string(), "password": _string()}, (_idx(("user", ASCENDING), unique=True),)),
    CollectionSchema(C.EMAIL_TEMPLATE, ("campaign", "subject", "title", "body"), {"campaign": _string(), "subject": _string(), "title": _string(), "body": _string()}, (_idx(("campaign", ASCENDING)),)),
    CollectionSchema(C.EMAIL_CONFIG, ("campaign", "email", "password", "server_smtp", "server_imap", "port"), {"campaign": _string(), "email": _string(), "password": _string(), "server_smtp": _string(), "server_imap": _string(), "port": _number()}, (_idx(("campaign", ASCENDING), unique=True),)),
    CollectionSchema(C.EMAIL_INFOTICKET, ("campaign", "header", "body", "footer"), {"campaign": _string(), "header": _string(), "body": _string(), "footer": _string()}, (_idx(("campaign", ASCENDING), unique=True),)),
    CollectionSchema(C.MEDIA, (), {"alt": _string(), "url": _string(), "filename": _string(), "mime_type": _string()}, (_idx(("alt", ASCENDING), sparse=True), _idx(("filename", ASCENDING), sparse=True), _idx(("created_at", DESCENDING)))),
)


async def ensure_mongo_schema(db: AsyncIOMotorDatabase) -> None:
    """Create every collection, JSON schema validator, and index from the PDF model."""

    existing = set(await db.list_collection_names())

    for schema in MONGO_SCHEMAS:
        if schema.name not in existing:
            try:
                await db.create_collection(schema.name, validator=schema.validator)
                logger.info("Coleccion MongoDB creada", collection=schema.name)
            except CollectionInvalid:
                pass
        else:
            try:
                await db.command("collMod", schema.name, validator=schema.validator)
                logger.info("Validador MongoDB actualizado", collection=schema.name)
            except OperationFailure as exc:
                logger.warning("No se pudo actualizar el validador MongoDB", collection=schema.name, error=str(exc))

        if schema.indexes:
            await db[schema.name].create_indexes(list(schema.indexes))
            logger.info("Indices MongoDB asegurados", collection=schema.name, count=len(schema.indexes))
