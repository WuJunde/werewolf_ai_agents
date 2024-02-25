import re
import sys
sys.path.append("..")

from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.logs import logger
from actions import ACTIONS, InstructSpeak, Speak, Reflect, NighttimeWhispers
from actions.experience_operation import AddNewExperiences, RetrieveExperiences
from schema import RoleExperience
from metagpt.const import MESSAGE_ROUTE_TO_ALL

class BasePlayer(Role):
    def __init__(
        self,
        name: str = "PlayerXYZ",
        profile: str = "BasePlayer",
        special_action_names: list[str] = [],
        use_reflection: bool = True,
        use_experience: bool = False,
        use_memory_selection: bool = False,
        new_experience_version: str = "",
        **kwargs,
    ):
        super().__init__(name = name, profile = profile, **kwargs)
        # 通过 set_status() 更新状态。
        self.status = 0 # 0代表活着，1代表死亡

        # 技能和监听配置
        self._watch([InstructSpeak]) # 监听Moderator的指令以做行动
        special_actions = [ACTIONS[action_name] for action_name in special_action_names]
        capable_actions = [Speak] + special_actions
        self.set_actions(capable_actions) # empower role action skills
        self.special_actions = special_actions

        self.use_reflection = use_reflection
        if not self.use_reflection and use_experience:
            logger.warning("You must enable use_reflection before using experience")
            self.use_experience = False
        else:
            self.use_experience = use_experience
        self.new_experience_version = new_experience_version
        self.use_memory_selection = use_memory_selection

        self.experiences = []

        self.addresses = {name, profile}

    async def _observe(self) -> int:
        if self.status == 1:
            # The dead no longer participate in the game
            return 0

        await super()._observe()
        # Only messages sent to all ("") or to oneself (self.profile) need to go through the following _react process, 
        # The rest can be heard, no action
        self.rc.news = [msg for msg in self.rc.news if any(element in [MESSAGE_ROUTE_TO_ALL, self.profile] for element in msg.send_to) and any(element == 1 for element in msg.send_to)]
        # logger.debug(f"{self._setting}: the news cause_by {type(self.rc.news[0].cause_by)}")
        return len(self.rc.news)

    async def _think(self):
        news = self.rc.news[0]
        assert news.cause_by == InstructSpeak or news.cause_by == "actions.moderator_actions.InstructSpeak" # Do the action only when the message is the instruction from the Moderator
        if MESSAGE_ROUTE_TO_ALL in news.send_to:
            # If the scope of message reception is for all roles, make a public statement (expressing voting views is also counted as speaking)
            self.rc.todo = Speak()
        elif self.profile in news.send_to.split(","):
            # FIXME: hard code to split, restricted to "Moderator" or "Moderator, profile"
            # Moderator is encrypted to himself, meaning to perform the role's specific actions
            self.rc.todo = self.special_actions[0]()

    async def _act(self):
                
        # todo为_think时确定的，有两种情况，Speak或Protect
        #todo is set in _think, there have two cases, Speak or Protect
        todo = self.rc.todo
        logger.info(f"{self._setting}: ready to {str(todo)}")

        # 可以用这个函数获取该角色的全部记忆和最新的instruction
        # this function is used to obtain the role's whole memory and newest instruction
        memories = self.get_all_memories()
        latest_instruction = self.get_latest_instruction()
        # print("*" * 10, f"{self._setting}'s current memories: {memories}", "*" * 10)

        reflection = await Reflect().run(
            profile=self.profile, name=self.name, context=memories, latest_instruction=latest_instruction
        ) if self.use_reflection else ""

        experiences = RetrieveExperiences().run(
            query=reflection, profile=self.profile, excluded_version=self.new_experience_version
        ) if self.use_experience else ""

        # 根据自己定义的角色Action，对应地去run，run的入参可能不同
        # run following the Action of the defined role, the para of run may be different
        if isinstance(todo, Speak):
            rsp = await todo.run(
                profile=self.profile, name=self.name, context=memories,
                latest_instruction=latest_instruction, reflection=reflection, experiences=experiences)
            send_to = ""

        elif isinstance(todo, NighttimeWhispers):
            rsp = await todo.run(profile=self.profile, name=self.name, context=memories, 
                reflection=reflection, experiences=experiences)
            send_to = f"Moderator,{self.profile}" # Send Moderator a confidential message using a special skill

        msg = Message(
            content=rsp, role=self.profile, sent_from=self.name,
            cause_by=type(todo), send_from="",
            send_to=send_to
        )

        self.experiences.append(
            RoleExperience(name=self.name, profile=self.profile, reflection=reflection,
                instruction=latest_instruction, response=rsp, version=self.new_experience_version)
        )

        logger.info(f"{self._setting}: {rsp}")

        return msg

    def get_all_memories(self) -> str:
        memories = self.rc.memory.get()
        time_stamp_pattern = r'[0-9]+ \| '
        # NOTE: 除Moderator外，其他角色使用memory，只能用m.sent_from（玩家名）不能用m.role（玩家角色），因为他们不知道说话者的身份
        memories = [f"{m.sent_from}: {re.sub(time_stamp_pattern, '', m.content)}" for m in memories] # regex去掉时间戳
        memories = "\n".join(memories)
        return memories
    
    def get_latest_instruction(self) -> str:
        return self.rc.important_memory[-1].content # 角色监听着Moderator的InstructSpeak，是其重要记忆，直接获取即可

    def set_status(self, new_status):
        self.status = new_status
    
    def record_experiences(self, round_id: str, outcome: str, game_setup: str):
        experiences = [exp for exp in self.experiences if len(exp.reflection) > 2] # not "" or not '""'
        for exp in experiences:
            exp.round_id = round_id
            exp.outcome = outcome
            exp.game_setup = game_setup
        AddNewExperiences().run(experiences)
