# handlers/admins/sever.py
import asyncio
import platform
import subprocess
import time
from datetime import timedelta

import psutil
import speedtest
from aiogram import Router

panel_router = Router()

BOT_START_TIME = time.time()


# -------------------- Helpers (async wrappers for blocking ops) --------------------
async def run_subprocess_ping() -> str:
    def _ping_blocking() -> str:
        try:
            ping_cmd = ["ping", "-c", "4", "google.com"] if platform.system() != "Windows" else ["ping", "-n", "4",
                                                                                                 "google.com"]
            result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=10)
            out = result.stdout.strip().splitlines()
            if not out:
                return "📶 Ping olinmadi"
            # last meaningful line often has slashes in Linux `rtt min/avg/max/mdev = x/x/x/x ms`
            last = out[-1]
            if "/" in last:
                # find average
                parts = last.split("/")
                if len(parts) >= 2:
                    avg = parts[-2] if "/" in last else parts[-1]
                    # try parse number
                    try:
                        # example: 'rtt min/avg/max/mdev = 14.456/15.123/17.000/0.800 ms'
                        avg_val = last.split("=")[1].split("/")[1]
                        return f"📶 Ping: <b>{avg_val} ms</b>"
                    except Exception:
                        return "📶 Ping: <b>Noma'lum</b>"
            # fallback: parse for 'time=' occurrences in ping output
            for line in reversed(out):
                if "time=" in line:
                    try:
                        t = line.split("time=")[1].split()[0]
                        return f"📶 Ping: <b>{t}</b>"
                    except Exception:
                        continue
            return "📶 Ping olinmadi"
        except Exception:
            return "📶 Ping olinmadi"

    return await asyncio.to_thread(_ping_blocking)


async def run_speedtest() -> str:
    def _speed_blocking() -> str:
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            dl = st.download() / 1e6
            ul = st.upload() / 1e6
            return f"🚀 <b>Internet tezligi:</b>\n🔻 Yuklab olish: <b>{dl:.2f} Mbps</b>\n🔺 Yuklash: <b>{ul:.2f} Mbps</b>"
        except Exception:
            return "🚀 Internet tezligi aniqlanmadi"

    return await asyncio.to_thread(_speed_blocking)


def get_bot_uptime() -> str:
    bot_uptime_seconds = time.time() - BOT_START_TIME
    return f"⏳ <b>Bot Uptime:</b> {str(timedelta(seconds=int(bot_uptime_seconds)))}"


async def gather_system_info() -> str:
    """
    Collect system info using psutil and platform in a thread to avoid blocking loop.
    """

    def _collect_blocking() -> str:
        try:
            uname = platform.uname()
            virtual_memory = psutil.virtual_memory()
            disk_usage = psutil.disk_usage("/")

            system_info = (
                f"🖥 <b>Server Ma'lumotlari:</b>\n"
                f"🔹 Tizim: <b>{uname.system}</b>\n"
                f"🔹 Host: <b>{uname.node}</b>\n"
                f"🔹 OS: <b>{uname.release}</b>\n"
                f"🔹 Arxitektura: <b>{uname.machine}</b>\n"
                f"🔹 Processor: <b>{uname.processor}</b>\n"
            )

            cpu_info = (
                f"\n⚙️ <b>CPU Ma'lumotlari:</b>\n"
                f"🖥 Yadro: <b>{psutil.cpu_count(logical=True)}</b>\n"
                f"📊 CPU Yuklanishi: <b>{psutil.cpu_percent()}%</b>\n"
            )

            def _format_size(num: int) -> str:
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if num < 1024.0:
                        return f"{num:.2f} {unit}"
                    num /= 1024.0
                return f"{num:.2f} PB"

            ram_info = (
                f"\n💾 <b>RAM:</b>\n"
                f"📌 Jami: <b>{_format_size(virtual_memory.total)}</b>\n"
                f"📊 Ishlatilmoqda: <b>{_format_size(virtual_memory.used)}</b>\n"
                f"🟢 Bo‘sh: <b>{_format_size(virtual_memory.available)}</b>\n"
                f"📈 Yuklanish: <b>{virtual_memory.percent}%</b>\n"
            )

            disk_info = (
                f"\n🗄 <b>Disk:</b>\n"
                f"💾 Umumiy: <b>{_format_size(disk_usage.total)}</b>\n"
                f"📂 Ishlatilgan: <b>{_format_size(disk_usage.used)}</b>\n"
                f"🟢 Bo‘sh joy: <b>{_format_size(disk_usage.free)}</b>\n"
                f"📊 Yuklanish: {disk_usage.percent}%\n"
            )

            return system_info + cpu_info + ram_info + disk_info
        except Exception as e:
            return f"🚨 Xatolik (system info): {e}"

    basic = await asyncio.to_thread(_collect_blocking)
    ping = await run_subprocess_ping()
    speed = await run_speedtest()
    bot_uptime = get_bot_uptime()
    return f"{basic}\n{ping}\n{speed}\n\n{bot_uptime}"
