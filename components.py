from dataclasses import dataclass, field
from typing import TypeAlias, Union

import pyray

from ecs import Component

Color: TypeAlias = Union[pyray.Color, tuple[int, int, int, int]]
Texture: TypeAlias = Union[str, pyray.Texture]


@dataclass
class Transform(Component):
    position: pyray.Vector2 = field(default_factory=lambda: pyray.Vector2(0.0, 0.0))
    scale: pyray.Vector2 = field(default_factory=lambda: pyray.Vector2(1.0, 1.0))
    rotation: float = 0.0


@dataclass
class Sprite(Component):
    texture: Texture
    tint_color: Color = pyray.WHITE
    use_clip: bool = False
    clip: pyray.Rectangle = field(default_factory=lambda: pyray.Rectangle(0, 0, 0, 0))
    z_index: int = 0

    centered: bool = False
    offset: pyray.Vector2 = field(default_factory=lambda: pyray.Vector2(0.0, 0.0))
    flip_h: bool = False
    flip_v: bool = False
