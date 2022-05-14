from random import random
import discord
from discord.ext import commands
from marsbots_core import config
from marsbots_core.models import ChatMessage
from marsbots_core.programs.lm import complete_text
from marsbots_core.resources.discord_utils import (
    filter_application_command_messages,
    get_discord_messages,
    is_mentioned,
    replace_mentions_with_usernames,
)
from marsbots_core.resources.language_models import OpenAIGPT3LanguageModel


class DoomerCog(commands.Cog):
    def __init__(self, bot: commands.bot) -> None:
        self.bot = bot
        self.language_model = OpenAIGPT3LanguageModel(
            frequency_penalty=1.0,
            presence_penalty=0.2,
        )
        self.response_thresh = 0.01

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message) -> None:
        if (
            is_mentioned(message, self.bot.user)
            or self.bot.settings.name.lower() in message.content.lower()
            or (not message.author.bot and self.should_act())
        ):
            ctx = await self.bot.get_context(message)
            async with ctx.channel.typing():
                completion = await self.get_completion_with_chat_context(ctx, 10)
                await ctx.channel.send(completion)

    @commands.slash_command()
    async def respond(
        self,
        ctx: commands.Context,
        n_messages: discord.Option(
            int,
            description="Number of recent messages to include",
            required=False,
            default=10,
        ),
    ) -> None:
        await ctx.defer()
        completion = await self.get_completion_with_chat_context(ctx, n_messages)
        await ctx.respond(completion)

    @commands.slash_command()
    async def complete(
        self,
        ctx,
        prompt: discord.Option(
            str,
            description="Text to complete",
            required=True,
        ),
        max_tokens: discord.Option(
            int,
            description="Number of tokens to generate",
            required=False,
            default=100,
        ),
    ):
        await ctx.defer()
        completion = await complete_text(
            self.language_model, prompt, max_tokens=max_tokens
        )
        formatted = f"**{prompt}**{completion}"
        await ctx.respond(formatted)

    def should_act(self) -> bool:
        r = random()
        return r < self.response_thresh

    async def get_completion_with_chat_context(self, ctx, n_messages):
        prompt = await self.format_prompt(ctx, n_messages)
        completion = await complete_text(
            self.language_model, prompt, max_tokens=80, stop=["**[", "\n\n"]
        )
        return completion

    async def format_prompt(self, ctx, n_messages):
        last_messages = await get_discord_messages(ctx.channel, n_messages)
        last_messages = (
            last_messages[:-1]
            if last_messages[-1].type == discord.MessageType.application_command
            else last_messages
        )
        prompt = "\n".join(
            [
                str(
                    ChatMessage(
                        self.message_preprocessor(m),
                        m.author.display_name,
                    )
                ).strip()
                for m in last_messages
            ]
        )
        prompt += "\n"
        prompt += f"**[{self.bot.user.display_name}]**:"
        return prompt

    def message_preprocessor(self, message: discord.Message) -> str:
        message_content = replace_mentions_with_usernames(
            message.content, message.mentions
        )
        message_content = message_content.strip()
        return message_content


def setup(bot: commands.Bot) -> None:
    bot.add_cog(DoomerCog(bot))
