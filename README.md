# Quick Start
## Use a context world
First we need to define a global entity (=context) whom hold inside all other entity.
And make a query with the defined context.
```python
from ecs import *

world = Entity("world")
query = Query(context=world)
```

## Define component
Components are simple classes whom inherit from Component.

```python
class Position(Component):
    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y
```

You can use the standard librairie *dataclass* decorator to save some code.
```python
from dataclasses import dataclass

@dataclass
class Position(Component):
    x = 0.0
    y = 0.0
```

## Create an entity
```python
scarfy = Entity("scarfy", Position(x=50.0, y=220.0))
world.append(scarfy)

# or more condensed
# world.append(Entity("scarfy", Position(x=50.0, y=220.0)))
```

We can also defined all entities inside the world at the initialisation.
```python
world = Entity("world",
    Entity("scarfy", Position(x=50.0, y=220.0)),
)
query = Query(context=world)
```

## The purpose of Query
If we want to make a system that affect multiple entities or we have a lot of entities,
we can use the query methodology.

1. define the query context ```query = Query(context=world)```
2. use query to find entities by criteria ```query.get(HasId("scarfy")) # return the first entity whom meet criteria```

## Call a system
System is a standard function.
```python
def update_scarfy(entity: Entity):
    entity.position.x += 10.0
```

They are several methods to call the system:
- standard
- query.call()
- Query.decorator()


```python
update_scarfy(scarfy)

query.call(update_scarfy, criteria_list=[HasComponent(Position)], proxy_components=[Position])()

update_scarfy_dec = Query.decorate(update_scarfy, Position, HasId("scarfy"))
update_scarfy_dec(query)
```

