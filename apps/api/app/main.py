from pathlib import Path
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, status
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.routes import api_router
from app import models
from app.dependencies import get_current_user
from app.models.user import User, UserRole
STATIC_DIR=Path(__file__).resolve().parent/"static"
app=FastAPI(title=settings.app_name,version=settings.app_version,debug=settings.debug)
@app.on_event("startup")
def ensure_schema():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE terms_documents ADD COLUMN IF NOT EXISTS document_type VARCHAR(40) DEFAULT 'terms'"));conn.execute(text("UPDATE terms_documents SET document_type='terms' WHERE document_type IS NULL"));conn.execute(text("ALTER TABLE hotels ADD COLUMN IF NOT EXISTS commission_percent NUMERIC(5,2)"));conn.execute(text("ALTER TABLE hotels ALTER COLUMN tax_percent DROP NOT NULL"));conn.execute(text("ALTER TABLE hotels ALTER COLUMN tax_percent DROP DEFAULT"));conn.execute(text("UPDATE hotels SET tax_percent=NULL WHERE tax_percent=0"));conn.execute(text("DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_type WHERE typname='reservationdisputestatus') THEN ALTER TYPE reservationdisputestatus ADD VALUE IF NOT EXISTS 'OWNER_VERIFIED'; END IF; END $$"))
DATE_DEFAULT_SCRIPT='<script src="/static/date-defaults.js?v=3"></script>'
RESERVATION_MANAGEMENT_SCRIPT='<script src="/static/reservation-management-ui.js?v=2"></script>'
RESERVATION_DETAIL_ACTIONS_FIX_SCRIPT='<script src="/static/reservation-details-actions-fix.js?v=1"></script>'
OWNER_ROOM_INVENTORY_PHOTOS_SCRIPT='<script src="/static/owner-room-inventory-photos.js?v=2"></script>'
OWNER_ROOM_CATEGORY_ACTIONS_SCRIPT='<script src="/static/owner-room-category-actions.js?v=1"></script>'
OWNER_REGISTER_ROOM_PRICING_SCRIPT='<script src="/static/public/owner-register-room-pricing.js?v=1"></script>'
OWNER_RESERVATION_NAVIGATION_FIX_SCRIPT='<script src="/static/owner-reservation-navigation-fix.js?v=1"></script>'
OWNER_ROOM_ADD_BUTTON_FIX_SCRIPT='<script src="/static/owner-room-add-button-fix.js?v=1"></script>'
OWNER_RESERVATION_ENCODING_FIX_SCRIPT='<script src="/static/owner-reservation-encoding-fix.js?v=1"></script>'
OWNER_NO_SHOW_DETAIL_UI_SCRIPT='<script src="/static/owner-no-show-detail-ui.js?v=4"></script>'
@app.get("/",include_in_schema=False)
def public_website():
    html=(STATIC_DIR/"index.html").read_text(encoding="utf-8");html=html.replace('href="/static/public/login.html"','href="/customer-login"');
    if "date-defaults.js" not in html: html=html.replace("</body>",DATE_DEFAULT_SCRIPT+"</body>")
    return HTMLResponse(html,headers={"Cache-Control":"no-store, no-cache, must-revalidate"})
@app.get("/customer-login",include_in_schema=False)
def customer_login(): return HTMLResponse((STATIC_DIR/"customer-login.html").read_text(encoding="utf-8"),headers={"Cache-Control":"no-store, no-cache, must-revalidate"})
@app.get("/my-reservations",include_in_schema=False)
def my_reservations(): return HTMLResponse((STATIC_DIR/"my-reservations.html").read_text(encoding="utf-8"),headers={"Cache-Control":"no-store, no-cache, must-revalidate"})
@app.get("/reservation-messages",include_in_schema=False)
def reservation_messages(): return HTMLResponse((STATIC_DIR/"reservation-messages.html").read_text(encoding="utf-8"),headers={"Cache-Control":"no-store, no-cache, must-revalidate"})
@app.get("/hotel/{slug}",include_in_schema=False)
def public_hotel_detail(slug:str):
    html=(STATIC_DIR/"public"/"hotel.html").read_text(encoding="utf-8");
    if "date-defaults.js" not in html: html=html.replace("</body>",DATE_DEFAULT_SCRIPT+"</body>")
    return HTMLResponse(html,headers={"Cache-Control":"no-store, no-cache, must-revalidate"})
@app.get("/booking",include_in_schema=False)
def public_booking_checkout():
    html=(STATIC_DIR/"public"/"booking.html").read_text(encoding="utf-8");
    if "date-defaults.js" not in html: html=html.replace("</body>",DATE_DEFAULT_SCRIPT+"</body>")
    return HTMLResponse(html,headers={"Cache-Control":"no-store, no-cache, must-revalidate"})
@app.get("/owner-register-v2.html",include_in_schema=False)
def owner_registration():
    path=STATIC_DIR/"public"/"owner-register-v2.html";html=path.read_text(encoding="utf-8");scripts='<script src="/static/public/owner-register-operational-ui.js?v=1"></script><script src="/static/public/owner-property-edit.js?v=1"></script><script src="/static/public/owner-register-room-pricing.js?v=1"></script><script src="/static/date-defaults.js?v=3"></script>'
    if "owner-register-operational-ui.js" not in html: html=html.replace("</body>",scripts+"</body>")
    else:
        if "owner-property-edit.js" not in html: html=html.replace("</body",'<script src="/static/public/owner-property-edit.js?v=1"></script></body>')
        if "owner-register-room-pricing.js" not in html: html=html.replace("</body",OWNER_REGISTER_ROOM_PRICING_SCRIPT+"</body>")
        if "date-defaults.js" not in html: html=html.replace("</body",'<script src="/static/date-defaults.js?v=3"></script></body>')
    return HTMLResponse(html,headers={"Cache-Control":"no-store, no-cache, must-revalidate"})
@app.get("/list-your-property",include_in_schema=False)
def list_your_property(): return owner_registration()
@app.get("/admin",include_in_schema=False)
def admin_panel():
    path=STATIC_DIR/"admin-panel.html";html=path.read_text(encoding="utf-8");scripts='<script src="/static/admin-finance.js?v=1"></script><script src="/static/admin-property-media.js?v=1"></script><script src="/static/admin-property-operations.js?v=1"></script><script src="/static/admin-property-editor.js?v=1"></script><script src="/static/admin-auth-guard.js?v=3"></script><script src="/static/admin-approval-workflow-v2.js?v=3"></script><script src="/static/admin-final-property-review.js?v=1"></script><script src="/static/admin-final-review-ui-fix.js?v=1"></script><script src="/static/admin-live-properties-ui.js?v=1"></script><script src="/static/date-defaults.js?v=3"></script><script src="/static/reservation-management-ui.js?v=2"></script><script src="/static/reservation-details-actions-fix.js?v=1"></script><script src="/static/admin-reservation-disputes.js?v=2"></script>'
    for marker in ("admin-approval-workflow-v2.js","admin-terms-workflow.js"): html=html.replace(f'<script src="/static/{marker}?v=2"></script>','');html=html.replace(f'<script src="/static/{marker}?v=1"></script>','')
    if "admin-final-review-ui-fix.js?v=1" not in html: html=html.replace("</body>",scripts+"</body>")
    else:
        if "admin-live-properties-ui.js?v=1" not in html: html=html.replace("</body",'<script src="/static/admin-live-properties-ui.js?v=1"></script></body>')
        if "date-defaults.js?v=3" not in html: html=html.replace("</body",'<script src="/static/date-defaults.js?v=3"></script></body>')
        if "reservation-management-ui.js?v=2" not in html: html=html.replace("</body",RESERVATION_MANAGEMENT_SCRIPT+"</body>")
        if "reservation-details-actions-fix.js?v=1" not in html: html=html.replace("</body",RESERVATION_DETAIL_ACTIONS_FIX_SCRIPT+"</body>")
        if "admin-reservation-disputes.js?v=2" not in html: html=html.replace("</body",'<script src="/static/admin-reservation-disputes.js?v=2"></script></body>')
    return HTMLResponse(html,headers={"Cache-Control":"no-store, no-cache, must-revalidate"})
@app.get("/owner",include_in_schema=False)
def owner_portal():
    path=STATIC_DIR/"owner-portal-pro.html";html=path.read_text(encoding="utf-8");scripts='<script src="/static/owner-portal-ops.js?v=3"></script><script src="/static/owner-pricing.js?v=4"></script><script src="/static/owner-reservation-policy.js?v=2"></script><script src="/static/owner-finance.js?v=1"></script><script src="/static/owner-navigation.js?v=1"></script><script src="/static/owner-rejection-workflow.js?v=1"></script><script src="/static/owner-rejection-workflow-v2.js?v=1"></script><script src="/static/owner-auth-guard.js?v=2"></script><script src="/static/owner-terms-workflow.js?v=4"></script><script src="/static/owner-calendar.js?v=2"></script><script src="/static/owner-commission-display-fix.js?v=2"></script><script src="/static/owner-billing-readonly.js?v=1"></script><script src="/static/owner-reservation-detail-fix.js?v=5"></script><script src="/static/owner-reservations-ui.js?v=2"></script><script src="/static/owner-reservation-label-fix.js?v=3"></script><script src="/static/date-defaults.js?v=3"></script><script src="/static/owner-reservation-actions.js?v=3"></script><script src="/static/owner-no-show-detail-ui.js?v=4"></script><script src="/static/owner-room-inventory-photos.js?v=2"></script><script src="/static/owner-room-category-actions.js?v=1"></script><script src="/static/owner-reservation-navigation-fix.js?v=1"></script><script src="/static/owner-room-add-button-fix.js?v=1"></script><script src="/static/owner-reservation-encoding-fix.js?v=1"></script><script src="/static/owner-notification-center.js?v=4"></script><script src="/static/owner-customer-messages-ui.js?v=1"></script><script src="/static/owner-customer-messages-override.js?v=1"></script>'
    if "owner-rejection-workflow-v2.js" not in html: html=html.replace("</body>",scripts+"</body>")
    else:
        for marker in ("owner-calendar.js?v=2","owner-terms-workflow.js?v=4","owner-commission-display-fix.js?v=2","owner-billing-readonly.js?v=1","owner-reservation-detail-fix.js?v=5","owner-reservations-ui.js?v=2","owner-reservation-label-fix.js?v=3","date-defaults.js?v=3","owner-reservation-actions.js?v=3","owner-no-show-detail-ui.js?v=4","owner-room-inventory-photos.js?v=2","owner-room-category-actions.js?v=1","owner-reservation-navigation-fix.js?v=1","owner-room-add-button-fix.js?v=1","owner-reservation-encoding-fix.js?v=1","owner-notification-center.js?v=4","owner-customer-messages-ui.js?v=1","owner-customer-messages-override.js?v=1"):
            if marker not in html: html=html.replace("</body>",f'<script src="/static/{marker}"></script></body>')
    return HTMLResponse(html,headers={"Cache-Control":"no-store, no-cache, must-revalidate"})
@app.get("/dashboard",include_in_schema=False)
def dashboard_redirect(current_user:User=Depends(get_current_user)):
    if current_user.role==UserRole.ADMIN:return RedirectResponse(url="/admin",status_code=307)
    if current_user.role==UserRole.HOTEL_OWNER:return RedirectResponse(url="/owner",status_code=307)
    if current_user.role==UserRole.CUSTOMER:return RedirectResponse(url="/my-reservations",status_code=307)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Portal access required")
app.mount("/static",StaticFiles(directory=STATIC_DIR),name="static");app.include_router(api_router);app.include_router(api_router,prefix="/api")
@app.get("/health")
async def health():return {"status":"healthy","version":settings.app_version}
@app.get("/db-test")
async def db_test():
    with engine.connect() as conn:return {"database":conn.execute(text("SELECT version();")).scalar()}
