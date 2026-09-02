from pathlib import Path


DETAIL_FIX_JS = Path(__file__).parents[1] / "app" / "static" / "owner-reservation-detail-fix.js"
MAIN_PY = Path(__file__).parents[1] / "app" / "main.py"


def test_reservation_detail_is_encoding_safe_and_cache_busted():
    detail_fix = DETAIL_FIX_JS.read_text(encoding="utf-8")
    main = MAIN_PY.read_text(encoding="utf-8")

    assert 'id="stayhubReservationDetailClose"' in detail_fix
    assert '>X</button>' in detail_fix
    assert "✕" not in detail_fix
    assert "âœ•" not in detail_fix
    assert "Â·" not in detail_fix
    assert " · " not in detail_fix
    assert "owner-reservation-detail-fix.js?v=2" in main
