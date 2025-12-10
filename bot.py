import discord
from discord.ext import commands
import requests
from datetime import datetime
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def check_website(url):
    """Check if a website is up or down"""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        start_time = datetime.now()
        response = requests.get(url, timeout=10, allow_redirects=True)
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'status': 'up',
            'code': response.status_code,
            'time': response_time,
            'url': url,
            'final_url': response.url
        }
    except requests.exceptions.Timeout:
        return {
            'status': 'down',
            'error': 'Request timed out (10s)',
            'url': url,
            'time': 0,
            'code': None
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'down',
            'error': 'Connection refused',
            'url': url,
            'time': 0,
            'code': None
        }
    except requests.exceptions.SSLError:
        return {
            'status': 'down',
            'error': 'SSL certificate error',
            'url': url,
            'time': 0,
            'code': None
        }
    except Exception as e:
        return {
            'status': 'down',
            'error': str(e)[:100],
            'url': url,
            'time': 0,
            'code': None
        }

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')
    print(f'Ready to check websites!')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="website status | !check"
        )
    )

@bot.command(name='check')
async def check(ctx, url: str = 'https://www.logged.tg/auth/unknowngu'):
    """Check if a website is up or down"""
    
    result = check_website(url)
    
    embed = discord.Embed(
        title='',
        description='## 🔥 ━━━━━━ SITE STATUS ━━━━━━ 🔥',
        color=0x2b2d31,
        timestamp=datetime.utcnow()
    )
    
    embed.set_thumbnail(url='https://64.media.tumblr.com/1e95052e26871747ac547c3f40b19d31/tumblr_o4q00xJyfy1u7gnm9o1_500.gif')
    
    domain_display = result['url'].replace('https://', '').replace('http://', '')
    
    if result['status'] == 'up':
        status_icon = '```diff\n+ ONLINE\n```'
        status_badge = '🟢'
    else:
        status_icon = '```diff\n- OFFLINE\n```'
        status_badge = '🔴'
    
    code_text = str(result['code']) if result['code'] else 'N/A'
    
    if result['time'] > 0:
        if result['time'] < 200:
            speed_rating = '▰▰▰▰▰ BLAZING'
            speed_icon = '⚡'
        elif result['time'] < 500:
            speed_rating = '▰▰▰▰▱ FAST'
            speed_icon = '🚀'
        elif result['time'] < 1000:
            speed_rating = '▰▰▰▱▱ NORMAL'
            speed_icon = '🏃'
        elif result['time'] < 2000:
            speed_rating = '▰▰▱▱▱ SLOW'
            speed_icon = '🐢'
        else:
            speed_rating = '▰▱▱▱▱ VERY SLOW'
            speed_icon = '🐌'
        time_text = f"`{result['time']:.2f}ms`"
    else:
        speed_rating = '▱▱▱▱▱ NO RESPONSE'
        speed_icon = '💀'
        time_text = '`0.00ms`'
    
    embed.add_field(
        name='┃ 🌐 Domain',
        value=f'```{domain_display}```',
        inline=False
    )
    
    embed.add_field(
        name=f'┃ {status_badge} Status',
        value=status_icon,
        inline=True
    )
    
    embed.add_field(
        name='┃ 📊 HTTP Code',
        value=f'```{code_text}```',
        inline=True
    )
    
    embed.add_field(
        name=f'┃ {speed_icon} Response Time',
        value=f'{time_text}\n`{speed_rating}`',
        inline=False
    )
    
    if result['status'] == 'down':
        embed.add_field(
            name='┃ ⚠️ Error Details',
            value=f"```fix\n{result.get('error', 'Unknown error')}\n```",
            inline=False
        )
    
    embed.set_footer(
        text=f'Requested by {ctx.author.name} • Powered by VIBE',
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    await ctx.send(embed=embed)

@check.error
async def check_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Missing URL',
            description='Please provide a website URL to check!',
            color=0xFFA500
        )
        embed.add_field(
            name='Usage',
            value='```!check <url>```\n**Example:**\n`!check google.com`\n`!check https://example.com`',
            inline=False
        )
        await ctx.send(embed=embed)

token = os.environ.get('DISCORD_BOT_TOKEN')
if not token:
    print("ERROR: DISCORD_BOT_TOKEN not found in environment variables!")
    print("Please add your Discord bot token as a secret.")
else:
    bot.run(token)
