from ecs import Entity, HasComponent, HasId, Query
from test import *


def test_found_by_id(basic_context: Query, entity_hero: Entity):
    "check first founded entity by id"
    query, hero = basic_context, entity_hero

    assert query.get([HasId("hero")]) == hero


def test_found_by_criteria(
    basic_context: Query, entity_hero: Entity, entity_logo: Entity
):
    "check founded entities by criteria"
    query, hero, logo = basic_context, entity_hero, entity_logo

    assert all(e in (logo, hero) for e in list(query.filter([HasComponent(Position)])))


def test_default_order(advanced_context: Query):
    "check founded entities default order"
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
    "check founded entities forced order with sorted()"
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
