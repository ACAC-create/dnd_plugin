from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import PersonNormalMessageReceived, GroupNormalMessageReceived
import random
import re # 导入正则表达式模块

@register(name="DnDCharacterCreator", description="D&D 5e character attribute roller & dice roller", version="1.3", author="AI & KirifujiNagisa") # 更新版本号
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

    def roll_dice(self, dice_command, num_dice=1): # 修改 roll_dice 函数，添加 num_dice 参数，默认为 1
        """Rolls a single die of the specified type, or multiple dice if num_dice > 1."""
        try:
            dice_type_str = dice_command[1:] # 从 "d20" 中提取 "20" (字符串形式),  注意这里去掉了 'd' 前缀，因为 dice_command 现在是 "d20" 或 "d6" 这样的格式
            dice_size = int(dice_type_str) # 将提取的数字字符串转换为整数
            if dice_size <= 0:
                return "无效的骰子类型"
            if num_dice <= 0: # 避免投掷 0 次或负数次骰子
                return "骰子数量无效"

            results = []
            for _ in range(num_dice): # 循环投掷多次
                results.append(random.randint(1, dice_size))

            if num_dice == 1: # 如果只投掷一次，直接返回数字结果
                return results[0]
            else: # 如果投掷多次，返回结果列表
                return results

        except ValueError:
            return "无效的骰子类型"
        except TypeError: # 处理 num_dice 不是整数的情况
            return "骰子数量无效"


    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        if msg.startswith(".dnd"):
            # .dnd 相关逻辑 (和之前一样，没有改动)
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

            reply = f"<user>的DnD5e人物作成(自由分配模式):\n" + "\n".join(attribute_sets_text)
            ctx.add_return("reply", [reply])
            ctx.prevent_default()
        elif msg.startswith(".rd") or msg.startswith(".r"): # 修改 .rd 和 .r 命令的处理逻辑
            command_parts = msg.split(" ")[0] # 获取命令部分，例如 ".rd20" 或 ".r3d6"

            num_dice = 1 # 默认骰子数量为 1
            dice_command_str = ""

            if command_parts.startswith(".rd"): # 处理旧的 .rd 命令
                dice_command_str = command_parts[2:] # 去除 ".rd" 前缀，例如 "d20"
                dice_command_prefix = ".rd" # 记录命令前缀，用于回复消息

            elif command_parts.startswith(".r"): # 处理新的 .r 命令 (多组投掷)
                match = re.match(r"\.r(\d+)d(\d+)", command_parts) # 使用正则表达式匹配 ".r{数量}d{骰子类型}" 格式
                if match:
                    num_dice = int(match.group(1)) # 提取骰子数量
                    dice_command_str = "d" + match.group(2) # 提取 "d{骰子类型}" 部分，例如 "d6"
                    dice_command_prefix = ".r" # 记录命令前缀

                else: # 如果 .r 命令格式不正确，例如 ".ra", ".rd", ".r3a" 等
                    reply = f"无效的骰子命令格式，多组投掷请使用 .r{{数量}}d{{骰子类型}}，例如 .r3d6, 单个骰子请使用 .rd{{骰子类型}}，例如 .rd20"
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()
                    return # 提前返回，避免后续代码执行


            if dice_command_str: # 如果成功解析出 dice_command_str (无论是 .rd 还是 .r 命令)
                roll_result = self.roll_dice(dice_command_str, num_dice) # 调用 roll_dice 函数，传入 dice_command_str 和 num_dice

                if isinstance(roll_result, int): # 如果是单个骰子结果
                    reply = f"<{ctx.event.sender_id if isinstance(ctx.event, GroupNormalMessageReceived) else 'user'}> 投掷 {dice_command_prefix}{dice_command_str} 结果: {roll_result}"
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()
                elif isinstance(roll_result, list): # 如果是多组骰子结果列表
                    results_str = ', '.join(map(str, roll_result)) # 将结果列表转换为逗号分隔的字符串
                    total_sum = sum(roll_result) # 计算结果总和
                    reply = f"<{ctx.event.sender_id if isinstance(ctx.event, GroupNormalMessageReceived) else 'user'}> 投掷 {command_parts} 结果: {results_str}  总和: {total_sum}" # 在回复消息中添加总和
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()
                elif isinstance(roll_result, str) and "无效" in roll_result: # 处理 "无效的骰子类型" 或 "骰子数量无效" 错误
                    reply = roll_result + f"，支持 .rd2, .rd4, .rd6, .rd8, .rd10, .rd12, .rd20, .rd100, 以及 .r{{数量}}d{{骰子类型}} 格式"
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()
                elif isinstance(roll_result, str) and "骰子数量无效" in roll_result: # 处理 "骰子数量无效" 错误 (单独处理可能更清晰)
                    reply = roll_result + f"，骰子数量必须是正整数"
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()


    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        sender_id = ctx.event.sender_id
        if msg.startswith(".dnd"):
            # 群聊 .dnd 逻辑 (和私聊一样，没有改动)
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
        elif msg.startswith(".rd") or msg.startswith(".r"): # 群聊 .rd 和 .r 命令的处理逻辑 (和私聊一样)
            command_parts = msg.split(" ")[0] # 获取命令部分，例如 ".rd20" 或 ".r3d6"

            num_dice = 1 # 默认骰子数量为 1
            dice_command_str = ""
            if command_parts.startswith(".rd"): # 处理旧的 .rd 命令
                dice_command_str = command_parts[2:] # 去除 ".rd" 前缀，例如 "d20"
                dice_command_prefix = ".rd" # 记录命令前缀，用于回复消息
            elif command_parts.startswith(".r"): # 处理新的 .r 命令 (多组投掷)
                match = re.match(r"\.r(\d+)d(\d+)", command_parts) # 使用正则表达式匹配 ".r{数量}d{骰子类型}" 格式
                if match:
                    num_dice = int(match.group(1)) # 提取骰子数量
                    dice_command_str = "d" + match.group(2) # 提取 "d{骰子类型}" 部分，例如 "d6"
                    dice_command_prefix = ".r" # 记录命令前缀
                else: # 如果 .r 命令格式不正确，例如 ".ra", ".rd", ".r3a" 等
                    reply = f"无效的骰子命令格式，多组投掷请使用 .r{{数量}}d{{骰子类型}}，例如 .r3d6, 单个骰子请使用 .rd{{骰子类型}}，例如 .rd20"
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()
                    return # 提前返回，避免后续代码执行


            if dice_command_str: # 如果成功解析出 dice_command_str (无论是 .rd 还是 .r 命令)
                roll_result = self.roll_dice(dice_command_str, num_dice) # 调用 roll_dice 函数，传入 dice_command_str 和 num_dice

                if isinstance(roll_result, int): # 如果是单个骰子结果
                    reply = f"<{sender_id}> 投掷 {dice_command_prefix}{dice_command_str} 结果: {roll_result}"
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()
                elif isinstance(roll_result, list): # 如果是多组骰子结果列表
                    results_str = ', '.join(map(str, roll_result)) # 将结果列表转换为逗号分隔的字符串
                    total_sum = sum(roll_result) # 计算结果总和
                    reply = f"<{sender_id}> 投掷 {command_parts} 结果: {results_str}  总和: {total_sum}" # 在回复消息中添加总和
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()
                elif isinstance(roll_result, str) and "无效" in roll_result: # 处理 "无效的骰子类型" 或 "骰子数量无效" 错误
                    reply = roll_result + f"，支持 .rd2, .rd4, .rd6, .rd8, .rd10, .rd12, .rd20, .rd100, 以及 .r{{数量}}d{{骰子类型}} 格式"
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()
                elif isinstance(roll_result, str) and "骰子数量无效" in roll_result: # 处理 "骰子数量无效" 错误 (单独处理可能更清晰)
                    reply = roll_result + f"，骰子数量必须是正整数"
                    ctx.add_return("reply", [reply])
                    ctx.prevent_default()


    def __del__(self):
        pass