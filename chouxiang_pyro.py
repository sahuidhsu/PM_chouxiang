import os
import shutil
import time
from traceback import print_exc
from typing import BinaryIO

from pagermaid.utils.bot_utils import log
from pagermaid.enums import Message
from pagermaid.listener import listener
from pagermaid.services import bot
from pagermaid.services import client

VERSION = "2.0.2"
REPO_RAW_URL = "https://raw.githubusercontent.com/sahuidhsu/PM_chouxiang/main"
REPO_NAME = "sahuidhsu/PM_chouxiang"
LOCAL_DIR = "data/cx_audios"


async def get_audio(name: str, retry=False) -> BinaryIO | None:
    os.makedirs(LOCAL_DIR, exist_ok=True)
    if os.path.isfile(f"{LOCAL_DIR}/{name}.mp3"):
        return open(f"{LOCAL_DIR}/{name}.mp3", "rb")
    else:
        if retry:
            return None
        # Try download from git
        try:
            response = await client.get(f"{REPO_RAW_URL}/audios/{name}.mp3")
            # File not found
            if response.status_code != 200:
                raise Exception("Audio not found")
            content = response.read()
            with open(f"{LOCAL_DIR}/{name}.mp3", "wb") as f:
                f.write(content)
            return await get_audio(name, True)
        except:
            await log("下载语音时发生错误")
            print_exc()
            return None


async def get_list() -> str:
    try:
        response = await client.get(f"{REPO_RAW_URL}/audios/list.json")
        res = response.json()
        result = "抽象语录列表：\n"
        for key, value in res["audios"].items():
            result += f"{key} - {value['description']}\n"
        return result
    except:
        await log("获取语录列表时发生错误")
        print_exc()
        return "抽象语录获取失败，请检查网络"


async def clear_cache():
    if os.path.exists(LOCAL_DIR):
        shutil.rmtree(LOCAL_DIR)


@listener(command="cx", description="发送抽象语录", parameters="[text]")
async def cx(message: Message):
    msg = message.arguments
    if not msg:
        await message.edit("参数有误，请使用 `,cx help` 查看帮助。")
        return
    match msg:
        case "help":
            # Help menu
            await message.edit(f"抽象语录 - V{VERSION}\n"
                               ",cx [text] - 发送抽象语录\n"
                               ",cx help - 获取帮助\n"
                               ",cx list - 获取抽象语录列表\n"
                               ",cx clear - 清理本地缓存")
            return
        case "list":
            # Get audio list from GitHub
            await message.edit(await get_list())
            return
        case "clear":
            # Clear local cache
            await clear_cache()
            await message.edit("`清理完成。`")
        case "update":
            # Update the plugin
            try:
                latest_version = await client.get(f"https://api.github.com/repos/{REPO_NAME}/releases/latest",
                                                  headers={"User-Agent": "Mozilla/5.0"})
                if latest_version.status_code != 200:
                    await message.edit("检测更新失败，请稍后重试")
                    return
                latest_version = latest_version.json()['tag_name']
                if VERSION == latest_version:
                    await message.edit(f"当前已是最新版本!\n版本号：**{latest_version}**")
                    time.sleep(2)
                    await message.delete()
                    return
                else:
                    await message.edit(f"检测到新版本!\n版本号：**{latest_version}**，正在更新...")
                file = client.get(f"{REPO_RAW_URL}/chouxiang_pyro.py")
                with open("plugins/chouxiang_pyro.py", "w") as f:
                    f.write(file.text)
                try:
                    await message.edit(
                        f"更新完成！已更新到**{latest_version}**版本\n请手动使用**restart**指令重启机器人！")
                    await log(f"抽象插件已更新到{latest_version}版本")
                    await clear_cache()
                except BaseException as e:
                    await log(f"自动重启失败!报错信息: {e}")
                    await message.edit(f"自动重启失败!\n报错信息: {e}")
                    return
            except:
                await log("更新插件时发生错误")
                print_exc()
                return
        case _:
            if (audio := await get_audio(msg)) is None:
                await message.edit("`出错了呜呜呜 ~ 未找到对应的语音。`")
                return
            else:
                await message.delete()
                await bot.send_voice(message.chat.id, audio)
                return
