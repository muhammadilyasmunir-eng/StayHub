from fastapi import APIRouter
from app.api.users import router as user_router
from app.api.hotel import router as hotel_router
from app.api.room_type import router as room_type_router
from app.api.room import router as room_router
from app.api.guest import router as guest_router
from app.api.reservation import router as reservation_router
from app.api.availability import router as availability_router
from app.api.uploads import router as upload_router
from app.api.upload_test import router as upload_test_router
from app.api.admin.hotels import router as admin_hotel_router
from app.api.admin.property_operations import router as admin_property_operations_router
from app.api.admin.reservations import router as admin_reservation_router
from app.api.admin.reservation_management import router as admin_reservation_management_router
from app.api.admin.verification import router as admin_verification_router
from app.api.admin.terms import router as admin_terms_router
from app.api.public_hotels import router as public_hotel_router
from app.api.public_bookings import router as public_booking_router
from app.api.public_booking_otp import router as public_booking_otp_router
from app.api.finance import router as finance_router
from app.api.destinations import router as destination_router
from app.api.password_reset import router as password_reset_router
from app.api.customer_reservations import router as customer_reservation_router
from app.api.notifications import router as notification_router

api_router = APIRouter()

for router in (
    user_router, hotel_router, room_type_router, room_router, guest_router,
    reservation_router, customer_reservation_router, availability_router, upload_router, upload_test_router,
    admin_hotel_router, admin_property_operations_router, admin_reservation_router,
    admin_reservation_management_router, admin_verification_router, admin_terms_router,
    public_hotel_router, public_bookings_router if False else public_booking_router,
    public_booking_otp_router, finance_router, destination_router, password_reset_router,
    notification_router,
):
    api_router.include_router(router)
