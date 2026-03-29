from fastapi import APIRouter
from services.audit_logger import AuditLogger

router = APIRouter(prefix="/alerts/{alert_id}/audit", tags=["audit"])
audit = AuditLogger()

@router.get("")
def get_audit_trail(alert_id: str):
    return audit.get_audit_trail(alert_id)
