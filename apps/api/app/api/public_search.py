from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.hotel import Hotel, HotelStatus
from app.models.guest_review import GuestReview
from app.api.public_hotels import serialize_public_hotel, _lowest_available_rate

router = APIRouter(prefix="/public/search", tags=["Public Search"])


def _csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@router.get("/hotels")
def search_public_hotels(
    destination: str | None = None,
    city: str | None = None,
    property_types: str | None = None,
    facilities: str | None = None,
    min_rating: float | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    check_in: date | None = None,
    check_out: date | None = None,
    sort: str = "recommended",
    db: Session = Depends(get_db),
):
    if (check_in is None) != (check_out is None):
        from fastapi import HTTPException
        raise HTTPException(400, "check_in and check_out must be provided together")
    if check_in and check_out <= check_in:
        from fastapi import HTTPException
        raise HTTPException(400, "check_out must be after check_in")

    query = db.query(Hotel).filter(Hotel.status == HotelStatus.APPROVED)
    destination_text = (destination or city or "").strip()
    if destination_text:
        needle = f"%{destination_text}%"
        query = query.filter(
            (Hotel.city.ilike(needle))
            | (Hotel.name.ilike(needle))
            | (Hotel.address.ilike(needle))
        )

    hotels = query.all()
    hotel_ids = [hotel.id for hotel in hotels]
    review_map = {}
    if hotel_ids:
        review_rows = (
            db.query(
                GuestReview.hotel_id,
                func.avg(GuestReview.overall_score),
                func.count(GuestReview.id),
            )
            .filter(
                GuestReview.hotel_id.in_(hotel_ids),
                GuestReview.deleted_at.is_(None),
            )
            .group_by(GuestReview.hotel_id)
            .all()
        )
        review_map = {
            row[0]: (round(float(row[1]), 1), int(row[2]))
            for row in review_rows
        }

    selected_types = {item.lower() for item in _csv(property_types)}
    selected_facilities = {item.lower() for item in _csv(facilities)}
    results = []
    for hotel in hotels:
        if selected_types and str(hotel.property_type or "").strip().lower() not in selected_types:
            continue

        star_rating = float(hotel.star_rating) if hotel.star_rating is not None else None
        review_score, review_count = review_map.get(hotel.id, (None, 0))
        effective_score = review_score if review_score is not None else star_rating
        if min_rating is not None and (effective_score is None or effective_score < min_rating):
            continue

        available_facilities = {
            str(item.name).strip().lower()
            for item in hotel.facilities
            if item.available and item.name
        }
        if selected_facilities and not selected_facilities.issubset(available_facilities):
            continue

        breakfast_available = bool(hotel.breakfast_options)
        family_friendly = any(int(room.max_children or 0) > 0 for room in hotel.room_types if room.status)
        adults_only = bool(hotel.room_types) and not family_friendly

        lowest = _lowest_available_rate(db, hotel, check_in, check_out)
        if lowest is None:
            continue
        price = float(lowest["total_price"])
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue

        data = serialize_public_hotel(hotel)
        data.update(
            {
                "rating": effective_score,
                "star_rating": star_rating,
                "review_score": review_score,
                "review_count": review_count,
                "latitude": hotel.latitude,
                "longitude": hotel.longitude,
                "breakfast_available": breakfast_available,
                "family_friendly": family_friendly,
                "adults_only": adults_only,
                "lowest_available_rate": float(lowest["selling_price"]),
                "lowest_available_total": price,
                "lowest_available_currency": lowest["currency"],
                "lowest_available_room_type_id": lowest["room_type_id"],
                "availability_check_in": check_in,
                "availability_check_out": check_out,
            }
        )
        results.append(data)

    if sort == "price_low":
        results.sort(key=lambda item: (item["lowest_available_total"], item["name"].lower()))
    elif sort == "price_high":
        results.sort(key=lambda item: (-item["lowest_available_total"], item["name"].lower()))
    elif sort == "rating":
        results.sort(key=lambda item: (-(item["rating"] or 0), item["name"].lower()))
    else:
        results.sort(
            key=lambda item: (
                -(item["rating"] or 0),
                item["lowest_available_total"],
                item["name"].lower(),
            )
        )

    return {"items": results, "total": len(results)}
