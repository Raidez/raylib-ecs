from dataclasses import dataclass
from pyray import WHITE, Rectangle, Texture, Vector2, Color

from ecs import Component


@dataclass
class Transform(Component):
    position: Vector2 = Vector2(0.0, 0.0)
    scale: Vector2 = Vector2(1.0, 1.0)
    rotation: float = 0.0


@dataclass
class Sprite(Component):
    texture: Texture
    tint_color: Color = WHITE
    clip: Rectangle = None

    centered: bool = False
    offset: Vector2 = Vector2(0.0, 0.0)
    flip_h: bool = False
    flip_v: bool = False
