import pytest
from fruit_catalog import get_fruit_by_name, get_all_catalog_fruits, ALL_FRUIT_NAMES


def test_get_fruit_by_name_exact():
    fruit = get_fruit_by_name("Kitsune")
    assert fruit is not None
    assert fruit.name == "Kitsune"
    assert fruit.rarity == "Mythical"
    assert fruit.beli_price == 8000000
    assert fruit.robux_price == 4000
    assert fruit.fruit_type == "Beast"


def test_get_fruit_by_alias():
    # Chop -> Blade
    blade = get_fruit_by_name("chop")
    assert blade is not None
    assert blade.name == "Blade"

    # Falcon -> Eagle
    eagle = get_fruit_by_name("falcon")
    assert eagle is not None
    assert eagle.name == "Eagle"

    # Dragon (East)
    dragon = get_fruit_by_name("dragon")
    assert dragon is not None
    assert dragon.name == "Dragon"


def test_get_fruit_by_name_case_insensitive():
    f = get_fruit_by_name("bUdDhA")
    assert f is not None
    assert f.name == "Buddha"
    assert f.rarity == "Legendary"
    assert f.beli_price == 1200000


def test_get_fruit_not_found():
    assert get_fruit_by_name("NonexistentFruit") is None
    assert get_fruit_by_name("") is None


def test_get_all_catalog_fruits():
    all_fruits = get_all_catalog_fruits()
    assert len(all_fruits) >= 40
    names = [f.name for f in all_fruits]
    assert "Rocket" in names
    assert "Kitsune" in names
    assert "Dragon" in names
    assert "Dough" in names
    assert "Leopard" in names
    assert "Yeti" in names
    assert "Gas" in names
