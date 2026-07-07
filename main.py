from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import textwrap
import psutil
import time
import os
import datetime
import random
import asyncio
import platform

@register("astrbot_plugin_Cecilia", 
          "Teddizen", 
          "塞西莉亚bot自写插件", 
          "2.1.1")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
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

    @filter.regex(r"^随机数\s*(?:(\d+)\s*到\s*(\d+))?$")
    async def rand_num(self, event, start: str = None, end: str = None):
        """随机数命令，格式：随机数[数字]到[数字]"""
        # 1. 给空参数赋默认区间 0~100
        if start is None and end is None:
            s, e = 0, 100
        else:
            try:
                s = int(start)
                e = int(end)
            except (ValueError, TypeError):
                yield event.plain_result("❌ 格式错误！请使用：随机数[数字]到[数字]\n例如：随机数1到10")
                return
            # 校验大小
            if s > e:
                yield event.plain_result("❌ 格式错误！起始数字不能大于结束数字")
                return
        
        # 生成随机数并回复
        res = random.randint(s, e)
        yield event.plain_result(f"塞西莉亚听到了…从遥远的神明那里传来的声音，那个数字是…{res}！")

    @filter.regex(r"^选\s*(\S+)\s*还是\s*(\S+)$")
    async def choose(self, event: AstrMessageEvent, opt1: str = None, opt2: str = None):
        """随机选择命令，格式：选[选项一]还是[选项二]"""
        if opt1 and opt2:
            try:
                result = random.choice([opt1, opt2])
                yield event.plain_result(f"塞西莉亚建议选择：{result}哦！")
                return
            except ValueError:
                pass
        
        # 格式错误，提示用户正确用法
        yield event.plain_result("❌ 格式错误！请使用：选选项一还是选项二\n例如：选 苹果还是橘子")

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
        top_processes = processes[:8]

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
            f"🚀 Version: 2.1.1"
        ])
        
        yield event.plain_result('\n'.join(lines))
    
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
