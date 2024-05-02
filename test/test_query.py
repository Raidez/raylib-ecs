from test import *
from ecs import (
    HasId,
    HasComponent,
    SugarCriteria,
)

def test_found_by_id(basic_context, entity_hero):
    "check first founded entity by id"
    query, hero = basic_context, entity_hero

    assert query.get(HasId("hero")) == hero

def test_found_by_criteria(basic_context, entity_hero, entity_logo):
    "check founded entities by criteria"
    query, hero, logo = basic_context, entity_hero, entity_logo
    
    assert all(e in (logo, hero) for e in list(query.filter(HasComponent(Position))))

def test_call_function_with_criteria(basic_context):
    query = basic_context

    def assert_(cond):
        assert cond

    query.call(lambda e: assert_(e.has(Position)), HasComponent(Position))()
    query.call(lambda e: assert_(e.id == "hero"), HasId("hero"))()
    query.call(
        lambda e, s: assert_(
            f"{s}/{e.get(Sprite).texture}" == "assets/sprite/hero.png"
        ),
        HasComponent(Sprite),
    )("assets/sprite")


def test_default_order(advanced_context):
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
    for i, found in enumerate(query.filter(SugarCriteria(has=Item))):
        assert order[i] == found.id


def test_forced_order(advanced_context):
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
    entity_list = query.filter(SugarCriteria(has=Item))
    entity_list = sorted(
        entity_list,
        key=lambda e: (e.get(Item).rarity, e.get(Item).quantity),
        reverse=True,
    )
    for i, found in enumerate(entity_list):
        assert order[i] == found.id
