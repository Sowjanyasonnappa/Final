from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.oauth2 import user_required

from app.services.invoice_service import (
    download_invoice,
)

router = APIRouter(
    prefix="/invoice",
    tags=["Invoice"],
)


@router.get("/{order_id}")
def invoice(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(user_required),
):

    pdf = download_invoice(
        db,
        current_user,
        order_id,
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename=invoice_{order_id}.pdf"
        },
    )