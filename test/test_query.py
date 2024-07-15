from ecs import *
from test import *


def test_get(basic_context: Query, logo: Entity):
    """Check the founded entity is the first in tree entities."""
    query = basic_context

    assert query.get() == logo


def test_get_only_active(basic_context: Query):
    """Check the founded entity is active."""
    query = basic_context

    if chest := query.get([HasId("chest")]):
        chest.is_active = False

    assert query.get([HasId("chest")]) is None


def test_found_all(basic_context: Query, hero: Entity, logo: Entity, chest: Entity):
    """Check all founded entities."""
    query = basic_context

    result = query.filter()
    assert len(result) == 4
    assert hero in result
    assert logo in result
    assert chest in result
    assert chest.entities[0] in result


def test_found_all2(advanced_context: Query):
    """Check all founded entities."""
    query = advanced_context

    assert len(query.filter()) == 13


def test_found_by_id(basic_context: Query, hero: Entity):
    """Check first founded entity by id."""
    query = basic_context

    assert query.get([HasId("hero")]) == hero


def test_found_by_criteria(basic_context: Query, hero: Entity, logo: Entity):
    """Check founded entities by criteria."""
    query = basic_context

    assert all(e in (logo, hero) for e in list(query.filter([HasComponent(Position)])))


def test_found_only_active(advanced_context: Query):
    """Check founded entities only active."""
    query = advanced_context

    if chest := query.get([HasId("chest")]):
        chest.is_active = False

    assert len(query.filter()) == 2


def test_default_order(advanced_context: Query):
    """Check founded entities default order."""
    query = advanced_context

    order = [
        "gold",
        "diamond",
        "key",
        "book",
        "sack",
        "sugar",
        "milk",
        "meat",
        "bread",
        "gold",
    ]
    for i, found in enumerate(query.filter([HasComponent(Item)])):
        assert order[i] == found.id


def test_forced_order(advanced_context: Query):
    """Check founded entities forced order with sorted()."""
    query = advanced_context

    order = [
        "diamond",
        "book",
        "key",
        "sack",
        "gold",
        "gold",
        "meat",
        "sugar",
        "milk",
        "bread",
    ]
    entity_list = query.filter([HasComponent(Item)])
    entity_list = sorted(
        entity_list,
        key=lambda e: (e.get(Item).rarity, e.get(Item).quantity),
        reverse=True,
    )
    for i, found in enumerate(entity_list):
        assert order[i] == found.id
