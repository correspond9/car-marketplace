from app.core.security import mask_registration_number, normalize_phone


def test_normalize_phone_ten_digits() -> None:
    assert normalize_phone("9876543210") == "+919876543210"


def test_normalize_phone_with_country_code() -> None:
    assert normalize_phone("+919876543210") == "+919876543210"


def test_mask_registration_number() -> None:
    assert mask_registration_number("MH12 AB 1234") == "MH12 AB ****"
