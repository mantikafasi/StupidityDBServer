import config
import discord


class embed:

    @staticmethod
    def success(title: str, description: str = ""):
        emoji, color = config.emojis.success, config.colors.success
        _embed = discord.Embed(
            title=f"{emoji} {title}", description=description, color=color)
        return _embed

    @staticmethod
    def error(title: str, description: str = ""):
        emoji, color = config.emojis.error, config.colors.error
        _embed = discord.Embed(
            title=f"{emoji} {title}", description=description, color=color)
        return _embed

    @staticmethod
    def warning(title: str, description: str = ""):
        emoji, color = config.emojis.warning, config.colors.warning
        _embed = discord.Embed(
            title=f"{emoji} {title}", description=description, color=color)
        return _embed