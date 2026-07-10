import discord
from discord.ext import commands
from discord import app_commands
import datetime
import pytz

# --- 設定 ---
TOKEN = 'MTQ5MDYyNDcyNzA1NDgxMTIwNw.GidxLC.UL1iJIlhnqvPCqRFmri-U4UigtK0y7pk8rljdA' # 先ほど取得したトークン
FORUM_CHANNEL_ID = 1490645851733889147 # フォーラムのID

JST = pytz.timezone('Asia/Tokyo')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# --- 日付生成ロジック ---
def generate_date_choices():
    choices = []
    now = datetime.datetime.now(JST)
    for i in range(21):
        target = now + datetime.timedelta(days=i)
        label = f"{target.month}/{target.day}({['月','火','水','木','金','土','日'][target.weekday()]})"
        if i == 0: label += " (今日)"
        choices.append(app_commands.Choice(name=label, value=target.strftime("%Y-%m-%d")))
    return choices

DATE_CHOICES = generate_date_choices()

@bot.tree.command(name="募集", description="対戦募集を開始します")
@app_commands.describe(date="日付", hour="時間", minute="分", map_name="マップ")
@app_commands.choices(
    date=DATE_CHOICES,
    hour=[app_commands.Choice(name=f"{i:02d}時", value=f"{i:02d}") for i in range(24)],
    minute=[app_commands.Choice(name=f"{i:02d}分", value=f"{i:02d}") for i in [0, 15, 30, 45]],
    map_name=[
    app_commands.Choice(name="古書館", value="古書館"),
    app_commands.Choice(name="リカドの村", value="リカドの村"),
    app_commands.Choice(name="天空庭園", value="天空庭園"),
    app_commands.Choice(name="シーダモの港", value="シーダモの港"),
    app_commands.Choice(name="ガイデス闘技場1", value="ガイデス闘技場1"),
    app_commands.Choice(name="ガイデス闘技場2", value="ガイデス闘技場2"),
    app_commands.Choice(name="地の神殿", value="地の神殿"),
    app_commands.Choice(name="塔都テレイア", value="塔都テレイア"),
    app_commands.Choice(name="風の神殿", value="風の神殿"),
    app_commands.Choice(name="ロータリー", value="ロータリー"),
    app_commands.Choice(name="ザエイト", value="ザエイト"),
    app_commands.Choice(name="どこでも", value="どこでも")
    ]
)
async def recruit(interaction: discord.Interaction, date: str, hour: str = "21", minute: str = "00", map_name: str = "未定"):
    await interaction.response.defer(ephemeral=True)
    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    target_dt = JST.localize(datetime.datetime(dt.year, dt.month, dt.day, int(hour), int(minute)))
    
    channel = bot.get_channel(FORUM_CHANNEL_ID)
    if isinstance(channel, discord.ForumChannel):
        try:
            tags = [channel.available_tags[0]] if channel.available_tags else []
            thread = await channel.create_thread(
                name=f"【募集】{target_dt.strftime('%m/%d %H:%M')}～ ＠{map_name}", 
                content=f"開始日時: <t:{int(target_dt.timestamp())}:F>\nマップ: **{map_name}**", 
                applied_tags=tags
            )
            await interaction.followup.send(f"作成完了: {thread.thread.jump_url}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"エラー: {e}", ephemeral=True)
    else:
        await interaction.followup.send("⚠️ フォーラムチャンネルで実行してください。", ephemeral=True)

bot.run(TOKEN)