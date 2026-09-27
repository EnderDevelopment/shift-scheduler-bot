import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class ShiftBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

        async def setup_hook(self):
            await self.tree.sync()

            bot = ShiftBot()

            @bot.event
            async def on_ready():
                print(f'Logged in as {bot.user}')

                @bot.tree.command(name='shift', description='Create a new shift')
                async def shift(interaction: discord.Interaction):
                    modal = ShiftModal()
                    await interaction.response.send_modal(modal)

                    class ShiftModal(discord.ui.Modal, title='Shift Details'):
                        time = discord.ui.TextInput(label='Shift Time', placeholder='Enter the shift time')
                        duration = discord.ui.TextInput(label='Shift Duration', placeholder='Enter the shift duration')
                        type = discord.ui.TextInput(label='Shift Type', placeholder='Enter the shift type (Promotional/Normal)')
                        title = discord.ui.TextInput(label='Shift Title', placeholder='Enter the shift title')
                        host = discord.ui.TextInput(label='Shift Host', placeholder='Enter the shift host')

                        async def on_submit(self, interaction: discord.Interaction):
                            shift_time = self.time.value
                            shift_duration = self.duration.value
                            shift_type = self.type.value
                            shift_title = self.title.value
                            shift_host = self.host.value

                            embed = discord.Embed(title=shift_title, description=f'Shift Type: {shift_type}\nShift Host: {shift_host}\nShift Time: {shift_time}\nShift Duration: {shift_duration}', color=discord.Color.green())
                            view = ShiftView(shift_time, shift_duration, shift_type, shift_title, shift_host)
                            await interaction.response.send_message(embed=embed, view=view)

                            class ShiftView(discord.ui.View):
                                def __init__(self, shift_time, shift_duration, shift_type, shift_title, shift_host):
                                    super().__init__()
                                    self.shift_time = shift_time
                                    self.shift_duration = shift_duration
                                    self.shift_type = shift_type
                                    self.shift_title = shift_title
                                    self.shift_host = shift_host

                                    @discord.ui.button(label='Subscribe', style=discord.ButtonStyle.green)
                                    async def subscribe(self, interaction: discord.Interaction, button: discord.ui.Button):
                                        user = interaction.user
                                        await user.send(f'You will receive all information about the shift: {self.shift_title}')
                                        await interaction.response.send_message(f'{user.mention} has subscribed to the shift!', ephemeral=True)

                                        # Schedule a reminder 5 minutes before the shift
                                        reminder_time = discord.utils.parse_time(self.shift_time) - discord.utils.timedelta(minutes=5)
                                        if reminder_time > discord.utils.utcnow():
                                            await discord.utils.sleep_until(reminder_time)
                                            await user.send(f'The shift {self.shift_title} is in 5 minutes!')

                                            bot.run(TOKEN)
