import pytest

from stage1_foundations.pricing import estimate_delivery


def test_standard_delivery_price():
    quote = estimate_delivery(
        "Dodoma",
        "Dar es Salaam",
        3,
        "standard"
    )

    assert quote["origin"] == "Dodoma"
    assert quote["destination"] == "Dar es Salaam"
    assert quote["distance_km"] == 450
    assert quote["price_tzs"] == 7150


def test_express_delivery_costs_more():
    standard = estimate_delivery(
        "Dodoma",
        "Dar es Salaam",
        3,
        "standard"
    )

    express = estimate_delivery(
        "Dodoma",
        "Dar es Salaam",
        3,
        "express"
    )

    assert express["price_tzs"] > standard["price_tzs"]


def test_zero_weight_is_rejected():
    with pytest.raises(ValueError):
        estimate_delivery(
            "Dodoma",
            "Dar es Salaam",
            0,
            "standard"
        )


def test_negative_weight_is_rejected():
    with pytest.raises(ValueError):
        estimate_delivery(
            "Dodoma",
            "Dar es Salaam",
            -2,
            "standard"
        )


def test_unsupported_city_is_rejected():
    with pytest.raises(ValueError):
        estimate_delivery(
            "Dodoma",
            "Mwanza",
            3,
            "standard"
        )


def test_invalid_service_is_rejected():
    with pytest.raises(ValueError):
        estimate_delivery(
            "Dodoma",
            "Dar es Salaam",
            3,
            "overnight"
        )