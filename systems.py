from typing import TypeAlias

import raylib
from pyray import Rectangle, Vector2, draw_texture_pro, load_texture, unload_texture

from components import Sprite, Transform
from ecs import Entity, HasComponent, Query

Texture: TypeAlias = raylib.ffi.CData


def load_resources(query: Query):
    entity_list = query.filter(HasComponent(Sprite))
    entity_list = list(filter(lambda e: isinstance(e.sprite.texture, str), entity_list))
    [setattr(e.sprite, "texture", load_texture(e.sprite.texture)) for e in entity_list]


def unload_resources(query: Query):
    entity_list = query.filter(HasComponent(Sprite))
    entity_list = list(
        filter(lambda e: isinstance(e.sprite.texture, Texture), entity_list)
    )
    [
        setattr(e.sprite, "texture", unload_texture(e.sprite.texture))
        for e in entity_list
    ]


def draw_sprite(entity: Entity):
    # retrieve data
    texture = entity.sprite.texture
    offset = entity.sprite.offset
    tint_color = entity.sprite.tint_color
    position = entity.transform.position
    scale = entity.transform.scale
    rotation = entity.transform.rotation

    # calculate source, dest and origin (and apply effects)
    source = Rectangle(0, 0, texture.width, texture.height)
    if entity.sprite.use_clip:
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


def render_sprites(query: Query):
    entity_list = query.filter(HasComponent(Transform, Sprite))
    entity_list = sorted(entity_list, key=lambda e: e.sprite.z_index)
    [draw_sprite(e) for e in entity_list]
