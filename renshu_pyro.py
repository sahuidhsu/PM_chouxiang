import base64
from os import remove
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.enums import Message
from pagermaid.services import bot

@listener(command="renshu",
          description="释放忍术")
async def renshu(message: Message):
    await message.edit("生成中")
    try:
        code = "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"
        tmpfile = open("renshu.mp3", "wb")
        tmpfile.write(base64.b64decode(code))
        tmpfile.close()
    except BaseException as e:
        await message.edit(f"出错了呜呜呜: {e}")
        return
    try:
        cid = message.chat.id
        await message.delete()
        await bot.send_voice(cid, "renshu.mp3")
        remove("renshu.mp3")
        await log("忍术发送完毕")
        return
    except BaseException as e:
        await log(f"忍术发送失败: {e}")
        return