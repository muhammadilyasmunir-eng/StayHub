from types import SimpleNamespace
from unittest.mock import Mock

from app.models.user import UserRole
from app.services.hotel_service import get_hotels_for_user


def test_admin_can_see_all_hotels():
    db = Mock()
    db.query.return_value.all.return_value = ["hotel-1", "hotel-2", "hotel-3"]

    admin = SimpleNamespace(id=99, role=UserRole.ADMIN)

    assert get_hotels_for_user(db, admin) == ["hotel-1", "hotel-2", "hotel-3"]
    db.query.return_value.all.assert_called_once()
    db.query.return_value.filter.assert_not_called()


def test_hotel_owner_can_see_only_owned_hotels():
    db = Mock()
    db.query.return_value.filter.return_value.all.return_value = ["owned-hotel"]

    owner = SimpleNamespace(id=5, role=UserRole.HOTEL_OWNER)

    assert get_hotels_for_user(db, owner) == ["owned-hotel"]
    db.query.return_value.filter.assert_called_once()
