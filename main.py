import copy
from pyray import *

from components import *
from ecs import Entity, Query, SugarCriteria
from systems import load_resources, render_sprite, unload_resources

WIDTH, HEIGHT = 800, 450
init_window(WIDTH, HEIGHT, "raylib [core] example - basic window")
set_target_fps(60)

world = Entity(
    "world",
    scarfy := Entity(
        "scarfy",
        Transform(Vector2(WIDTH / 2, HEIGHT / 2), scale=Vector2(0.5, 0.5)),
        Sprite(load_texture("assets/scarfy.png"), centered=True),
    ),
)
query = Query(world)

scarfy1 = copy.deepcopy(scarfy)
scarfy2 = copy.deepcopy(scarfy)
world.extend(scarfy1, scarfy2)

scarfy1.update(Transform(Vector2(100, 100), scale=Vector2(0.2, 0.2), rotation=45))
scarfy2.update(Transform(Vector2(600, 250), scale=Vector2(0.8, 0.8), rotation=-90))

################################################################################


def update(entity: Entity, delta: float):
    entity.transform.rotation += 10.0 * delta


update = Query.decorate(update, SugarCriteria(Transform, id="scarfy"))

################################################################################

load_resources(query)

while not window_should_close():
    # update
    delta = get_frame_time()
    update(query, delta)

    # render
    begin_drawing()
    clear_background(RAYWHITE)
    render_sprite(query)
    end_drawing()

unload_resources(query)
close_window()
