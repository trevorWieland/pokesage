from pydantic import BaseModel, Field


class BattleState(BaseModel):
    """
    Representing the current state of the field in a given pokemon battle.

    Built to support singles, doubles, or triples gametypes
    """
