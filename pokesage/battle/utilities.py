"""Contains utility functions for the battle module."""

from poketypes.dex import DexMoveTarget
from typing import List, Literal, Dict, Optional


def get_valid_target_slots(
    source_slot: int,
    filled_slots: List[int],
    move_target: DexMoveTarget.ValueType,
    gametype: Literal["doubles", "triples"],
) -> List[int]:
    """Get a list of valid target slots for a move.

    This function will return a list of valid target slots for a move, given the source slot, the filled slots, the
    move target, and the gametype. This function does not check if the move is valid, only if the target slots are
    valid. For example, if you pass in a move that targets the user, this function will return an empty list, even
    though the move is valid. You should first use needs_target() to check if a move needs a target in the first place.

    Tip:
        This method uses Showdown-style slots, meaning that the first slot is 1, not 0, and that when targetting for a
        move, your side has negative numbers counting from -1, while the opponent's side has positive numbers counting
        from 1.

        For example, in a double battle, the field looks like this:
            >-2 -1
            > 1  2

        In a triple battle the field looks like this:
            >-3 -2 -1
            > 1  2  3

        In single battles, slot numbers are irrelevant and thus you don't need to use this function.

    Args:
        source_slot (int): The integer slot of the pokemon using the move.
        filled_slots (List[int]): A list of all the filled slots in the battle.
        move_target (DexMoveTarget.ValueType): The DexMoveTarget of the move being used.
        gametype (Literal["doubles", "triples"]): The gametype of the battle. Either "doubles" or "triples".

    Returns:
        List[int]: A list of valid target slots. Will be a subset of filled_slots.
    """
    targettable_slots: List[int] = []

    for target_slot in filled_slots:
        if can_target_slot(source_slot, target_slot, move_target, gametype):
            targettable_slots.append(target_slot)

    return targettable_slots


def needs_target(move_target: Optional[DexMoveTarget.ValueType]) -> bool:
    """Check if a move needs a target.

    Args:
        move_target (Optional[DexMoveTarget.ValueType]): The DexMoveTarget of the move being used.

    Returns:
        bool: Whether the move needs a target.
    """
    if move_target is None:
        return False

    need_dict: Dict[DexMoveTarget.ValueType, bool] = {
        DexMoveTarget.MOVETARGET_SELF: False,
        DexMoveTarget.MOVETARGET_ADJACENTALLY: True,
        DexMoveTarget.MOVETARGET_ADJACENTALLYORSELF: True,
        DexMoveTarget.MOVETARGET_ALL: False,
        DexMoveTarget.MOVETARGET_ALLADJACENT: False,
        DexMoveTarget.MOVETARGET_ALLADJACENTFOES: False,
        DexMoveTarget.MOVETARGET_ALLIES: False,
        DexMoveTarget.MOVETARGET_ALLYSIDE: False,
        DexMoveTarget.MOVETARGET_ALLYTEAM: False,
        DexMoveTarget.MOVETARGET_ANY: True,
        DexMoveTarget.MOVETARGET_FOESIDE: False,
        DexMoveTarget.MOVETARGET_NORMAL: True,
        DexMoveTarget.MOVETARGET_RANDOMNORMAL: False,
        DexMoveTarget.MOVETARGET_SCRIPTED: False,  # TODO: Need to verify what this is
        DexMoveTarget.MOVETARGET_ADJACENTFOE: True,
    }

    return need_dict[move_target]


def can_target_slot(
    source_slot: int, target_slot: int, move_target: DexMoveTarget.ValueType, gametype: Literal["doubles", "triples"]
) -> bool:
    """Check if source_slot can target target_slot with a move that targets with move_target.

    Note, since we care about targetting, this is specifically for moves that target a specific slot, not moves that
    are used without a target (like Protect, Earthquake, etc.). Thus, this function will return False for those moves.

    Tip:
        This method uses Showdown-style slots, meaning that the first slot is 1, not 0, and that when targetting for a
        move, your side has negative numbers counting from -1, while the opponent's side has positive numbers counting
        from 1.

        For example, in a double battle, the field looks like this:
            > 2  1
            >-1 -2

        In a triple battle the field looks like this:
            > 3  2  1
            >-1 -2 -3

        In a hypothetical 4v4 battle, the field looks like this:
            > 4  3  2  1
            >-1 -2 -3 -4

        In single battles, slot numbers are irrelevant and thus you don't need to use this function.

    Args:
        source_slot (int): The integer slot of the pokemon using the move.
        target_slot (int): The integer slot of the pokemon being targeted.
        move_target (DexMoveTarget.ValueType): The DexMoveTarget of the move being used.
        gametype (Literal["doubles", "triples"]): The gametype of the battle. Either "doubles" or "triples".

    Returns:
        bool: Whether the move can target the target_slot from the source_slot.

    Raises:
        RuntimeError: If the move_target is not recognized.
    """
    if not needs_target(move_target):
        return False

    max_num = 2 if gametype == "doubles" else 3

    is_self = source_slot == target_slot
    is_same_side = source_slot * target_slot > 0
    is_opposite_side = source_slot * target_slot < 0
    is_adj_ally = is_same_side and abs(source_slot - target_slot) == 1
    is_adj_foe = is_opposite_side and abs(abs(source_slot) - max_num - 1) == abs(target_slot)
    is_corner_foe = is_opposite_side and abs(abs(abs(source_slot) - max_num - 1) - abs(target_slot)) == 1
    is_adjacent = is_adj_ally or is_adj_foe

    if move_target == DexMoveTarget.MOVETARGET_ADJACENTALLY:
        return is_adj_ally
    elif move_target == DexMoveTarget.MOVETARGET_ADJACENTALLYORSELF:
        return is_adj_ally or is_self
    elif move_target == DexMoveTarget.MOVETARGET_ANY:
        return not is_self
    elif move_target == DexMoveTarget.MOVETARGET_NORMAL:
        return is_adjacent or is_corner_foe
    elif move_target == DexMoveTarget.MOVETARGET_ADJACENTFOE:
        return is_adj_foe or is_corner_foe
    else:
        raise RuntimeError(f"Unknown move target {move_target}")
