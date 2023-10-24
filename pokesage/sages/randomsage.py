"""Player Logic for making random choices in a battle.

Contains both RandomSage and Bronius, which are the same class but with different names.
This class will make random choices, including moves, switches, and team orders.
"""

from aiohttp import ClientSession

from ..battle.choices import (
    ForceSwitchChoice,
    MoveDecisionChoice,
    TeamOrderChoice,
    TeamChoice,
    PassChoice,
    SwitchChoice,
)
from ..battle.state import BattleState
from .abstractsage import AbstractSage

from beartype.door import is_bearable
import random


class RandomSage(AbstractSage):
    """Picks a random move between moves, switches, and team order.

    Best used for testing connections and choice parsing.
    """

    async def team_choice(self, session: ClientSession, battle_state: BattleState) -> TeamOrderChoice:
        """Generate a TeamOrderChoice decision, which will be used for selecting pokemon order.

        This class specifically will randomly sort the given team order.

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            battle_state (BattleState): The current battle state to make a decision from.

        Returns:
            TeamOrderChoice: A randomly sorted list for team order
        """
        # TODO: Implement random sub-team ordering (ex: of the 6 options, pick 4)

        assert is_bearable(
            battle_state.battle_choice, TeamChoice
        ), f"Expected to receive a TeamChoice to decide from but got: {type(battle_state.battle_choice)} instead!"

        team_order = battle_state.battle_choice.team_order

        random.shuffle(team_order)

        return TeamChoice(team_order=team_order)

    async def move_choice(self, session: ClientSession, battle_state: BattleState) -> MoveDecisionChoice:
        """Generate a MoveDecisionChoice decision, which will be used for typical move selection.

        This class specifically will randomly pick one option for each slot, in order from left to right.
        This means that if we randomly choose to swap slot 1 to Pokemon B, then slot 2 will not have this as an option.

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            battle_state (BattleState): The current battle state to make a decision from.

        Returns:
            MoveDecisionChoice: A randomly selected move for each slot
        """
        assert is_bearable(battle_state.battle_choice, list), "The given choices should be a list!"

        selected_choices = []
        for slot_choices in battle_state.battle_choice:
            if is_bearable(slot_choices, PassChoice):
                selected_choices.append(slot_choices)
            else:
                valid_choices = [c for c in slot_choices if (not is_bearable(c, SwitchChoice) or c not in slot_choices)]
                selected_choices.append(valid_choices[random.randint(0, len(valid_choices) - 1)])

        return selected_choices

    async def forceswitch_choice(self, session: ClientSession, battle_state: BattleState) -> ForceSwitchChoice:
        """Generate a ForceSwitchChoice decision, which will be used when needing to switch pokemon.

        This class specifically will randomly pick one option for each slot, in order from left to right.
        This means that if we randomly choose to swap slot 1 to Pokemon B, then slot 2 will not have this as an option.

        Args:
            session (ClientSession): An aiohttp session to use for making requests as needed.
            battle_state (BattleState): The current battle state to make a decision from.

        Returns:
            ForceSwitchChoice: A randomly selected switch for each slot, as needed.
        """
        assert is_bearable(battle_state.battle_choice, list), "The given choices should be a list!"

        selected_choices = []
        for slot_choices in battle_state.battle_choice:
            if is_bearable(slot_choices, PassChoice):
                selected_choices.append(slot_choices)
            else:
                valid_choices = [c for c in slot_choices if (c not in selected_choices)]

                if len(valid_choices) == 0:
                    print(slot_choices)
                    print(selected_choices)
                    print(valid_choices)

                selected_choices.append(valid_choices[random.randint(0, len(valid_choices) - 1)])

        return selected_choices


class Bronius(RandomSage):
    """Sage-named version of the RandomSage class.

    Cool kids use this instead of RandomSage.
    """
