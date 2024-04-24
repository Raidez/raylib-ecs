import raylib
from pyray import (
    Rectangle,
    Vector2,
    draw_texture_pro,
    load_texture,
    unload_texture,
)
from typing import TypeAlias

from components import Transform, Sprite
from ecs import Entity, Query, HasComponent

Texture: TypeAlias = raylib.ffi.CData


def load_resources(entity: Entity):
    if Sprite in entity and isinstance(entity.sprite.texture, str):
        entity.sprite.texture = load_texture(entity.sprite.texture)


def unload_resources(entity: Entity):
    if Sprite in entity and isinstance(entity.sprite.texture, Texture):
        unload_texture(entity.sprite.texture)


def render_sprite(entity: Entity):
    # retrieve data
    texture = entity.sprite.texture
    offset = entity.sprite.offset
    tint_color = entity.sprite.tint_color
    position = entity.transform.position
    scale = entity.transform.scale
    rotation = entity.transform.rotation

    # calculate source, dest and origin (and apply effects)
    source = Rectangle(0, 0, texture.width, texture.height)
    if entity.sprite.clip:
        source = entity.sprite.clip
    if entity.sprite.flip_h:
        source.width = -source.width
    if entity.sprite.flip_v:
        source.height = -source.height
    dest = Rectangle(
        position.x + offset.x,
        position.y + offset.y,
        source.width * scale.x,
        source.height * scale.y,
    )
    origin = Vector2(0.0, 0.0)
    if entity.sprite.centered:
        origin = Vector2(source.width * 0.5 * scale.x, source.height * 0.5 * scale.y)

    draw_texture_pro(texture, source, dest, origin, rotation, tint_color)


################################################################################

load_resources = Query.decorate(load_resources, HasComponent(Sprite))
unload_resources = Query.decorate(unload_resources, HasComponent(Sprite))
render_sprite = Query.decorate(render_sprite, HasComponent(Transform, Sprite))
