from test import *
from ecs import (
    HasComponent,
)

def test_basic_decorator(basic_context, entity_hero):
    query, hero = basic_context, entity_hero
    def move_position(entity: Entity, offset: int):
        entity.get(Position).x += offset

    move_position_dec = Query.decorate(move_position, HasComponent(Position))
    move_position_dec(query, 10)

    assert hero.get(Position).x == 60
