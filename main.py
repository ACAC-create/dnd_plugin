from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import PersonNormalMessageReceived, GroupNormalMessageReceived
import random

@register(name="DnDCharacterCreator", description="D&D 5e character attribute roller", version="1.0", author="AI & KirifujiNagisa")
class DnDCharacterCreatorPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        pass

    async def initialize(self):
        pass

    def roll_attributes(self):
        """Rolls 4d6 and drops the lowest die, six times."""
        attributes = []
        for _ in range(6):
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.remove(min(rolls))
            attributes.append(sum(rolls))
        return attributes

    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        if msg == ".dnd":
            attributes = self.roll_attributes()
            total = sum(attributes)
            reply = f"<user>的DnD5e人物作成(自由分配模式):\n[{', '.join(map(str, attributes))}] = {total}"
            ctx.add_return("reply", [reply])
            ctx.prevent_default()

    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        sender_id = ctx.event.sender_id
        if msg == ".dnd":
            attributes = self.roll_attributes()
            total = sum(attributes)
            reply = f"<{sender_id}>的DnD5e人物作成(自由分配模式):\n[{', '.join(map(str, attributes))}] = {total}"
            ctx.add_return("reply", [reply])
            ctx.prevent_default()
    
    def __del__(self):
        pass