import itertools
from pyray import (
    KeyboardKey,
    Rectangle,
    Vector2,
    check_collision_circle_rec,
    check_collision_circles,
    check_collision_recs,
    draw_circle,
    draw_circle_lines,
    draw_rectangle,
    draw_rectangle_lines,
    draw_texture_pro,
    is_key_down,
    load_texture,
    unload_texture,
)

from components import (
    Collision,
    Controller,
    Debug,
    Drawing,
    Position,
    Shape,
    Sprite,
    Transform,
    Velocity,
)
from ecs import Entity, HasComponent, HasId, HasValues, Query


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
    update_physics(query, delta)
    check_collisions(query)
    move_paddle(query, delta)


def update_physics(query: Query, delta: float):
    entity_list = query.filter([HasComponent(Position), HasComponent(Velocity)])
    for entity in entity_list:
        position = entity.get(Position)
        velocity = entity.get(Velocity)

        # reverse velocity if ball hit the paddle
        if entity.get(Collision).has_collision:
            velocity.x *= -1
            velocity.y *= -1

        position.x += velocity.x * delta
        position.y += velocity.y * delta


def check_collisions(query: Query):
    entity_list = query.filter([HasComponent(Position), HasComponent(Collision)])
    for entity1, entity2 in itertools.permutations(entity_list, 2):
        collision1 = entity1.get(Collision)
        collision2 = entity2.get(Collision)
        position1 = entity1.get(Position)
        position2 = entity2.get(Position)

        collision1.has_collision = False
        collision2.has_collision = False

        if collision1.shape == Shape.CIRCLE and collision2.shape == Shape.CIRCLE:
            if check_collision_circles(
                Vector2(position1.x, position1.y),
                collision1.parameters["radius"],
                Vector2(position2.x, position2.y),
                collision2.parameters["radius"],
            ):
                collision1.has_collision = True
                collision2.has_collision = True

        elif (
            collision1.shape == Shape.RECTANGLE and collision2.shape == Shape.RECTANGLE
        ):
            if check_collision_recs(
                Rectangle(
                    position1.x,
                    position1.y,
                    collision1.parameters["width"],
                    collision1.parameters["height"],
                ),
                Rectangle(
                    position2.x,
                    position2.y,
                    collision2.parameters["width"],
                    collision2.parameters["height"],
                ),
            ):
                collision1.has_collision = True
                collision2.has_collision = True

        elif collision1.shape == Shape.CIRCLE and collision2.shape == Shape.RECTANGLE:
            if check_collision_circle_rec(
                Vector2(position1.x, position1.y),
                collision1.parameters["radius"],
                Rectangle(
                    position2.x,
                    position2.y,
                    collision2.parameters["width"],
                    collision2.parameters["height"],
                ),
            ):
                collision1.has_collision = True
                collision2.has_collision = True

        elif collision1.shape == Shape.RECTANGLE and collision2.shape == Shape.CIRCLE:
            if check_collision_circle_rec(
                Vector2(position2.x, position2.y),
                collision2.parameters["radius"],
                Rectangle(
                    position1.x,
                    position1.y,
                    collision1.parameters["width"],
                    collision1.parameters["height"],
                ),
            ):
                collision1.has_collision = True
                collision2.has_collision = True


def move_paddle(query: Query, delta: float):
    if entity := query.get(
        [HasId("paddle"), HasComponent(Position), HasComponent(Controller)]
    ):
        if is_key_down(KeyboardKey.KEY_LEFT):
            entity.get(Position).x -= 400 * delta
        if is_key_down(KeyboardKey.KEY_RIGHT):
            entity.get(Position).x += 400 * delta


# endregion


# region DRAW
def draw(query: Query):
    render_sprites(query)
    draw_shapes(query)
    draw_collisions(query)


def render_sprites(query: Query):
    entity_list = query.filter([HasComponent(Transform), HasComponent(Sprite)])
    entity_list = sorted(entity_list, key=lambda e: e.get(Sprite).z_index)
    [_draw_sprite(e) for e in entity_list]


def draw_shapes(query: Query):
    entity_list = query.filter([HasComponent(Position), HasComponent(Drawing)])
    for entity in entity_list:
        position = entity.get(Position)
        drawing = entity.get(Drawing)

        match drawing.shape:
            case Shape.CIRCLE:
                draw_circle(
                    int(position.x),
                    int(position.y),
                    int(drawing.parameters["radius"]),
                    drawing.color,
                )
            case Shape.RECTANGLE:
                draw_rectangle(
                    int(position.x),
                    int(position.y),
                    int(drawing.parameters["width"]),
                    int(drawing.parameters["height"]),
                    drawing.color,
                )


def draw_collisions(query: Query):
    entity_list = query.filter(
        [
            HasValues(debug__draw_collision=True),
            HasComponent(Position),
            HasComponent(Collision),
        ]
    )
    for entity in entity_list:
        position = entity.get(Position)
        collision = entity.get(Collision)
        debug = entity.get(Debug)

        print(collision.has_collision)

        match collision.shape:
            case Shape.CIRCLE:
                call = draw_circle if collision.has_collision else draw_circle_lines
                call(
                    int(position.x),
                    int(position.y),
                    int(collision.parameters["radius"]),
                    debug.color,
                )
            case Shape.RECTANGLE:
                call = (
                    draw_rectangle if collision.has_collision else draw_rectangle_lines
                )
                call(
                    int(position.x),
                    int(position.y),
                    int(collision.parameters["width"]),
                    int(collision.parameters["height"]),
                    debug.color,
                )


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
