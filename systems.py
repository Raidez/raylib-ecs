from pyray import (
    Rectangle,
    Vector2,
    draw_texture_pro,
    load_texture,
    unload_texture,
)

from components import (
    Sprite,
    Transform,
)
from ecs import Entity, HasComponent, Query


# region INIT
def init(query: Query):
    load_resources(query)


def load_resources(query: Query):
    entity_list = query.filter([HasComponent(Sprite)])
    for entity in entity_list:
        if (sprite := entity.get(Sprite)) and sprite.filename:
            sprite.texture = load_texture(sprite.filename)


# endregion


# region CLOSE
def close(query: Query):
    unload_resources(query)


def unload_resources(query: Query):
    entity_list = query.filter([HasComponent(Sprite)])
    for entity in entity_list:
        if (sprite := entity.get(Sprite)) and sprite.texture:
            unload_texture(sprite.texture)


# endregion


# region UPDATE
def update(query: Query, delta: float):
    pass


# endregion


# region DRAW
def draw(query: Query):
    render_sprites(query)


def render_sprites(query: Query):
    entity_list = query.filter([HasComponent(Transform), HasComponent(Sprite)])
    entity_list = sorted(entity_list, key=lambda e: e.get(Sprite).z_index)
    [_draw_sprite(e) for e in entity_list]


# endregion


# region UTILS
def _draw_sprite(entity: Entity):
    sprite = entity.get(Sprite)
    transform = entity.get(Transform)

    if not sprite.texture:
        return

    # retrieve data
    texture = sprite.texture
    offset = sprite.offset
    tint_color = sprite.tint_color
    position = transform.position
    scale = transform.scale
    rotation = transform.rotation

    # calculate source, dest and origin (and apply effects)
    source = Rectangle(0, 0, texture.width, texture.height)
    if sprite.use_clip:
        source = sprite.clip
    if sprite.flip_h:
        source.width = -source.width
    if sprite.flip_v:
        source.height = -source.height
    dest = Rectangle(
        position.x + offset.x,
        position.y + offset.y,
        source.width * scale.x,
        source.height * scale.y,
    )
    origin = Vector2(0.0, 0.0)
    if sprite.centered:
        origin = Vector2(source.width * 0.5 * scale.x, source.height * 0.5 * scale.y)

    draw_texture_pro(texture, source, dest, origin, rotation, tint_color)


# endregion
