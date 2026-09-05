from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.hotel import Hotel, HotelStatus
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
    query = db.query(Hotel).filter(Hotel.status == HotelStatus.APPROVED)

    destination_text = (destination or city or "").strip()
    if destination_text:
        needle = f"%{destination_text}%"
        query = query.filter(
            (Hotel.city.ilike(needle))
            | (Hotel.name.ilike(needle))
            | (Hotel.address.ilike(needle))
        )

    selected_types = {item.lower() for item in _csv(property_types)}
    if selected_types:
        query = query.filter(Hotel.property_type.in_(list(selected_types)))

    selected_facilities = {item.lower() for item in _csv(facilities)}
    results = []
    for hotel in query.all():
        rating = float(hotel.star_rating) if hotel.star_rating is not None else None
        if min_rating is not None and (rating is None or rating < min_rating):
            continue

        available_facilities = {
            str(item.name).strip().lower()
            for item in hotel.facilities
            if item.available and item.name
        }
        if selected_facilities and not selected_facilities.issubset(available_facilities):
            continue

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
                "rating": rating,
                "review_count": None,
                "latitude": hotel.latitude,
                "longitude": hotel.longitude,
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
    elif sort == "distance":
        # A precise destination-distance sort is applied by the browser when map coordinates are available.
        results.sort(key=lambda item: item["name"].lower())
    else:
        results.sort(
            key=lambda item: (
                -(item["rating"] or 0),
                item["lowest_available_total"],
                item["name"].lower(),
            )
        )

    return {"items": results, "total": len(results)}
