import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.dependencies import get_current_user
from app.models.user import User, UserRole

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="StayHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/customer-login", include_in_schema=False)
def customer_login():
    return HTMLResponse((STATIC_DIR / "customer-login.html").read_text(encoding="utf-8"), headers={"Cache-Control":"no-store, no-cache, must-revalidate"})


@app.get("/my-reservations", include_in_schema=False)
def my_reservations():
    return HTMLResponse((STATIC_DIR / "my-reservations.html").read_text(encoding="utf-8"), headers={"Cache-Control":"no-store, no-cache, must-revalidate"})


@app.get("/admin", include_in_schema=False)
def admin_portal():
    path = STATIC_DIR / "admin-panel.html"
    html = path.read_text(encoding="utf-8")
    scripts = '<script src="/static/admin-live-properties-ui.js?v=1"></script><script src="/static/date-defaults.js?v=3"></script><script src="/static/reservation-management-ui.js?v=2"></script><script src="/static/reservation-details-actions-fix.js?v=1"></script><script src="/static/admin-final-property-review.js?v=1"></script><script src="/static/admin-final-review-ui-fix.js?v=1"></script><script src="/static/admin-property-editor.js?v=1"></script><script src="/static/admin-property-operations.js?v=1"></script><script src="/static/admin-reservation-disputes.js?v=2"></script>'
    if "admin-final-review-ui-fix.js?v=1" not in html: html=html.replace("</body>",scripts+"</body>")
    else:
        if "admin-live-properties-ui.js?v=1" not in html: html=html.replace("</body",'<script src="/static/admin-live-properties-ui.js?v=1"></script></body>')
        if "date-defaults.js?v=3" not in html: html=html.replace("</body",'<script src="/static/date-defaults.js?v=3"></script></body>')
        if "reservation-management-ui.js?v=2" not in html: html=html.replace("</body",'<script src="/static/reservation-management-ui.js?v=2"></script></body>')
        if "reservation-details-actions-fix.js?v=1" not in html: html=html.replace("</body",'<script src="/static/reservation-details-actions-fix.js?v=1"></script></body>')
        if "admin-reservation-disputes.js?v=2" not in html: html=html.replace("</body",'<script src="/static/admin-reservation-disputes.js?v=2"></script></body>')
    return HTMLResponse(html,headers={"Cache-Control":"no-store, no-cache, must-revalidate"})


@app.get("/owner",include_in_schema=False)
def owner_portal():
    path=STATIC_DIR/"owner-portal-pro.html"; html=path.read_text(encoding="utf-8")
    scripts='<script src="/static/owner-portal-ops.js?v=3"></script><script src="/static/owner-pricing.js?v=4"></script><script src="/static/owner-reservation-policy.js?v=2"></script><script src="/static/owner-finance.js?v=1"></script><script src="/static/owner-navigation.js?v=1"></script><script src="/static/owner-rejection-workflow.js?v=1"></script><script src="/static/owner-rejection-workflow-v2.js?v=1"></script><script src="/static/owner-auth-guard.js?v=2"></script><script src="/static/owner-terms-workflow.js?v=4"></script><script src="/static/owner-calendar.js?v=2"></script><script src="/static/owner-commission-display-fix.js?v=2"></script><script src="/static/owner-billing-readonly.js?v=1"></script><script src="/static/owner-reservation-detail-fix.js?v=5"></script><script src="/static/owner-reservations-ui.js?v=2"></script><script src="/static/owner-reservation-label-fix.js?v=3"></script><script src="/static/date-defaults.js?v=3"></script><script src="/static/owner-reservation-actions.js?v=3"></script><script src="/static/owner-no-show-detail-ui.js?v=4"></script><script src="/static/owner-room-inventory-photos.js?v=2"></script><script src="/static/owner-room-category-actions.js?v=1"></script><script src="/static/owner-reservation-navigation-fix.js?v=1"></script><script src="/static/owner-room-add-button-fix.js?v=1"></script><script src="/static/owner-reservation-encoding-fix.js?v=1"></script><script src="/static/owner-notification-center.js?v=3"></script>'
    if "owner-rejection-workflow-v2.js" not in html: html=html.replace("</body>",scripts+"</body>")
    else:
        for marker in ("owner-calendar.js?v=2","owner-terms-workflow.js?v=4","owner-commission-display-fix.js?v=2","owner-billing-readonly.js?v=1","owner-reservation-detail-fix.js?v=5","owner-reservations-ui.js?v=2","owner-reservation-label-fix.js?v=3","date-defaults.js?v=3","owner-reservation-actions.js?v=3","owner-no-show-detail-ui.js?v=4","owner-room-inventory-photos.js?v=2","owner-room-category-actions.js?v=1","owner-reservation-navigation-fix.js?v=1","owner-room-add-button-fix.js?v=1","owner-reservation-encoding-fix.js?v=1","owner-notification-center.js?v=3"):
            if marker not in html: html=html.replace("</body>",f'<script src="/static/{marker}"></script></body>')
    return HTMLResponse(html,headers={"Cache-Control":"no-store, no-cache, must-revalidate"})

@app.get("/dashboard",include_in_schema=False)
def dashboard_redirect(current_user:User=Depends(get_current_user)):
    if current_user.role==UserRole.ADMIN:return RedirectResponse(url="/admin",status_code=307)
    if current_user.role==UserRole.HOTEL_OWNER:return RedirectResponse(url="/owner",status_code=307)
    if current_user.role==UserRole.CUSTOMER:return RedirectResponse(url="/my-reservations",status_code=307)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Portal access required")

app.mount("/static",StaticFiles(directory=STATIC_DIR),name="static")
app.include_router(api_router)
app.include_router(api_router,prefix="/api")

@app.get("/health")
def health():
    return {"status":"ok"}
