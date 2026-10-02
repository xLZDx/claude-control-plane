from fastapi import APIRouter, Depends

from .auth import current_user
from .store import all_reports, get_report

router = APIRouter()


@router.get("/reports")
def list_reports(user=Depends(current_user)):
    return [r for r in all_reports() if r.project_id in user.project_ids]


@router.get("/reports/{report_id}/download")
def download_report(report_id: str, user=Depends(current_user)):
    return get_report(report_id).file_bytes()
