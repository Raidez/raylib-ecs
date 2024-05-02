from test import *
from ecs import (
    EntityProxy,
    HasComponent,
    HasId,
)


def test_basic_call(basic_context):
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


def test_call(basic_context, entity_hero):
    query, hero = basic_context, entity_hero

    def move_position(entity: EntityProxy, offset: int):
        entity.get(Position).x += offset

    query.call(
        move_position,
        criteria_list=[HasComponent(Position)],
        proxy_components=[Position],
    )(10)
    query.call(move_position, proxy_components=[Position])(10)
    query.call(move_position, HasComponent(Position), Position)(10)
    query.call(move_position, Position, HasComponent(Position))(10)
    query.call(move_position, Position)(10)

    assert hero.get(Position).x == 100


def test_decorator(basic_context, entity_hero):
    query, hero = basic_context, entity_hero

    def move_position(entity: Entity, offset: int):
        entity.get(Position).x += offset

    move_position_dec = Query.decorate(move_position, HasComponent(Position))
    move_position_dec(query, 10)

    assert hero.get(Position).x == 60
