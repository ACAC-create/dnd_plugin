from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import PersonNormalMessageReceived, GroupNormalMessageReceived
import random

@register(name="DnDCharacterCreator", description="D&D 5e character attribute roller & dice roller", version="1.1", author="AI & KirifujiNagisa") # 更新描述和版本
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

    def roll_dice(self, dice_command): #  参数改为接收完整的 dice_command (例如 ".rd20")
        """Rolls a single die of the specified type."""
        try:
            dice_type_str = dice_command[3:] # 从 ".rd20" 中提取 "20" (字符串形式)
            dice_size = int(dice_type_str) # 将提取的数字字符串转换为整数
            if dice_size <= 0:
                return "无效的骰子类型"
            return random.randint(1, dice_size)
        except ValueError:
            return "无效的骰子类型"

    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        if msg.startswith(".dnd"): # 修改判断逻辑，使用 startswith
            num_sets = 1 # 默认生成 1 组
            parts = msg.split(".dnd", 1) # 使用 split 切割，最多切割一次
            if len(parts) > 1 and parts[1].strip(): # 检查是否有数字部分
                num_str = parts[1].strip()
                if num_str.isdigit(): # 检查是否是数字
                    num_sets = int(num_str)
                    if num_sets <= 0: # 确保是正整数
                        num_sets = 1
                    elif num_sets > 10: # 限制生成组数上限，防止刷屏，可以根据需要调整
                        num_sets = 10
                else:
                    num_sets = 1 # 如果不是数字，也默认 1 组 (或者可以提示错误，看你想要的行为)

            attribute_sets_text = []
            for _ in range(num_sets): # 循环生成多组属性
                attributes = self.roll_attributes()
                total = sum(attributes)
                attribute_sets_text.append(f"[{', '.join(map(str, attributes))}] = {total}") # 每组属性一行

            reply = f"<user>的DnD5e人物作成(自由分配模式):\n" + "\n".join(attribute_sets_text) # 将多组属性用换行符连接
            ctx.add_return("reply", [reply])
            ctx.prevent_default()
        elif msg.startswith(".rd"): # 处理 .rd 骰子命令
            dice_command = msg.split(" ")[0] # 获取命令部分，例如 ".rd20"
            roll_result = self.roll_dice(dice_command) #  **这里，直接把完整的 dice_command (例如 ".rd20") 传给 roll_dice**
            if isinstance(roll_result, int): # 如果 roll_dice 返回的是整数，说明是有效骰子类型
                reply = f"<{ctx.event.sender_id if isinstance(ctx.event, GroupNormalMessageReceived) else 'user'}> 投掷 {dice_command} 结果: {roll_result}" # 群聊显示 sender_id, 私聊显示 user
                ctx.add_return("reply", [reply])
                ctx.prevent_default()
            elif roll_result == "无效的骰子类型": # 处理无效骰子类型
                reply = f"无效的骰子类型，支持 .rd2, .rd4, .rd6, .rd8, .rd10, .rd12, .rd20, .rd100"
                ctx.add_return("reply", [reply])
                ctx.prevent_default()


    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        sender_id = ctx.event.sender_id
        if msg.startswith(".dnd"): # 群聊的 .dnd 处理逻辑和私聊基本一致
            num_sets = 1
            parts = msg.split(".dnd", 1)
            if len(parts) > 1 and parts[1].strip():
                num_str = parts[1].strip()
                if num_str.isdigit():
                    num_sets = int(num_str)
                    if num_sets <= 0:
                        num_sets = 1
                    elif num_sets > 10:
                        num_sets = 10
                else:
                    num_sets = 1

            attribute_sets_text = []
            for _ in range(num_sets):
                attributes = self.roll_attributes()
                total = sum(attributes)
                attribute_sets_text.append(f"[{', '.join(map(str, attributes))}] = {total}")

            reply = f"<{sender_id}>的DnD5e人物作成(自由分配模式):\n" + "\n".join(attribute_sets_text)
            ctx.add_return("reply", [reply])
            ctx.prevent_default()
        elif msg.startswith(".rd"): # 群聊的 .rd 骰子命令处理逻辑和私聊基本一致
            dice_command = msg.split(" ")[0] # 获取命令部分，例如 ".rd20"
            roll_result = self.roll_dice(dice_command) # **这里，同样直接传递 dice_command**
            if isinstance(roll_result, int):
                reply = f"<{sender_id}> 投掷 {dice_command} 结果: {roll_result}"
                ctx.add_return("reply", [reply])
                ctx.prevent_default()
            elif roll_result == "无效的骰子类型":
                reply = f"无效的骰子类型，支持 .rd2, .rd4, .rd6, .rd8, .rd10, .rd12, .rd20, .rd100"
                ctx.add_return("reply", [reply])
                ctx.prevent_default()


    def __del__(self):
        pass