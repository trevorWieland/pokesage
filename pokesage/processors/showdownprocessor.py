from beartype.typing import Optional
from copy import deepcopy
from poketypes.dex import clean_forme
from poketypes.showdown.battlemessage import *

from ..battle import Battle, BattleAbility, BattleItem, BattleMove, BattlePokemon, BattleState, BoostBlock, StatBlock
from ..battle.choices import MoveChoice, PassChoice, SwitchChoice, TeamChoice, AnyChoice
from .abstractprocessor import Processor, ProgressState


class ShowdownProcessor(Processor):
    """
    Processor class for showdown-style messages. Built to work for showdown-style battle messages exclusively

    This class on its own only provides the framework to process the battle. You should then extend this class
    to actually implement battle state processing. As is, it will provide the minimal request-handling to provide
    valid actions. Almost no other details will be available in the battle state if you use this!
    """

    async def process_action(self, action: AnyChoice, action_str: str) -> None:
        """
        Takes the action given by the sage and adds it to the log

        Also duplicates the battle_state so we save a copy of the state previous to the decision
        """

        self.log.append(action_str)
        self.battle.battle_actions.append(action)
        self.battle.battle_states.append(deepcopy(self.battle.battle_states[-1]))

    async def process_message(self, message_str: str) -> ProgressState:
        """
        This function shouild process the given message and return a ProgressState accordingly.

        Remember, everything that you want to keep should be stored in self.battle / a state inside self.battle.battle_states!
        self.log should only be used for troubleshooting measures, or other logging purposes
        """

        bm = BattleMessage.from_message(message_str)

        try:
            progress_state = await self.process_bm(bm)
        except Exception as e:
            print("Log so far:")
            for m in self.log:
                print(m)
            print()
            print("Current Battle State:")
            print(self.battle.battle_states[-1].model_dump_json(indent=4))
            print()
            print("Message that caused error:")
            print(bm.BATTLE_MESSAGE)
            print()
            raise e

        return progress_state

    async def preprocess_bm(self, bm: BattleMessage) -> Optional[ProgressState]:
        """
        A function to hook into the battle message processing flow.
        This will run *before* the battle message is processed by its specific method

        If the function returns a ProgressState, we will *SKIP* the remaining processing
        """

        self.log.append(bm.BATTLE_MESSAGE)

    async def postprocess_bm(self, bm: BattleMessage) -> Optional[ProgressState]:
        """
        A function to hook into the battle message processing flow.
        This will run *after* the battle message is processed by its specific method

        If the function returns a ProgressState, it will overwrite the original ProgressState
        """

    async def process_bm(self, bm: BattleMessage) -> ProgressState:
        """
        The main processing flow for Battle Messages.

        Flow:
        - preprocess_bm -> If not None, break and return result
        - processbm_{BMTYPE} runs for the specific battle message type
        - postprocess_bm -> If not None, result overrides previous progress state result

        In subclasses, you shouldn't need to override this function, instead you would override individual
        process_bm_{BMTYPE} functions for specific feature extraction, or the pre/post process functions

        The returned ProgressState will be acted on, so make sure that if the server is expecting an action,
        you return the correct corresponding ProgressState for the expected action.
        """

        progress_state = await self.preprocess_bm(bm)

        if progress_state is not None:
            return progress_state

        if bm.BMTYPE == BMType.player:
            await self.processbm_player(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.teamsize:
            await self.processbm_teamsize(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.gametype:
            await self.processbm_gametype(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.gen:
            await self.processbm_gen(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.tier:
            await self.processbm_tier(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.rated:
            await self.processbm_rated(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.rule:
            await self.processbm_rule(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.clearpoke:
            await self.processbm_clearpoke(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.poke:
            await self.processbm_poke(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.start:
            await self.processbm_start(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.teampreview:
            await self.processbm_teampreview(bm)
            progress_state = ProgressState.TEAM_ORDER
        elif bm.BMTYPE == BMType.empty:
            await self.processbm_empty(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.request:
            await self.processbm_request(bm)

            bm: BattleMessage_request = bm

            if bm.REQUEST_TYPE == "TEAMPREVIEW":
                progress_state = ProgressState.NO_ACTION
            elif bm.REQUEST_TYPE == "ACTIVE":
                progress_state = ProgressState.NO_ACTION
            elif bm.REQUEST_TYPE == "FORCESWITCH":
                progress_state = ProgressState.SWITCH
            elif bm.REQUEST_TYPE == "WAIT":
                progress_state = ProgressState.NO_ACTION
            else:
                progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.inactive:
            await self.processbm_inactive(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.inactiveoff:
            await self.processbm_inactiveoff(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.upkeep:
            await self.processbm_upkeep(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.turn:
            await self.processbm_turn(bm)
            progress_state = ProgressState.MOVE
        elif bm.BMTYPE == BMType.win:
            await self.processbm_win(bm)
            progress_state = ProgressState.GAME_END
        elif bm.BMTYPE == BMType.tie:
            await self.processbm_tie(bm)
            progress_state = ProgressState.GAME_END
        elif bm.BMTYPE == BMType.expire:
            await self.processbm_expire(bm)
            progress_state = ProgressState.GAME_END
        elif bm.BMTYPE == BMType.t:
            await self.processbm_t(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.move:
            await self.processbm_move(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.switch:
            await self.processbm_switch(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.drag:
            await self.processbm_drag(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.detailschange:
            await self.processbm_detailschange(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.replace:
            await self.processbm_replace(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.swap:
            await self.processbm_swap(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.cant:
            await self.processbm_cant(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.faint:
            await self.processbm_faint(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.fail:
            await self.processbm_fail(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.block:
            await self.processbm_block(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.notarget:
            await self.processbm_notarget(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.miss:
            await self.processbm_miss(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.damage:
            await self.processbm_damage(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.heal:
            await self.processbm_heal(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.sethp:
            await self.processbm_sethp(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.status:
            await self.processbm_status(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.curestatus:
            await self.processbm_curestatus(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.cureteam:
            await self.processbm_cureteam(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.boost:
            await self.processbm_boost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.unboost:
            await self.processbm_unboost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.setboost:
            await self.processbm_setboost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.swapboost:
            await self.processbm_swapboost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.invertboost:
            await self.processbm_invertboost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.clearboost:
            await self.processbm_clearboost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.clearallboost:
            await self.processbm_clearallboost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.clearpositiveboost:
            await self.processbm_clearpositiveboost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.clearnegativeboost:
            await self.processbm_clearnegativeboost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.copyboost:
            await self.processbm_copyboost(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.weather:
            await self.processbm_weather(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.fieldstart:
            await self.processbm_fieldstart(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.fieldend:
            await self.processbm_fieldend(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.terastallize:
            await self.processbm_terastallize(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.fieldactivate:
            await self.processbm_fieldactivate(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.sidestart:
            await self.processbm_sidestart(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.sideend:
            await self.processbm_sideend(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.swapsideconditions:
            await self.processbm_swapsideconditions(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.volstart:
            await self.processbm_volstart(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.volend:
            await self.processbm_volend(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.crit:
            await self.processbm_crit(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.supereffective:
            await self.processbm_supereffective(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.resisted:
            await self.processbm_resisted(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.immune:
            await self.processbm_immune(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.item:
            await self.processbm_item(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.enditem:
            await self.processbm_enditem(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.ability:
            await self.processbm_ability(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.endability:
            await self.processbm_endability(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.transform:
            await self.processbm_transform(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.mega:
            await self.processbm_mega(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.primal:
            await self.processbm_primal(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.burst:
            await self.processbm_burst(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.zpower:
            await self.processbm_zpower(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.zbroken:
            await self.processbm_zbroken(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.activate:
            await self.processbm_activate(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.hint:
            await self.processbm_hint(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.center:
            await self.processbm_center(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.message:
            await self.processbm_message(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.combine:
            await self.processbm_combine(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.waiting:
            await self.processbm_waiting(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.prepare:
            await self.processbm_prepare(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.mustrecharge:
            await self.processbm_mustrecharge(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.nothing:
            await self.processbm_nothing(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.hitcount:
            await self.processbm_hitcount(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.singlemove:
            await self.processbm_singlemove(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.singleturn:
            await self.processbm_singleturn(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.formechange:
            await self.processbm_formechange(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.error:
            await self.processbm_error(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.bigerror:
            await self.processbm_bigerror(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.unknown:
            await self.processbm_unknown(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.init:
            await self.processbm_init(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.title:
            await self.processbm_title(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.join:
            await self.processbm_join(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.leave:
            await self.processbm_leave(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.raw:
            await self.processbm_raw(bm)
            progress_state = ProgressState.NO_ACTION
        elif bm.BMTYPE == BMType.anim:
            await self.processbm_anim(bm)
            progress_state = ProgressState.NO_ACTION
        else:
            print(f"BattleStateProcessor does not have a handler for BMType: {bm.BMTYPE}!")
            progress_state = ProgressState.NO_ACTION

        other_state = await self.postprocess_bm(bm)

        if other_state is not None:
            progress_state = other_state

        return progress_state

    async def processbm_player(self, bm: BattleMessage_player) -> None:
        """
        Processes this message to update the current battle state
        """

        if self.battle.player_name == bm.USERNAME:
            self.battle.player_id = bm.PLAYER
            self.battle.player_rating = bm.RATING
        else:
            self.battle.opponent_name = bm.USERNAME
            self.battle.opponent_id = bm.PLAYER
            self.battle.opponent_rating = bm.RATING

    async def processbm_teamsize(self, bm: BattleMessage_teamsize) -> None:
        """
        Processes this message to update the current battle state
        """

        if self.battle.player_id == bm.PLAYER:
            self.battle.player_team_size = bm.NUMBER
        else:
            self.battle.opponent_team_size = bm.NUMBER

    async def processbm_gametype(self, bm: BattleMessage_gametype) -> None:
        """
        Processes this message to update the current battle state
        """

        self.battle.gametype = bm.GAMETYPE

        if bm.GAMETYPE == "singles":
            self.battle.battle_states[-1].player_slots = {1: None}
            self.battle.battle_states[-1].opponent_slots = {1: None}
        elif bm.GAMETYPE == "doubles":
            self.battle.battle_states[-1].player_slots = {1: None, 2: None}
            self.battle.battle_states[-1].opponent_slots = {1: None, 2: None}
        elif bm.GAMETYPE == "triples":
            self.battle.battle_states[-1].player_slots = {1: None, 2: None, 3: None}
            self.battle.battle_states[-1].opponent_slots = {1: None, 2: None, 3: None}

    async def processbm_gen(self, bm: BattleMessage_gen) -> None:
        """
        Processes this message to update the current battle state
        """

        self.battle.gen = bm.GENNUM

    async def processbm_tier(self, bm: BattleMessage_tier) -> None:
        """
        Processes this message to update the current battle state
        """

        self.battle.format = bm.FORMATNAME.lower().replace("[", "").replace("]", "").replace(" ", "")

    async def processbm_rated(self, bm: BattleMessage_rated) -> None:
        """
        Processes this message to update the current battle state
        """

        self.battle.rated = True

    async def processbm_rule(self, bm: BattleMessage_rule) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_clearpoke(self, bm: BattleMessage_clearpoke) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_poke(self, bm: BattleMessage_poke) -> None:
        """
        Processes this message to update the current battle state
        """

        if bm.PLAYER == self.battle.player_id:
            # We already get better information from the request object, so we don't care about this for us
            return

        # In showdown we first see opponent pokemon base-species details, without knowing what the exact forme is
        # So later, when checking, check for a match on species first, then on base-species.
        # Once base-species finds a match, set species accordingly
        poke = BattlePokemon(
            player_id=bm.PLAYER,
            species=bm.SPECIES,
            base_species=clean_forme(bm.SPECIES),
            nickname=None,
            level=bm.LEVEL,
            gender=bm.GENDER,
            tera_type=bm.TERA,
            has_item=bm.HAS_ITEM,
        )

        temp_id = poke.to_base_id()

        self.battle.battle_states[-1].opponent_team[temp_id] = poke

    async def processbm_start(self, bm: BattleMessage_start) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_teampreview(self, bm: BattleMessage_teampreview) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_empty(self, bm: BattleMessage_empty) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_request(self, bm: BattleMessage_request) -> None:
        """
        Processes this message to update the current battle state
        """

        assert self.battle.player_name == bm.USERNAME

        assert (self.battle.player_id == bm.PLAYER) or (self.battle.player_id is None)

        if self.battle.player_id is None:
            self.battle.player_id = bm.PLAYER

        # Set our choices back to empty so we're ready to add details
        current_state = self.battle.battle_states[-1]
        current_state.battle_choice = None

        # Process all pokemon in the `side` data
        for e, bm_poke in enumerate(bm.POKEMON):
            # TODO: Process Reviving/Commanding mechanics properly (Don't know what they're for yet)

            if len(current_state.player_team) == e:
                # This means we have never initialized this pokemon before, so we need to do so
                s_block = StatBlock(
                    min_attack=bm_poke.STATS["atk"],
                    max_attack=bm_poke.STATS["atk"],
                    min_defence=bm_poke.STATS["def"],
                    max_defence=bm_poke.STATS["def"],
                    min_spattack=bm_poke.STATS["spa"],
                    max_apattack=bm_poke.STATS["spa"],
                    min_spdefence=bm_poke.STATS["spd"],
                    max_spdefence=bm_poke.STATS["spd"],
                    min_speed=bm_poke.STATS["spe"],
                    max_speed=bm_poke.STATS["spe"],
                    min_hp=bm_poke.MAX_HP,
                    max_hp=bm_poke.MAX_HP,
                )
                poke = BattlePokemon(
                    player_id=bm.PLAYER,
                    species=bm_poke.SPECIES,
                    base_species=clean_forme(bm_poke.SPECIES),
                    nickname=bm_poke.IDENT.IDENTITY,
                    level=bm_poke.LEVEL,
                    gender=bm_poke.GENDER,
                    hp_type="exact",
                    max_hp=bm_poke.MAX_HP,
                    cur_hp=bm_poke.CUR_HP,
                    team_pos=e + 1,
                    stats=s_block,
                    has_item=bm_poke.ITEM is not None,
                    possible_items=[] if bm_poke.ITEM is None else [BattleItem(name=bm_poke.ITEM, probability=1.0)],
                    possible_abilities=[BattleAbility(name=bm_poke.BASE_ABILITY, probability=1.0)],
                    overwritten_ability=None if (bm_poke.ABILITY == bm_poke.BASE_ABILITY) else bm_poke.ABILITY,
                    moveset=[BattleMove(name=m, probability=1.0, use_count=0) for m in bm_poke.MOVES],
                    status=bm_poke.STATUS,
                    tera_type=bm_poke.TERATYPE,
                    is_tera=bm_poke.TERASTALLIZED is not None,
                    active=bm_poke.ACTIVE,
                )

                current_state.player_team[poke.to_id()] = poke
            else:
                poke_id = f"{bm.PLAYER}_{bm_poke.SPECIES}_{bm_poke.LEVEL}_{bm_poke.GENDER}_{bm_poke.IDENT.IDENTITY}"
                poke = current_state.player_team[poke_id]

                poke.max_hp = bm_poke.MAX_HP if bm_poke.MAX_HP is not None else poke.max_hp
                poke.cur_hp = bm_poke.CUR_HP

                poke.has_item = bm_poke.ITEM is not None
                poke.possible_items = [] if bm_poke.ITEM is None else [BattleItem(name=bm_poke.ITEM, probability=1.0)]

                poke.possible_abilities = (
                    [BattleAbility(name=bm_poke.BASE_ABILITY, probability=1.0)]
                    if len(poke.possible_abilities) == 0
                    else poke.possible_abilities
                )
                poke.overwritten_ability = (
                    None
                    if (bm_poke.ABILITY == bm_poke.BASE_ABILITY or bm_poke.ABILITY == poke.possible_abilities[0].name)
                    else bm_poke.ABILITY
                )

                poke.moveset = (
                    [BattleMove(name=m, probability=1.0, use_count=0) for m in bm_poke.MOVES]
                    if len(poke.moveset) == 0
                    else poke.moveset
                )

                poke.status = bm_poke.STATUS

                poke.tera_type = bm_poke.TERATYPE
                poke.is_tera = bm_poke.TERASTALLIZED is not None

                poke.team_pos = e + 1

                poke.active = bm_poke.ACTIVE

                poke.is_reviving = bm_poke.REVIVING

                current_state.player_team[poke_id] = poke

        if bm.REQUEST_TYPE == "WAIT":
            # In this case there is no action to be made, so we just set the state and move on
            self.battle.battle_states[-1] = current_state
            return

        if bm.REQUEST_TYPE == "TEAMPREVIEW":
            # In this case we have a teamchoice decision to make, though unlike other choices where we calculate every
            # option ahead of time for the player, here we just send a sorted list of team slots.
            # No point in returning a list of every possible teamchoice permutation
            current_state.battle_choice = TeamChoice(team_order=list(range(1, len(current_state.player_team) + 1)))

            self.battle.battle_states[-1] = current_state
            return

        # Process the active pokemon
        switch_options = [
            SwitchChoice(slot=p.team_pos)
            for p in current_state.player_team.values()
            if (p.status != DexStatus.STATUS_FNT and not p.active)
        ]
        revive_options = [
            SwitchChoice(slot=p.team_pos)
            for p in current_state.player_team.values()
            if (p.status == DexStatus.STATUS_FNT and not p.active)
        ]

        if bm.REQUEST_TYPE == "FORCESWITCH":
            # If the request type is a forceswitch, then we have already identified every option the player has

            choices = []
            for i in range(self.battle.slot_length()):
                if bm.FORCESWITCH_SLOTS[i]:
                    choices.append(switch_options)
                else:
                    choices.append(PassChoice())

            current_state.battle_choice = choices

            self.battle.battle_states[-1] = current_state
            return

        assert bm.REQUEST_TYPE == "ACTIVE"

        choices = []
        for i in range(self.battle.slot_length()):
            if len(bm.ACTIVE_OPTIONS) <= i:
                # This implies we have less alive pokemon than slots, so we fill the remaining parts with pass choices
                choices.append(PassChoice())
                continue

            # This has extra details about moves and options for our pokemon in the active slots
            # We use this information to build current_state.move_choices / switch_choices
            ao = bm.ACTIVE_OPTIONS[i]

            # Process all the moves that are open to us
            move_options = []
            for move_num, m_data in enumerate(ao.MOVES):
                if m_data.DISABLED or m_data.CUR_PP == 0:
                    continue

                # Since the request comes before we see any switches, we have to process valid targets later in `turn`
                mo = MoveChoice(move_number=move_num + 1)
                move_options.append(mo)

                if ao.CAN_TERA:
                    mo = MoveChoice(move_number=move_num + 1, tera=True)
                    move_options.append(mo)

                if ao.CAN_MEGA:
                    mo = MoveChoice(move_number=move_num + 1, mega=True)
                    move_options.append(mo)

                if ao.CAN_DYNA:
                    mo = MoveChoice(move_number=move_num + 1, dyna=True)
                    move_options.append(mo)

                if ao.CAN_ZMOVE:
                    mo = MoveChoice(move_number=move_num + 1, zmove=True)
                    move_options.append(mo)

            if not ao.TRAPPED:
                slot_choices = move_options + switch_options
            else:
                slot_choices = move_options

            choices.append(slot_choices)

        current_state.battle_choice = choices
        self.battle.battle_states[-1] = current_state

    async def processbm_inactive(self, bm: BattleMessage_inactive) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_inactiveoff(self, bm: BattleMessage_inactiveoff) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_upkeep(self, bm: BattleMessage_upkeep) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_turn(self, bm: BattleMessage_turn) -> None:
        """
        Processes this message to update the current battle state
        """

        self.battle.turn = bm.NUMBER

        # We need to process valid targets here, as this will happen `after` any switches are made
        # TODO: process move target options

    async def processbm_win(self, bm: BattleMessage_win) -> None:
        """
        Processes this message to update the current battle state
        """

        self.battle.player_victory = bm.USERNAME == self.battle.player_name

    async def processbm_tie(self, bm: BattleMessage_tie) -> None:
        """
        Processes this message to update the current battle state
        """

        self.battle.player_victory = False

    async def processbm_expire(self, bm: BattleMessage_expire) -> None:
        """
        Processes this message to update the current battle state
        """

        self.battle.player_victory = False

    async def processbm_t(self, bm: BattleMessage_t) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_move(self, bm: BattleMessage_move) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_switch(self, bm: BattleMessage_switch) -> None:
        """
        Processes this message to update the current battle state
        """

        # TODO: Figure out a way of supporting duplicate base species w/ different nicknames
        ## Maybe a numbering system based on appearance?
        ## Current setup breaks when a pokemon changes forme back to a basespecies
        ## Current setup also relies on perfect accounting of slot information

        full_ident = f"{bm.POKEMON.PLAYER}_{bm.SPECIES}_{bm.LEVEL}_{bm.GENDER}_{bm.POKEMON.IDENTITY}"
        base_ident = f"{bm.POKEMON.PLAYER}_{clean_forme(bm.SPECIES)}_{bm.LEVEL}_{bm.GENDER}_None"

        slot = bm.POKEMON.SLOT
        assert slot is not None

        slot = "abc".find(slot) + 1

        current_state = self.battle.battle_states[-1]

        if full_ident in current_state.player_team.keys():
            # Process this as a player slot switch
            if current_state.player_slots[slot] is not None:
                old_poke_id = current_state.player_slots[slot]
                current_state.player_team[old_poke_id].slot = None
                current_state.player_team[old_poke_id].active = False

            current_state.player_team[full_ident].slot = slot
            current_state.player_team[full_ident].active = True
            current_state.player_slots[slot] = full_ident
        elif full_ident in current_state.opponent_team.keys():
            # Process this as an opponent slot switch
            # This also means this is a pokemon we have seen before from the opponent
            if current_state.opponent_slots[slot] is not None:
                old_poke_id = current_state.opponent_slots[slot]
                current_state.opponent_team[old_poke_id].slot = None
                current_state.opponent_team[old_poke_id].active = False

            current_state.opponent_team[full_ident].slot = slot
            current_state.opponent_team[full_ident].active = True
            current_state.opponent_slots[slot] = full_ident
        elif base_ident in current_state.opponent_team.keys():
            # Process this as an opponent slot switch
            # This also means this is a pokemon we have not yet seen before from the opponent
            poke = current_state.opponent_team.pop(base_ident)
            poke.species = bm.SPECIES
            poke.nickname = bm.POKEMON.IDENTITY
            current_state.opponent_team[full_ident] = poke

            if current_state.opponent_slots[slot] is not None:
                old_poke_id = current_state.opponent_slots[slot]
                current_state.opponent_team[old_poke_id].slot = None
                current_state.opponent_team[old_poke_id].active = False

            current_state.opponent_team[full_ident].slot = slot
            current_state.opponent_team[full_ident].active = True
            current_state.opponent_slots[slot] = full_ident
        else:
            # In this case, we must be playing without teampreview, since we haven't seen this before
            # TODO: assert that teampreview is part of this format for bugtracking reasons

            assert (
                bm.POKEMON.PLAYER == self.battle.opponent_id
            ), f"Previously unindentified player pokemon: {full_ident}"

            poke = BattlePokemon(
                player_id=bm.POKEMON.PLAYER,
                species=bm.SPECIES,
                base_species=clean_forme(bm.SPECIES),
                nickname=bm.POKEMON.IDENTITY,
                level=bm.LEVEL,
                gender=bm.GENDER,
                tera_type=bm.TERA,
            )
            current_state.opponent_team[full_ident] = poke

            # Process this as an opponent slot switch
            if current_state.opponent_slots[slot] is not None:
                old_poke_id = current_state.opponent_slots[slot]
                current_state.opponent_team[old_poke_id].slot = None
                current_state.opponent_team[old_poke_id].active = False

            current_state.opponent_team[full_ident].slot = slot
            current_state.opponent_team[full_ident].active = True
            current_state.opponent_slots[slot] = full_ident

        self.battle.battle_states[-1] = current_state

    async def processbm_drag(self, bm: BattleMessage_drag) -> None:
        """
        Processes this message to update the current battle state
        """

        full_ident = f"{bm.POKEMON.PLAYER}_{bm.SPECIES}_{bm.LEVEL}_{bm.GENDER}_{bm.POKEMON.IDENTITY}"
        base_ident = f"{bm.POKEMON.PLAYER}_{clean_forme(bm.SPECIES)}_{bm.LEVEL}_{bm.GENDER}_None"

        slot = bm.POKEMON.SLOT
        assert slot is not None

        slot = "abc".find(slot) + 1

        current_state = self.battle.battle_states[-1]

        if full_ident in current_state.player_team.keys():
            # Process this as a player slot switch
            if current_state.player_slots[slot] is not None:
                old_poke_id = current_state.player_slots[slot]
                current_state.player_team[old_poke_id].slot = None
                current_state.player_team[old_poke_id].active = False

            current_state.player_team[full_ident].slot = slot
            current_state.player_team[full_ident].active = True
            current_state.player_slots[slot] = full_ident
        elif full_ident in current_state.opponent_team.keys():
            # Process this as an opponent slot switch
            # This also means this is a pokemon we have seen before from the opponent
            if current_state.opponent_slots[slot] is not None:
                old_poke_id = current_state.opponent_slots[slot]
                current_state.opponent_team[old_poke_id].slot = None
                current_state.opponent_team[old_poke_id].active = False

            current_state.opponent_team[full_ident].slot = slot
            current_state.opponent_team[full_ident].active = True
            current_state.opponent_slots[slot] = full_ident
        elif base_ident in current_state.opponent_team.keys():
            # Process this as an opponent slot switch
            # This also means this is a pokemon we have not yet seen before from the opponent
            poke = current_state.opponent_team.pop(base_ident)
            poke.species = bm.SPECIES
            poke.nickname = bm.POKEMON.IDENTITY
            current_state.opponent_team[full_ident] = poke

            if current_state.opponent_slots[slot] is not None:
                old_poke_id = current_state.opponent_slots[slot]
                current_state.opponent_team[old_poke_id].slot = None
                current_state.opponent_team[old_poke_id].active = False

            current_state.opponent_team[full_ident].slot = slot
            current_state.opponent_team[full_ident].active = True
            current_state.opponent_slots[slot] = full_ident
        else:
            # In this case, we must be playing without teampreview, since we haven't seen this before
            # TODO: assert that teampreview is part of this format for bugtracking reasons

            assert (
                bm.POKEMON.PLAYER == self.battle.opponent_id
            ), f"Previously unindentified player pokemon: {full_ident}"

            poke = BattlePokemon(
                player_id=bm.POKEMON.PLAYER,
                species=bm.SPECIES,
                base_species=clean_forme(bm.SPECIES),
                nickname=bm.POKEMON.IDENTITY,
                level=bm.LEVEL,
                gender=bm.GENDER,
                tera_type=bm.TERA,
            )
            current_state.opponent_team[full_ident] = poke

            # Process this as an opponent slot switch
            if current_state.opponent_slots[slot] is not None:
                old_poke_id = current_state.opponent_slots[slot]
                current_state.opponent_team[old_poke_id].slot = None
                current_state.opponent_team[old_poke_id].active = False

            current_state.opponent_team[full_ident].slot = slot
            current_state.opponent_team[full_ident].active = True
            current_state.opponent_slots[slot] = full_ident

        self.battle.battle_states[-1] = current_state

    async def processbm_detailschange(self, bm: BattleMessage_detailschange) -> None:
        """
        Processes this message to update the current battle state
        """

        full_ident = f"{bm.POKEMON.PLAYER}_{bm.SPECIES}_{bm.LEVEL}_{bm.GENDER}_{bm.POKEMON.IDENTITY}"

        slot = bm.POKEMON.SLOT
        assert slot is not None

        slot = "abc".find(slot) + 1

        current_state = self.battle.battle_states[-1]

        if bm.POKEMON.PLAYER == self.battle.player_id:
            # Process this as a player update
            assert current_state.player_slots[slot] is not None, "Failed to setup slots before change occured"

            old_poke_id = current_state.player_slots[slot]
            poke = current_state.player_team.pop(old_poke_id)

            poke.species = bm.SPECIES
            poke.base_species = clean_forme(bm.SPECIES)

            current_state.player_team[full_ident] = poke
            current_state.player_slots[slot] = full_ident
        else:
            # Process this as a opponent update
            assert current_state.opponent_slots[slot] is not None, "Failed to setup slots before change occured"

            old_poke_id = current_state.opponent_slots[slot]
            poke = current_state.opponent_team.pop(old_poke_id)

            poke.species = bm.SPECIES
            poke.base_species = clean_forme(bm.SPECIES)

            current_state.opponent_team[full_ident] = poke
            current_state.opponent_slots[slot] = full_ident

        self.battle.battle_states[-1] = current_state

    async def processbm_replace(self, bm: BattleMessage_replace) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_swap(self, bm: BattleMessage_swap) -> None:
        """
        Processes this message to update the current battle state
        """

        player = bm.POKEMON.PLAYER

        original_slot = bm.POKEMON.SLOT
        assert original_slot is not None

        original_slot = "abc".find(original_slot) + 1
        new_slot = bm.POSITION + 1

        current_state = self.battle.battle_states[-1]

        if player == self.battle.player_id:
            # Process this swap as a player-side swap
            assert current_state.player_slots[original_slot] is not None, "Failed to setup slots before swap occured"
            assert current_state.player_slots[new_slot] is not None, "Failed to setup slots before swap occured"

            orig_id = current_state.player_slots[original_slot]
            new_id = current_state.player_slots[new_slot]

            current_state.player_team[orig_id].slot = new_slot
            current_state.player_team[new_id].slot = original_slot

            current_state.player_slots[original_slot] = new_id
            current_state.player_slots[new_slot] = orig_id
        else:
            # Process this swap as an opponent-side swap
            assert current_state.opponent_slots[original_slot] is not None, "Failed to setup slots before swap occured"
            assert current_state.opponent_slots[new_slot] is not None, "Failed to setup slots before swap occured"

            orig_id = current_state.opponent_slots[original_slot]
            new_id = current_state.opponent_slots[new_slot]

            current_state.opponent_team[orig_id].slot = new_slot
            current_state.opponent_team[new_id].slot = original_slot

            current_state.opponent_slots[original_slot] = new_id
            current_state.opponent_slots[new_slot] = orig_id

        self.battle.battle_states[-1] = current_state

    async def processbm_cant(self, bm: BattleMessage_cant) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_faint(self, bm: BattleMessage_faint) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_fail(self, bm: BattleMessage_fail) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_block(self, bm: BattleMessage_block) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_notarget(self, bm: BattleMessage_notarget) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_miss(self, bm: BattleMessage_miss) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_damage(self, bm: BattleMessage_damage) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_heal(self, bm: BattleMessage_heal) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_sethp(self, bm: BattleMessage_sethp) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_status(self, bm: BattleMessage_status) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_curestatus(self, bm: BattleMessage_curestatus) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_cureteam(self, bm: BattleMessage_cureteam) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_boost(self, bm: BattleMessage_boost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_unboost(self, bm: BattleMessage_unboost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_setboost(self, bm: BattleMessage_setboost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_swapboost(self, bm: BattleMessage_swapboost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_invertboost(self, bm: BattleMessage_invertboost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_clearboost(self, bm: BattleMessage_clearboost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_clearallboost(self, bm: BattleMessage_clearallboost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_clearpositiveboost(self, bm: BattleMessage_clearpositiveboost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_clearnegativeboost(self, bm: BattleMessage_clearnegativeboost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_copyboost(self, bm: BattleMessage_copyboost) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_weather(self, bm: BattleMessage_weather) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_fieldstart(self, bm: BattleMessage_fieldstart) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_terastallize(self, bm: BattleMessage_terastallize) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_fieldend(self, bm: BattleMessage_fieldend) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_fieldactivate(self, bm: BattleMessage_fieldactivate) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_sidestart(self, bm: BattleMessage_sidestart) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_sideend(self, bm: BattleMessage_sideend) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_swapsideconditions(self, bm: BattleMessage_swapsideconditions) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_volstart(self, bm: BattleMessage_volstart) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_volend(self, bm: BattleMessage_volend) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_crit(self, bm: BattleMessage_crit) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_supereffective(self, bm: BattleMessage_supereffective) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_resisted(self, bm: BattleMessage_resisted) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_immune(self, bm: BattleMessage_immune) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_item(self, bm: BattleMessage_item) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_enditem(self, bm: BattleMessage_enditem) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_ability(self, bm: BattleMessage_ability) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_endability(self, bm: BattleMessage_endability) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_transform(self, bm: BattleMessage_transform) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_mega(self, bm: BattleMessage_mega) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_primal(self, bm: BattleMessage_primal) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_burst(self, bm: BattleMessage_burst) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_zpower(self, bm: BattleMessage_zpower) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_zbroken(self, bm: BattleMessage_zbroken) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_activate(self, bm: BattleMessage_activate) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_hint(self, bm: BattleMessage_hint) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_center(self, bm: BattleMessage_center) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_message(self, bm: BattleMessage_message) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_combine(self, bm: BattleMessage_combine) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_waiting(self, bm: BattleMessage_waiting) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_prepare(self, bm: BattleMessage_prepare) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_mustrecharge(self, bm: BattleMessage_mustrecharge) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_nothing(self, bm: BattleMessage_nothing) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_hitcount(self, bm: BattleMessage_hitcount) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_singlemove(self, bm: BattleMessage_singlemove) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_singleturn(self, bm: BattleMessage_singleturn) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_formechange(self, bm: BattleMessage_formechange) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_error(self, bm: BattleMessage_error) -> None:
        """
        Processes this message to update the current battle state
        """

        raise RuntimeError(f"Reached error state: {bm.MESSAGE}")

    async def processbm_bigerror(self, bm: BattleMessage_bigerror) -> None:
        """
        Processes this message to update the current battle state
        """

        raise RuntimeError(f"Reached big error state: {bm.MESSAGE}")

    async def processbm_unknown(self, bm: BattleMessage) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_init(self, bm: BattleMessage_init) -> None:
        """
        Processes this message to update the current battle state
        """

        # This signifies that the game has started, so we need to initialize our first state
        bs = BattleState(turn=1)
        self.battle.battle_states.append(bs)

    async def processbm_title(self, bm: BattleMessage_title) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_join(self, bm: BattleMessage_join) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_leave(self, bm: BattleMessage_leave) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_raw(self, bm: BattleMessage_raw) -> None:
        """
        Processes this message to update the current battle state
        """

    async def processbm_anim(self, bm: BattleMessage_anim) -> None:
        """
        Processes this message to update the current battle state
        """
