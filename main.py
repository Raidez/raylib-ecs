from pyray import (
    RAYWHITE,
    Color,
    Vector2,
    begin_drawing,
    clear_background,
    close_window,
    end_drawing,
    get_frame_time,
    init_window,
    set_target_fps,
    window_should_close,
)

from components import (
    Sprite,
    Transform,
)
from ecs import Entity, Has, Query
from systems import (
    close,
    draw,
    init,
    update,
)

WIDTH, HEIGHT = 800, 450
init_window(WIDTH, HEIGHT, "raylib [core] example - basic window")
set_target_fps(60)
BACKGROUND_COLOR = Color(*RAYWHITE)

world = Entity(
    "world",
    [],
    [
        scarfy := Entity(
            "scarfy",
            [
                Transform(Vector2(WIDTH / 2, HEIGHT / 2), scale=Vector2(0.5, 0.5)),
                Sprite("assets/scarfy.png", centered=True),
            ],
        ),
    ],
)

scarfy1 = scarfy.clone("scarfy")
scarfy2 = scarfy.clone("scarfy")
world.entities.extend([scarfy1, scarfy2])

scarfy1.add(Transform(Vector2(100, 100), scale=Vector2(0.2, 0.2), rotation=45))
scarfy2.add(Transform(Vector2(600, 250), scale=Vector2(0.8, 0.8), rotation=-90))
scarfy2.get(Sprite).z_index = -5

################################################################################


def update_scarfy(query: Query, delta: float):
    entity_list = query.filter([Has(id="scarfy", component=Transform)])
    for entity in entity_list:
        entity.get(Transform).rotation += 10.0 * delta


################################################################################

query = Query(world)
init(query)

while not window_should_close():
    # update
    delta = get_frame_time()
    update_scarfy(query, delta)
    update(query, delta)

    # render
    begin_drawing()
    clear_background(BACKGROUND_COLOR)
    draw(query)
    end_drawing()

close(query)
close_window()
