import logging

import telegrampy
from telegrampy.ext import commands

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("telegrampy")

bot = commands.Bot("token here")


class ConfirmMenu(telegrampy.InlineKeyboard):
    @telegrampy.inline_keyboard_button(text="Yes")
    async def yes(self, query: telegrampy.CallbackQuery, button: telegrampy.InlineKeyboardButton):
        await query.answer(text="Operation confirmed")
        self.stop()

    @telegrampy.inline_keyboard_button(text="No")
    async def no(self, query: telegrampy.CallbackQuery, button: telegrampy.InlineKeyboardButton):
        await query.answer(text="Operation cancelled")
        self.stop()


@bot.command(name="confirm")
async def confirm_command(ctx: commands.Context):
    await ctx.send("Are you sure you want to do this?", reply_markup=ConfirmMenu())

bot.run()
