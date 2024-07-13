from test import *
from ecs import (
    HasId,
    HasComponent,
    HasValue,
    HasNotComponent,
    FilterCriteria,
    SugarCriteria,
)


def test_id(entity_hero):
    "check if entity meet criteria with HasId"
    hero = entity_hero

    assert Query.check(hero, HasId("hero"))


def test_has_components(entity_hero):
    "check if entity meet criteria with HasComponent"
    hero = entity_hero

    assert Query.check(hero, HasComponent(Position))
    assert Query.check(hero, HasComponent(Sprite))
    assert Query.check(hero, HasComponent(Position, Sprite))
    assert Query.check(hero, HasNotComponent(Spatial))


def test_has_components_value(entity_hero):
    "check if entity meet criteria with HasComponentValue"
    hero = entity_hero

    assert Query.check(hero, HasValue(Position(50, 20)))


def test_filter_criteria(entity_hero):
    "check if entity meet criteria with FilterCriteria"
    hero = entity_hero

    assert Query.check(hero, FilterCriteria(lambda e: e.has(Position)))


def test_sugar_criteria(entity_hero):
    "check if entity meet criteria with SugarCriteria"
    hero = entity_hero

    assert Query.check(hero, SugarCriteria(has=Position, id="hero", position__x=50))
    assert Query.check(hero, SugarCriteria(Position(x=50, y=20)))
