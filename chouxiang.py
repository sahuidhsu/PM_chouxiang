import base64
import time
from http.client import responses
from os import remove,makedirs

from pagermaid import log, bot
from pagermaid.listener import listener
from pagermaid.utils import alias_command
from requests import get
version = "2.0.2"
REPO_RAW_URL = "https://raw.githubusercontent.com/sahuidhsu/PM_chouxiang/main"
REPO_NAME = "sahuidhsu/PM_chouxiang"
LOCAL_DIR = "data/cx_audios"

async def update(context):
    await context.edit("检查更新中...")
    try:
        latest = get(f"{REPO_RAW_URL}/version.txt")
        if latest.status_code != 200:
            await context.edit(f"检查更新失败!\n服务器返回状态码: {latest.status_code}")
            await log(f"检查更新失败!服务器返回状态码: {latest.status_code}")
            return
        if latest.text == version:
            await context.edit(f"当前已是最新版本!\n版本号：**{latest.text}**")
            time.sleep(2)
            await context.delete()
            return
        else:
            await context.edit(f"检测到新版本**{latest.text}**，正在更新...")
            file = get(f"{REPO_RAW_URL}/chouxiang.py")
            if file.status_code != 200:
                await context.edit(f"更新失败!\n服务器返回状态码: {file.status_code}")
                await log(f"更新失败!服务器返回状态码: {file.status_code}")
                return
            with open("plugins/chouxiang.py", "w") as f:
                f.write(file.text)
            try:
                await context.edit(f"更新完成！已更新到**{latest.text}**版本\n正在尝试自动重启(重启完不会有提示)...")
                await log(f"抽象插件已更新到{latest.text}版本")
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

async def send_audio(context, text):
    await context.edit("生成中...")
    try:
        code = ""
        tmpfile = open("renshu.mp3", "wb")
        tmpfile.write(base64.b64decode(code))
        tmpfile.close()
    except BaseException as e:
        await context.edit(f"出错了呜呜呜: {e}")
        return
    try:
        await context.delete()
        await context.client.send_file(context.chat_id, "renshu.mp3", voice_note=True)
        remove("renshu.mp3")
        await log("忍术发送完毕")
        return
    except BaseException as e:
        await log(f"忍术发送失败: {e}")
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
        # await clear_cache()
        await context.edit("`功能待实现。`")
        return
    elif command == "update":
        await update(context)
        return
    else:
        if not command:
            await context.edit("参数有误，请使用 `,cx help` 查看帮助。")
            return
        else:
            await send_audio(context, command)
            return