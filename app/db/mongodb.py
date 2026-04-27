"""
db/mongodb.py - Conexion asincrona a MongoDB con Motor.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

_mongo_client: AsyncIOMotorClient | None = None
_mongo_db: AsyncIOMotorDatabase | None = None


def init_mongodb() -> None:
    """Crea el cliente Motor y selecciona la base de datos configurada."""
    global _mongo_client, _mongo_db

    try:
        _mongo_client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10,
        )
        _mongo_db = _mongo_client[settings.mongodb_db_name]
        logger.info("Cliente MongoDB inicializado", base_de_datos=settings.mongodb_db_name)
    except Exception as e:
        logger.error("Error al inicializar MongoDB", error=str(e))
        raise


async def close_mongodb() -> None:
    """Cierra el cliente Motor correctamente."""
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        logger.info("Conexion MongoDB cerrada correctamente.")


def get_mongo_db() -> AsyncIOMotorDatabase:
    """Retorna la base de datos MongoDB lista para consultas asincronas."""
    if _mongo_db is None:
        raise RuntimeError(
            "La base de datos MongoDB no esta inicializada. "
            "Asegurate de llamar a init_mongodb() al arrancar la app."
        )
    return _mongo_db


class MongoCollections:
    """Colecciones MongoDB del modelo WellQ descrito en el PDF."""

    USUARIOS = "usuarios"
    INVITATIONS = "invitations"
    PUSH_TOKENS = "push_tokens"
    CLINICS = "clinics"
    CLINICIANS = "clinicians"
    SPECIALITIES_CATALOG = "specialities_catalog"
    PATIENTS = "patients"
    CASES = "cases"
    INTAKES = "intakes"
    CONSENTS = "consents"
    HISTORIAL_MEDICO = "historial_medico"
    CHECKINS = "checkins"
    METRICS = "metrics"
    MAP_STRUCTINTEG = "map_structinteg"
    APPOINTMENTS = "appointments"
    CLINICAL_NOTES = "clinical_notes"
    EJERCICIOS_CATALOGO = "ejercicios_catalogo"
    PROGRAM_TEMPLATES = "program_templates"
    PATIENT_PROGRAMS = "patient_programs"
    CLINICAL_PROGRAMS = "clinical_programs"
    SCHEDULED_EXERCISES = "scheduled_exercises"
    PATIENT_ROUTINES = "patient_routines"
    PATIENT_WORKOUT_LOGS = "patient_workout_logs"
    PATIENT_CUSTOM_EXERCISES = "patient_custom_exercises"
    PATIENT_GOALS = "patient_goals"
    PATIENT_COMMITMENTS = "patient_commitments"
    ALERTS = "alerts"
    COMMUNICATIONS_LOG = "communications_log"
    ACTIONS_LOG = "actions_log"
    DIAGNOSTIC_CODES = "diagnostic_codes"
    DIAGNOSES_SECTIONS = "diagnoses_sections"
    STATE_RULE_CONFIGS = "state_rule_configs"
    CREDENTIALS = "credentials"
    LEGAL_DOCS = "legal_docs"
    TICKET = "ticket"
    TICKET_CATEGORIES = "ticket_categories"
    CHANNELS = "channels"
    EMAIL_TEMPLATE = "email_template"
    EMAIL_CONFIG = "email_config"
    EMAIL_INFOTICKET = "email_infoticket"
    RESPONDER = "responder"
    MEDIA = "media"
