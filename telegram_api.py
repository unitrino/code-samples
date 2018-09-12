from aiotg import Bot, Chat

from db import UserData

bot = Bot("518654004:AAGeHYTzXDd-gRN-2LwjUeljN4nghIM3F34")

async def greeter(private_id, body):
    private = bot.private(private_id)
    await private.send_text(body)

@bot.command(r"/whoami")
async def whoami(chat, match):
    return chat.reply(chat.sender["id"])

@bot.command(r"/create (.+)")
async def create_new_app(chat: Chat, match):
    private_id = chat.sender["id"]
    app_name = str(match.group(1))
    print(str(private_id) + " " + str(app_name))
    if UserData.select().where(UserData.app_name == app_name):
        return chat.reply("App with this name already exists")
    else:
        UserData.create(app_name=app_name, private_id=private_id).save()
        return chat.reply("App " + str(app_name) + " successfully create")


if __name__ == '__main__':
    bot.run(debug=True)
