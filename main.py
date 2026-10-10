import discord
from discord.ext import commands
from discord import app_commands
import datetime
import pytz
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# --- Webサーバーのダミー処理 ---
def run_dummy_server():
    # Renderは PORT という環境変数を指定してくるので、それを使う
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# Bot起動の前にサーバーを起動する
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- ここから下のBotの処理はそのまま！ ---
TOKEN = os.environ.get('DISCORD_TOKEN')

# --- 設定 ---
FORUM_CHANNEL_ID = 1490645851733889147 # フォーラムのID

JST = pytz.timezone('Asia/Tokyo')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# ① 日付の候補を動的に作る関数
async def date_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    choices = []
    today = datetime.datetime.now(JST).date()
    
    # 今日から21日分（または必要な日数分）の選択肢を動的に生成
    for i in range(21):
        d = today + datetime.timedelta(days=i)
        day_str = d.strftime("%Y-%m-%d")  # 内部の値 (例: "2026-10-11")
        
        # 表示名を作る (例: "10/11(日)(今日)")
        name = f"{d.month}/{d.day}({'月火水木金土日'[d.weekday()]})"
        if i == 0:
            name += "(今日)"
            
        choices.append(app_commands.Choice(name=name, value=day_str))
        
    return choices

@bot.tree.command(name="募集", description="対戦募集を開始します")
@app_commands.describe(date="日付", hour="時間", minute="分", map_name="マップ")
@app_commands.autocomplete(date=date_autocomplete)  # ← ここで動的関数を指定！
@app_commands.choices(
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
    app_commands.Choice(name="炎都ビステア", value="炎都ビステア"),
    app_commands.Choice(name="炎の神殿", value="炎の神殿"),
    app_commands.Choice(name="古の大水門", value="古の大水門"),
    app_commands.Choice(name="水の神殿跡", value="水の神殿跡"),
    app_commands.Choice(name="闇神の神殿", value="闇神の神殿"),
    app_commands.Choice(name="闇神ノンデス", value="闇神ノンデス"),
    app_commands.Choice(name="天空庭園半壊", value="天空庭園半壊"),
    app_commands.Choice(name="ロータリー", value="ロータリー"),
    app_commands.Choice(name="ザエイト", value="ザエイト"),
    app_commands.Choice(name="ダブルハート", value="ダブルハート"),
    app_commands.Choice(name="モルフォ", value="モルフォ"),
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
                content=f"**募集主: {interaction.user.mention}**\n\n開始日時: <t:{int(target_dt.timestamp())}:F>\nマップ: **{map_name}**\n\n参加希望の方はこのスレに書込みしてください！", 
                applied_tags=tags
            )
            await interaction.followup.send(f"作成完了: {thread.thread.jump_url}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"エラー: {e}", ephemeral=True)
    else:
        await interaction.followup.send("⚠️ フォーラムチャンネルで実行してください。", ephemeral=True)

bot.run(TOKEN)
