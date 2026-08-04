from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
import textwrap
import psutil
import time
import os
import datetime
import random
import asyncio
import platform

# ========= 常量 ==========
VERSION = "2.2.0" # 插件版本
RUN_INFO_LINES = 8 # 打印的运行信息列表行数，超过部分省略号


@register("astrbot_plugin_Cecilia", 
          "Teddizen", 
          "塞西莉亚bot自写插件", 
          VERSION)  
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `！helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"HelloWorld, {user_name}, 你发的 “{message_str}” 塞西莉亚收到啦!") # 发送一条纯文本消息

    @filter.command("help")
    async def help(self, event: AstrMessageEvent):
        """这是一个 help 指令"""
        logger.info("接收到help请求")
        yield event.image_result("https://teddizen-java-tesy.oss-cn-guangzhou.aliyuncs.com/help.png")

    @filter.regex(r"^.*司康饼.*$")
    async def cookie(self, event: AstrMessageEvent):
        """司康饼命令"""
        logger.info("接收到司康饼请求（？")
        yield event.plain_result("司康饼？！在哪里？！…啊，对不起，我太激动了。但是，但是！司康饼真的很好吃嘛…热乎乎的，外酥内软，配上红茶简直是天作之合…如果你有司康饼的话，能不能分我一小块？只要一小块就好！我可以帮你祈祷作为交换…")
    
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def resive_message(self, event: AstrMessageEvent):
        raw = event.message_obj.raw_message
        if not isinstance(raw, dict):
            return
        if raw.get("post_type") != "notice":
            return

        notice_type = raw.get("notice_type")
        if notice_type == "group_increase":
            uid = raw["user_id"]
            group_id = str(raw["group_id"])
            logger.info(f"新成员 {uid} 进入群 {group_id}")
            chain = [
                Comp.At(qq=uid),
                Comp.Plain(f" 欢迎新成员 {uid} 进入群 {group_id}")
            ]

            from astrbot.core.platform.message_session import MessageType

            # HACK: 处理平台标识的log记录
            # 在入群事件处理中
            logger.info(f"event.session_id: {event.session_id}")
            logger.info(f"All MessageType values: {[e.value for e in MessageType]}")

            # 获取平台标识（通常为 'onebot'，但建议从 event 获取）
            platform = getattr(event, 'platform', 'onebot')  # 若 event 无 platform 属性则默认 onebot
            # 正确构造 session 字符串
            origin = f"{platform}:{MessageType.GroupMessage.value}:{group_id}"
            await self.context.send_message(origin, chain)

    @filter.command("投骰子")
    async def roll_dice(self, event: AstrMessageEvent):
        """投骰子命令"""
        logger.info("接收到roll骰子请求")
        # 生成随机数并回复
        res = random.randint(1, 6)
        yield event.plain_result(f"塞西莉亚投出了一个6面骰子，结果是：{res}")

    @filter.regex(r"^随机数.*到.*$")
    async def rand_num(self, event: AstrMessageEvent):
        """随机数命令，格式：随机数[数字]到[数字]"""
        text = event.message_str.strip()
        # 移除开头的“随机数”字
        content = text.removeprefix("随机数").strip()
        # 用到分割两段
        parts = content.split("到")

        start = parts[0].strip()
        end = parts[1].strip()
        logger.info(f"接收到rand_num请求，起始数字：{start}，结束数字：{end}")
        # 1. 给空参数赋默认区间 0~100
        if not start or not end:
            yield event.plain_result("❌ 格式错误！请使用：随机数[数字]到[数字]\n例如：随机数1到10")
            return
        else:
            try:
                s = int(start)
                e = int(end)
            except (ValueError, TypeError):
                yield event.plain_result("❌ 输入数据类型错误！请使用：随机数[数字]到[数字]\n例如：随机数1到10")
                return
            # 校验大小
            if s > e:
                yield event.plain_result("❌ 数据大小错误！起始数字不能大于结束数字")
                return
        
        # 生成随机数并回复
        res = random.randint(s, e)
        yield event.plain_result(f"塞西莉亚听到了…从遥远的神明那里传来的声音，那个数字是…{res}！")

    @filter.regex(r"^选.*还是.*$")
    async def choose(self, event: AstrMessageEvent):
        """随机选择命令，格式：选选项一还是选项二"""
        text = event.message_str.strip()
        # 移除开头的“选”字
        content = text.removeprefix("选").strip()
        # 用还是分割两段
        parts = content.split("还是")

        opt1 = parts[0].strip()
        opt2 = parts[1].strip()
        logger.info(f"接收到choose请求，选项一：{opt1}，选项二：{opt2}")
        
        # 校验选项是否为空
        if not opt1 or not opt2:
            yield event.plain_result("❌ 格式错误！请使用：选选项一还是选项二\n例如：选苹果还是橘子")
            return

        result = random.choice([opt1, opt2])
        yield event.plain_result(f"塞西莉亚建议选择：{result}哦！")

    @filter.command("top")
    async def top(self, event: AstrMessageEvent):
        """🔧 系统资源监控命令"""
        logger.info("接收到top请求")
        
        # ========== 获取系统信息 ==========
        cpu_percent = psutil.cpu_percent(interval=0.3, percpu=True)
        cpu_avg = sum(cpu_percent) / len(cpu_percent)
        load_avg = psutil.getloadavg()  # 系统1/5/15分钟负载
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        uptime_str = str(uptime).split('.')[0]
        
        from .utils.top_processes import get_processes
        processes = get_processes()
        top_processes = processes[:RUN_INFO_LINES]

        # ========== 专业版输出 ==========
        lines = [
            "   ✨ 塞西莉亚bot ✨",
            "    系统资源监控面板",
            "-" * 25,
            "",
            "📊 【系统概览】",
            f"• 系统信息: {platform.platform()}",
            f"• 系统运行时间: {uptime_str}",
            f"• 启动时间: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "💻 【CPU 状态】",
            f"• CPU核心数: {len(cpu_percent)}核",
            f"• 当前使用率: {cpu_avg:.1f}%",
            f"• 1分钟负载: {load_avg[0]:.2f}",
            f"• 5分钟负载: {load_avg[1]:.2f}",
            f"• 15分钟负载: {load_avg[2]:.2f}",
            "",
            "💾 【内存状态】",
            f"• 物理内存: {mem.used/1024**3:.1f}GB / {mem.total/1024**3:.1f}GB ({mem.percent:.1f}%)",
            f"• 可用内存: {mem.available/1024**3:.2f} GB",
            f"• 交换分区: {swap.used/1024**3:.1f}GB / {swap.total/1024**3:.1f}GB ({swap.percent:.1f}%)",
            "",
            "💽 【磁盘状态】",
            f"• 根分区: {disk.used/1024**3:.1f}GB / {disk.total/1024**3:.1f}GB ({disk.percent:.1f}%)",
            "",
            "📋 【进程列表】",
            f"• 进程总数: {len(processes)} 个",
            "-" * 25,
            f" {'PID':<6} {'进程名':<15} {'用户':<8} "
            f" {'内存(MB)':>8} {'占比':>6}",
            "-" * 25,
        ]
        
        for p in top_processes:
            lines.append(
                f" {p['pid']:<6} {p['name'][:14]:<15} {p['user'][:6]:<8} "
                f" {p['memory_mb']:>8.1f} {p['memory_percent']:>5.1f}%"
            )
        
        lines.extend([
            "-" * 25,
            "📌 Made by 哲迪君",
            f"🚀 Version: {VERSION}"
        ])
        
        yield event.plain_result('\n'.join(lines))

    @filter.regex(r"^！？.*？！$", priority=1)
    async def resive_message_gantan(self, event: AstrMessageEvent):
        text = event.message_str.strip()
        yield event.plain_result(text)
        """接收消息"""
    
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
