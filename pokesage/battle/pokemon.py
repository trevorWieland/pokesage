"""Pydantic BaseModels for Battling Pokemon.

Note that these BaseModels represent a specific instance of a Pokemon as it is in a battle. This is in contrast to the
DexPokemon class, which is an Enum that represents a specific species of Pokemon, and to the PokedexPokemon class,
which is a BaseModel that represents traits of a whole species of Pokemon.
"""

from typing import List, Literal, Optional

from poketypes.dex import (
    DexAbility,
    DexCondition,
    DexItem,
    DexMove,
    DexPokemon,
    DexStatus,
    DexType,
)
from pydantic import BaseModel, Field


class StatBlock(BaseModel):
    """BaseModel for representing the min-max stats of a pokemon.

    Note:
        If you know the exact stat of a pokemon, min=max.

    Attributes:
        min_attack: The minimum attack of the pokemon
        min_defence: The minimum defence of the pokemon
        min_spattack: The minimum special attack of the pokemon
        min_spdefence: The minimum special defence of the pokemon
        min_speed: The minimum speed of the pokemon
        min_hp: The minimum hp of the pokemon
        max_attack: The maximum attack of the pokemon
        max_defence: The maximum defence of the pokemon
        max_spattack: The maximum special attack of the pokemon
        max_spdefence: The maximum special defence of the pokemon
        max_speed: The maximum speed of the pokemon
        max_hp: The maximum hp of the pokemon
    """

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
    """BaseModel for representing the current stat boosts of a pokemon.

    Attributes:
        attack: The current attack boost of the pokemon
        defence: The current defence boost of the pokemon
        spattack: The current special attack boost of the pokemon
        spdefence: The current special defence boost of the pokemon
        speed: The current speed boost of the pokemon
        accuracy: The current accuracy boost of the pokemon
        evasion: The current evasion boost of the pokemon
    """

    attack: int = 0
    defence: int = 0
    spattack: int = 0
    spdefence: int = 0
    speed: int = 0

    accuracy: int = 0
    evasion: int = 0


class BattleMove(BaseModel):
    """BaseModel for representing a move that a pokemon potentially has.

    Note:
        This class is meant to be used in a list of possible moves, not necessarily as a single move. This is because
        we may not know which moves the pokemon has, but want to be able to encode information about what moves are
        possible. Especially since we may be able to eliminate some moves as impossible, even if we still don't know
        which moves the pokemon has.

    Attributes:
        name: The move as a DexMove
        probability: The probability that this pokemon has this move.
    """

    name: DexMove.ValueType = Field(..., description="The move")
    probability: float = Field(1.0, description="The probability that this pokemon has this move.")

    use_count: int = Field(..., description="The number of times this move has been seen")


class BattleAbility(BaseModel):
    """BaseModel for representing an ability that a pokemon potentially has.

    Note:
        This class is meant to be used in a list of possible abilities, not necessarily as a single ability. This is
        because we may not know which ability the pokemon has, but want to be able to encode information about what
        abilities are possible. Especially since we may be able to eliminate some abilities as impossible, even if we
        still don't know which ability the pokemon has.

    Attributes:
        name: The ability as a DexAbility
        probability: The probability that this pokemon has this ability.
    """

    name: DexAbility.ValueType = Field(..., description="The ability")
    probability: float = Field(1.0, description="The probability that this pokemon has this ability.")


class BattleItem(BaseModel):
    """BaseModel for representing an item that a pokemon is potentially holding.

    Note:
        This class is meant to be used in a list of possible items, not necessarily as a single item. This is because
        we may not know which item the pokemon is holding, but want to be able to encode information about what items
        are possible.

    Attributes:
        name: The item as a DexItem
        probability: The probability that this pokemon is holding this item.
    """

    name: DexItem.ValueType = Field(..., description="The item")
    probability: float = Field(1.0, description="The probability that this pokemon is holding this item.")


class BattlePokemon(BaseModel):
    """BaseModel for representing a pokemon in a battle.

    Tip:
        In contrast to DexPokemon and PokedexPokemon from poketypes, this class is meant to represent a specific
        instance of a pokemon as it is in a battle.

    Attributes:
        player_id: A unique identifier for the player that controls this pokemon
        species: The species of the pokemon
        base_species: The base species of the pokemon
        nickname: The nickname of this pokemon. If we don't know the nickname yet, put None
        level: The level of the pokemon
        gender: The gender of this pokemon
        hp_type: Whether the max_hp and cur_hp fields are fractional out of 100 or exact.
        max_hp: The maximum health of the pokemon. If hp_type set to fractional, will always be 100
        cur_hp: The current health of the pokemon. If hp_type set to fractional, will be percentage
        team_pos: Which team-position the pokemon is currently in
        slot: Which slot (if any) the pokemon is currently in
        active: Whether the current pokemon is active or not
        stats: The min-max stat block of the pokemon. If you know the exact stats, min=max
        boosts: The current stat boosts of the pokemon.
        has_item: Whether the pokemon is holding an item or not. None if unknown
        possible_items: The list of possible items that the pokemon is holding
        possible_abilities: The list of possible abilities of this pokemon
        overwritten_ability: If this pokemon's ability has been overwritten, which ability does it now have?
        moveset: The list of moves this pokemon has. If doing things probablistically, this can exceed 4!
        status: The current status this pokemon is dealing with
        conditions: The list of current conditions this pokemon is dealing with
        tera_type: The teratype of this pokemon
        is_tera: Whether the pokemon is currently teratyped
        is_mega: Whether the pokemon is currently mega-evolved
        is_dynamax: Whether the pokemon is currently dynamaxed
        is_reviving: Revival Blessing mechanic support
    """

    player_id: str = Field(..., description="A unique identifier for the player that controls this pokemon")

    species: DexPokemon.ValueType = Field(..., description="The species of the pokemon")
    base_species: DexPokemon.ValueType = Field(..., description="The base species of the pokemon")
    nickname: Optional[str] = Field(
        None,
        description="The nickname of this pokemon. If we don't know the nickname yet, put None",
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

    team_pos: Optional[int] = Field(None, description="Which team-position the pokemon is currently in")
    slot: Optional[int] = Field(None, description="Which slot (if any) the pokemon is currently in", ge=1, le=3)

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

    is_reviving: bool = Field(False, description="Revival Blessing mechanic support")

    def to_id(self) -> str:
        """Extract an id for this pokemon based on currently known information.

        When a player has multiple mostly-identical pokemon (basespecies, forme, level, gender, nickname) this breaks

        Returns:
            str: An id for this pokemon
        """
        id_str = f"{self.player_id}_{self.species}_{self.level}_{self.gender}_{self.nickname}"

        return id_str

    def to_base_id(self) -> str:
        """Extract an id for this pokemon based on currently known base-level information.

        When a player has multiple partially-identical pokemon (basespecies, level, gender) this breaks

        Returns:
            str: An id for this pokemon
        """
        id_str = f"{self.player_id}_{self.base_species}_{self.level}_{self.gender}_None"

        return id_str
