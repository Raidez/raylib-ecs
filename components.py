import pyray
from ecs import Component
from typing import Optional, TypeAlias
from dataclasses import dataclass, field
from enum import Enum, auto


Color: TypeAlias = pyray.Color
Texture: TypeAlias = pyray.Texture


class Shape(Enum):
    RECTANGLE = auto()
    CIRCLE = auto()


@dataclass
class Debug(Component):
    draw_collision: bool = False
    color: Color = field(default_factory=lambda: Color(*pyray.RED))


@dataclass
class Transform(Component):
    position: pyray.Vector2 = field(default_factory=lambda: pyray.Vector2(0.0, 0.0))
    scale: pyray.Vector2 = field(default_factory=lambda: pyray.Vector2(1.0, 1.0))
    rotation: float = 0.0


@dataclass
class Sprite(Component):
    filename: str
    texture: Optional[Texture] = None
    tint_color: Color = field(default_factory=lambda: Color(*pyray.WHITE))
    use_clip: bool = False
    clip: pyray.Rectangle = field(default_factory=lambda: pyray.Rectangle(0, 0, 0, 0))
    z_index: int = 0

    centered: bool = False
    offset: pyray.Vector2 = field(default_factory=lambda: pyray.Vector2(0.0, 0.0))
    flip_h: bool = False
    flip_v: bool = False


@dataclass
class Position(Component):
    x: float = 0.0
    y: float = 0.0


@dataclass
class Velocity(Component):
    x: float = 0.0
    y: float = 0.0
    accel: float = 0.0
    decel: float = 0.0


@dataclass
class Collision(Component):
    shape: Shape
    has_collision: bool = False
    parameters: dict = field(default_factory=dict)

    def __post_init__(self):
        match self.shape:
            case Shape.CIRCLE:
                self.parameters.setdefault("radius", 10.0)
                self.parameters.setdefault("outline", 1.0)
            case Shape.RECTANGLE:
                self.parameters.setdefault("width", 10.0)
                self.parameters.setdefault("height", 10.0)
                self.parameters.setdefault("outline", 1.0)


@dataclass
class Drawing(Component):
    shape: Shape
    color: Color = field(default_factory=lambda: Color(*pyray.BLACK))
    parameters: dict = field(default_factory=dict)

    def __post_init__(self):
        match self.shape:
            case Shape.CIRCLE:
                self.parameters.setdefault("radius", 10.0)
                self.parameters.setdefault("outline", 1.0)
            case Shape.RECTANGLE:
                self.parameters.setdefault("width", 10.0)
                self.parameters.setdefault("height", 10.0)
                self.parameters.setdefault("outline", 1.0)


@dataclass
class Controller(Component):
    pass
