import time
import shutil
from os import makedirs,path

from pagermaid import log, bot
from pagermaid.listener import listener
from pagermaid.utils import alias_command
from requests import get
version = "2.02"
REPO_RAW_URL = "https://raw.githubusercontent.com/sahuidhsu/PM_chouxiang/main"
REPO_NAME = "sahuidhsu/PM_chouxiang"
LOCAL_DIR = "data/cx_audios"

async def update(context):
    await context.edit("检查更新中...")
    try:
        response = get(f"https://api.github.com/repos/{REPO_NAME}/releases/latest",
                                                  headers={"User-Agent": "Mozilla/5.0"})
        latest = response.json()['tag_name']
        if response.status_code != 200:
            await context.edit(f"检查更新失败!\n服务器返回状态码: {response.status_code}")
            await log(f"检查更新失败!服务器返回状态码: {response.status_code}")
            return
        if latest == version:
            await context.edit(f"当前已是最新版本!\n最新Release版本号：**{latest}**")
            time.sleep(2)
            await context.delete()
            return
        else:
            await context.edit(f"检测到新版本**{latest}**，正在更新...")
            file = get(f"{REPO_RAW_URL}/chouxiang.py")
            if file.status_code != 200:
                await context.edit(f"更新失败!\n服务器返回状态码: {file.status_code}")
                await log(f"更新失败!服务器返回状态码: {file.status_code}")
                return
            with open("plugins/chouxiang.py", "w") as f:
                f.write(file.text)
            try:
                await context.edit(f"更新完成！已更新到**{latest}**版本\n正在尝试自动重启(重启完不会有提示)...")
                await log(f"抽象插件已更新到{latest}版本")
                await context.client.disconnect()
            except BaseException as e:
                await log(f"自动重启失败!报错信息: {e}")
                await context.edit(f"自动重启失败!\n报错信息: {e}")
                return
    except Exception as e:
        await log(f"更新失败!报错信息: {e}")
        await context.edit(f"更新失败!报错信息: {e}")
        return

async def get_list() -> str:
    try:
        response = get(f"{REPO_RAW_URL}/audios/list.json")
        res = response.json()
        result = "抽象语录列表：\n"
        for key, value in res["audios"].items():
            result += f"{key} - {value['description']}\n"
        return result
    except:
        await log("获取语录列表时发生错误")
        return "抽象语录获取失败，请检查网络"

async def clear_cache() -> str:
    if path.exists(LOCAL_DIR):
        try:
            shutil.rmtree(LOCAL_DIR)
            return "清理完成"
        except Exception as e:
            await log(f"清理失败 错误信息: {e}")
            return "清理失败 错误信息:\n" + str(e)
    else:
        return "本地缓存不存在"

async def send_audio(context, text):
    makedirs(LOCAL_DIR, exist_ok=True)
    if path.exists(f"{LOCAL_DIR}/{text}.mp3"):
        await context.edit("正在发送语录...")
        await context.client.send_file(context.chat_id, f"{LOCAL_DIR}/{text}.mp3", voice_note=True)
        await log(f"语录 {text} 发送完毕")
        await context.delete()
        return
    else:
        try:
            response = get(f"{REPO_RAW_URL}/audios/{text}.mp3")
            if response.status_code != 200:
                await context.edit("语录不存在或无法联系GitHub服务器，请检查是否输入正确")
                return
            with open(f"{LOCAL_DIR}/{text}.mp3", "wb") as f:
                f.write(response.content)
            await context.edit("正在发送语录...")
            await context.client.send_file(context.chat_id, f"{LOCAL_DIR}/{text}.mp3", voice_note=True)
            await log(f"语录 {text} 发送完毕")
            await context.delete()
            return
        except Exception as e:
            await log(f"下载语录时发生错误: {e}")
            await context.edit(f"下载语录时发生错误: {e}")
            return

@listener(outgoing=True, command=alias_command("cx"),
          description="抽象语录", parameters="<text>")
async def cx(context):
    command = context.arguments
    if command == "help":
        await context.edit(f"抽象语录 - V{version}\n"
                           "-cx [text] - 发送抽象语录\n"
                           "-cx help - 获取帮助\n"
                           "-cx list - 获取抽象语录列表\n"
                           "-cx clear - 清理本地缓存")
        return
    elif command == "list":
        await context.edit(await get_list())
        return
    elif command == "clear":
        await context.edit(await clear_cache())
        return
    elif command == "update":
        await update(context)
        return
    else:
        if not command:
            await context.edit("参数有误，请使用 `-cx help` 查看帮助。")
            return
        else:
            await send_audio(context, command)
            return