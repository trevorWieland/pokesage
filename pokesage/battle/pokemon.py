from typing import Dict, List, Literal, Optional, Union

from poketypes.dex import (
    DexAbility,
    DexCondition,
    DexGen,
    DexItem,
    DexMove,
    DexMoveCategory,
    DexNature,
    DexPokemon,
    DexStat,
    DexStatus,
    DexType,
    DexWeather,
)
from pydantic import BaseModel, Field


class StatBlock(BaseModel):
    """"""

    min_attack: Optional[int] = None
    min_defence: Optional[int] = None
    min_spattack: Optional[int] = None
    min_spdefence: Optional[int] = None
    min_speed: Optional[int] = None
    min_hp: Optional[int] = None

    max_attack: Optional[int] = None
    max_defence: Optional[int] = None
    max_spattack: Optional[int] = None
    max_spdefence: Optional[int] = None
    max_speed: Optional[int] = None
    max_hp: Optional[int] = None


class BoostBlock(BaseModel):
    """"""

    attack: int = 0
    defence: int = 0
    spattack: int = 0
    spdefence: int = 0
    speed: int = 0

    accuracy: int = 0
    evasion: int = 0


class BattleMove(BaseModel):
    """"""

    name: DexMove.ValueType = Field(..., description="The move")
    probability: float = Field(1.0, description="The probability that this pokemon has this move.")

    use_count: int = Field(..., description="The number of times this move has been seen")


class BattleAbility(BaseModel):
    """"""

    name: DexAbility.ValueType = Field(..., description="The ability")
    probability: float = Field(1.0, description="The probability that this pokemon has this ability.")


class BattleItem(BaseModel):
    """"""

    name: DexItem.ValueType = Field(..., description="The item")
    probability: float = Field(1.0, description="The probability that this pokemon is holding this item.")


class BattlePokemon(BaseModel):
    """ """

    species: DexPokemon.ValueType = Field(..., description="The species of the pokemon")
    base_species: DexPokemon.ValueType = Field(..., description="The base species of the pokemon")
    identifier: Optional[str] = Field(
        None,
        description="A unique identifier for this pokemon. If we don't know the identifier yet, put None",
    )

    level: int = Field(100, description="The level of the pokemon")
    gender: Optional[Literal["M", "F"]] = Field(None, description="The gender of this pokemon")

    hp_type: Literal["exact", "fraction"] = Field(
        "fraction",
        description="Whether the max_hp and cur_hp fields are fractional out of 100 or exact.",
    )
    max_hp: Optional[int] = Field(
        None,
        description="The maximum health of the pokemon. If hp_type set to fractional, will always be 100",
    )
    cur_hp: Optional[int] = Field(
        None,
        description="The current health of the pokemon. If hp_type set to fractional, will be percentage",
    )

    slot: Optional[str] = Field(
        None,
        description="Which slot (if any) the pokemon is currently in",
        max_length=1,
        min_length=1,
        pattern=r"[abc]",
    )

    active: bool = Field(False, description="Whether the current pokemon is active or not")

    stats: StatBlock = Field(
        StatBlock(),
        description="The min-max stat block of the pokemon. If you know the exact stats, min=max",
    )
    boosts: BoostBlock = Field(StatBlock(), description="The current stat boosts of the pokemon.")

    has_item: Optional[bool] = Field(
        None,
        description="Whether the pokemon is holding an item or not. None if unknown",
    )
    possible_items: List[BattleItem] = Field([], description="The list of possible items that the pokemon is holding")

    possible_abilities: List[BattleAbility] = Field([], description="The list of possible abilities of this pokemon")
    overwritten_ability: Optional[DexAbility.ValueType] = Field(
        None,
        description="If this pokemon's ability has been overwritten, which ability does it now have?",
    )

    moveset: List[BattleMove] = Field(
        [],
        description="The list of moves this pokemon has. If doing things probablistically, this can exceed 4!",
    )

    status: Optional[DexStatus.ValueType] = Field(None, description="The current status this pokemon is dealing with")
    conditions: List[DexCondition.ValueType] = Field(
        [], description="The list of current conditions this pokemon is dealing with"
    )

    tera_type: Optional[DexType.ValueType] = Field(None, description="The teratype of this pokemon")

    is_tera: bool = Field(False, description="Whether the pokemon is currently teratyped")
    is_mega: bool = Field(False, description="Whether the pokemon is currently mega-evolved")
    is_dynamax: bool = Field(False, description="Whether the pokemon is currently dynamaxed")
