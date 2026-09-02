def room_type_display_name(value):
    return str(value or '').split(' · Room ', 1)[0].strip()


def test_reservation_room_display_uses_only_room_type_name():
    assert room_type_display_name('Deluxe Twin · Room 10') == 'Deluxe Twin'
    assert room_type_display_name('Deluxe Master · Room AUTO-23-3') == 'Deluxe Master'
    assert room_type_display_name('Deluxe Master Interconnecting Room · Room AUTO-28-1') == 'Deluxe Master Interconnecting Room'
