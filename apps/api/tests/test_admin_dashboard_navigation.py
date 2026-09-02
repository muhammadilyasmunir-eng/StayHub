from pathlib import Path


DASHBOARD_JS = Path(__file__).parents[1] / "app" / "static" / "admin-property-operations.js"


def test_admin_dashboard_has_requested_modules():
    source = DASHBOARD_JS.read_text(encoding="utf-8")
    for label in [
        "Active Properties",
        "Pending Properties",
        "Rejected Properties",
        "Invoice Over Due Properties",
        "Dublication Rejection",
        "Reservations",
        "Owners & Users",
        "Reviews",
        "Finance",
        "Finance Reports",
    ]:
        assert label in source


def test_dashboard_cards_navigate_to_working_sections():
    source = DASHBOARD_JS.read_text(encoding="utf-8")
    assert "dashReservations" in source
    assert "dashOwners" in source
    assert "dashReviews" in source
    assert "dashRevenue" in source
    assert "data-dashboard-target" in source
    assert "const target=c.dataset.dashboardTarget" in source
    assert "show(target" in source
