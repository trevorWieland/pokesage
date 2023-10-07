from pydantic import BaseModel, Field


class MoveChoice(BaseModel):
    """
    Data Model representing a single move option for a pokemon.

    Contains information about move, target, and any extra move actions
    """


class SwitchChoice(BaseModel):
    """
    Data Model representing a switch-out option for a pokemon.

    Contains information about target switch slot number
    """


class ItemChoice(BaseModel):
    """
    Data Model representing a item-use option for a pokemon.

    Contains information about target and which item to use.

    Unused for showdown. Reserved for future emulator interaction
    """
