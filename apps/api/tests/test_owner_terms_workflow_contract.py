from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_terms_workflow_api_and_ui_are_wired():
    terms_api = (ROOT / "app/api/admin/terms.py").read_text(encoding="utf-8")
    verification_api = (ROOT / "app/api/admin/verification.py").read_text(encoding="utf-8")
    routes = (ROOT / "app/api/routes.py").read_text(encoding="utf-8")
    main = (ROOT / "app/main.py").read_text(encoding="utf-8")
    owner_ui = (ROOT / "app/static/owner-verification-workflow-v2.js").read_text(encoding="utf-8")
    admin_ui = (ROOT / "app/static/admin-terms-workflow.js").read_text(encoding="utf-8")
    assert "AWAITING_TERMS" in terms_api
    assert "/property/{hotel_id}/approve" in terms_api
    assert "/property/{hotel_id}/accept" in terms_api
    assert "terms_required" in terms_api
    assert "/property/{hotel_id}/accept" in verification_api
    assert "/property/{hotel_id}/submit" in verification_api
    assert "/property/{hotel_id}/go-live" in verification_api
    assert "admin_terms_router" in routes
    assert "admin-terms-workflow.js" in main
    assert "owner-terms-workflow.js" in main
    assert "Terms & Conditions" in owner_ui
    assert "Accommodation Agreement" in owner_ui
    assert "Contract" in owner_ui
    assert "Read & Accept" in owner_ui
    assert "Accept" in owner_ui
    assert "Submit for Final Admin Review" in owner_ui
    assert "stayhubApproveProperty" in admin_ui


def test_public_listing_does_not_treat_awaiting_terms_as_live():
    public_api = (ROOT / "app/api/public_hotels.py").read_text(encoding="utf-8")
    assert "HotelStatus.APPROVED" in public_api
    assert "AWAITING_TERMS" not in public_api
