from aiohttp import ClientSession

from ..battle.choices import (
    DefaultChoice,
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
    """
    Picks the first legal option every time.

    Best used for testing connections, as this is even less sophisticated than random choices.
    """

    async def team_choice(self, session: ClientSession, battle_state: BattleState) -> TeamOrderChoice:
        """
        Simply returns default choice, which will signify picking the first legal option.

        This is the equivalent to picking /choose default on showdown or running out of time in VGC
        """

        # TODO: Implement random sub-team ordering (ex: of the 6 options, pick 4)

        assert is_bearable(
            battle_state.battle_choice, TeamChoice
        ), f"Expected to receive a TeamChoice to decide from but got: {type(battle_state.battle_choice)} instead!"

        team_order = battle_state.battle_choice.team_order

        print(team_order)

        random.shuffle(team_order)

        return TeamChoice(team_order=team_order)

    async def move_choice(self, session: ClientSession, battle_state: BattleState) -> MoveDecisionChoice:
        """
        Simply returns default choice, which will signify picking the first legal option.

        This is the equivalent to picking /choose default on showdown or running out of time in VGC
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
        """
        Simply returns default choice, which will signify picking the first legal option.

        This is the equivalent to picking /choose default on showdown or running out of time in VGC
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


class Bronius(RandomSage):
    """
    Sage-named version of the RandomSage class.

    Cool kids use this instead of RandomSage
    """
