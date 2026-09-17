import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from typing import Optional

class TicketsPanel(commands.Cog):
    """Ticket panel system with persistent messages and buttons"""

    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'tickets_panel_config.json'
        self.load_config()

    def load_config(self):
        """Load panel configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            self.config = {}

    def save_config(self):
        """Save panel configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_panel_channel(self, guild_id: int) -> Optional[int]:
        """Get the ticket panel channel for a guild"""
        guild_key = str(guild_id)
        return self.config.get(guild_key, {}).get('panel_channel')

    def set_panel_channel(self, guild_id: int, channel_id: int):
        """Set the ticket panel channel"""
        guild_key = str(guild_id)
        if guild_key not in self.config:
            self.config[guild_key] = {}
        self.config[guild_key]['panel_channel'] = channel_id
        self.save_config()

    def get_panel_message_id(self, guild_id: int) -> Optional[int]:
        """Get the ticket panel message ID"""
        guild_key = str(guild_id)
        return self.config.get(guild_key, {}).get('panel_message_id')

    def set_panel_message_id(self, guild_id: int, message_id: int):
        """Set the ticket panel message ID"""
        guild_key = str(guild_id)
        if guild_key not in self.config:
            self.config[guild_key] = {}
        self.config[guild_key]['panel_message_id'] = message_id
        self.save_config()

    @app_commands.command(name='setticketpanel', description='Set the channel for the ticket panel (Admin only)')
    @app_commands.describe(channel='The channel to post the ticket panel')
    async def set_ticket_panel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the ticket panel channel and create the panel"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title='❌ Permission Denied',
                description='Only administrators can set the ticket panel',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Save channel
        self.set_panel_channel(interaction.guild_id, channel.id)

        # Create the panel embed
        panel_embed = discord.Embed(
            title='🎫 Tickets',
            description='To create a ticket use the **Create Ticket** button below',
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        panel_embed.add_field(
            name='🆘 Support System',
            value='Click the button below to create a support ticket. We\'re here to help!',
            inline=False
        )
        panel_embed.add_field(
            name='📌 Categories',
            value='🐛 **Bug** - Report a bug\n💡 **Feature** - Request a feature\n❓ **Support** - Get help\n📝 **General** - General inquiries',
            inline=False
        )
        panel_embed.set_footer(text='Your ticket will be reviewed by our support team')

        # Create button view
        view = TicketPanelView(self.bot)

        # Send the panel message
        try:
            message = await channel.send(embed=panel_embed, view=view)
            self.set_panel_message_id(interaction.guild_id, message.id)

            embed = discord.Embed(
                title='✅ Ticket Panel Created',
                description=f'Ticket panel has been created in {channel.mention}',
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name='Channel', value=channel.mention, inline=True)
            embed.add_field(name='Message ID', value=f'`{message.id}`', inline=True)
            embed.add_field(name='Status', value='🟢 Active', inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title='❌ Error',
                description=f'Failed to create panel: {str(e)}',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='viewticketpanel', description='View ticket panel settings (Admin only)')
    async def view_ticket_panel(self, interaction: discord.Interaction):
        """View the current ticket panel settings"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title='❌ Permission Denied',
                description='Only administrators can view panel settings',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        panel_channel_id = self.get_panel_channel(interaction.guild_id)
        panel_message_id = self.get_panel_message_id(interaction.guild_id)

        if not panel_channel_id:
            embed = discord.Embed(
                title='📭 No Ticket Panel',
                description='Use `/setticketpanel` to create a ticket panel',
                color=discord.Color.yellow(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            channel = await self.bot.fetch_channel(panel_channel_id)
            embed = discord.Embed(
                title='🎫 Ticket Panel Settings',
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            embed.add_field(name='Channel', value=channel.mention, inline=True)
            embed.add_field(name='Channel ID', value=f'`{panel_channel_id}`', inline=True)
            if panel_message_id:
                embed.add_field(name='Message ID', value=f'`{panel_message_id}`', inline=True)
            embed.add_field(name='Status', value='🟢 Active', inline=False)
            embed.set_footer(text='Panel is active and ready to use')
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            embed = discord.Embed(
                title='⚠️ Channel Not Found',
                description='The configured panel channel no longer exists. Use `/setticketpanel` to set a new one.',
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='deleteticketpanel', description='Delete the ticket panel (Admin only)')
    async def delete_ticket_panel(self, interaction: discord.Interaction):
        """Delete the ticket panel"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title='❌ Permission Denied',
                description='Only administrators can delete the ticket panel',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        panel_channel_id = self.get_panel_channel(interaction.guild_id)
        panel_message_id = self.get_panel_message_id(interaction.guild_id)

        if not panel_channel_id or not panel_message_id:
            embed = discord.Embed(
                title='❌ No Panel Found',
                description='No ticket panel has been created yet',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            channel = await self.bot.fetch_channel(panel_channel_id)
            message = await channel.fetch_message(panel_message_id)
            await message.delete()

            guild_key = str(interaction.guild_id)
            if guild_key in self.config:
                del self.config[guild_key]
                self.save_config()

            embed = discord.Embed(
                title='✅ Ticket Panel Deleted',
                description='The ticket panel has been removed',
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title='❌ Error',
                description=f'Failed to delete panel: {str(e)}',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


class TicketPanelView(discord.ui.View):
    """View for the ticket panel with Create Ticket button"""

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label='Create Ticket',
        style=discord.ButtonStyle.primary,
        emoji='🎫',
        custom_id='create_ticket_btn'
    )
    async def create_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle the create ticket button press"""
        # Get the Tickets cog
        tickets_cog = self.bot.get_cog('Tickets')

        if not tickets_cog:
            await interaction.response.send_message('❌ Tickets system not found', ephemeral=True)
            return

        # Show category selection
        await interaction.response.send_message(
            embed=discord.Embed(
                title='🎫 Create Ticket',
                description='Select a ticket category below',
                color=discord.Color.blurple()
            ),
            view=TicketCategoryView(self.bot),
            ephemeral=True
        )


class TicketCategoryView(discord.ui.View):
    """View for selecting ticket category"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.select(
        placeholder='Choose a ticket category...',
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label='🐛 Bug Report', value='bug', description='Report a bug or issue'),
            discord.SelectOption(label='💡 Feature Request', value='feature', description='Suggest a new feature'),
            discord.SelectOption(label='❓ Support', value='support', description='Get help or support'),
            discord.SelectOption(label='📝 General', value='general', description='General inquiries'),
        ]
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Handle category selection"""
        category = select.values[0]

        # Create modal for ticket creation
        class TicketCreateModal(discord.ui.Modal, title='Create Ticket'):
            title_input = discord.ui.TextInput(
                label='Ticket Title',
                placeholder='Brief description of your issue...',
                required=True,
                max_length=100
            )
            description_input = discord.ui.TextInput(
                label='Description',
                placeholder='Provide more details...',
                required=True,
                max_length=1000,
                style=discord.TextStyle.paragraph
            )

            async def on_submit(self, modal_interaction: discord.Interaction):
                tickets_cog = self.bot.get_cog('Tickets')
                if tickets_cog:
                    ticket_id = tickets_cog.create_ticket(
                        modal_interaction.user.id,
                        self.title_input.value,
                        self.description_input.value,
                        category,
                        modal_interaction.guild_id
                    )

                    embed = discord.Embed(
                        title='✅ Ticket Created',
                        description='Your support ticket has been created',
                        color=discord.Color.green()
                    )
                    embed.add_field(name='Ticket ID', value=f'`{ticket_id}`', inline=False)
                    embed.add_field(name='Category', value=category.capitalize(), inline=True)
                    embed.add_field(name='Title', value=self.title_input.value, inline=False)
                    embed.set_footer(text='Use /viewticket to check status')

                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)

        # Pass bot reference to modal
        modal = TicketCreateModal()
        modal.bot = self.bot
        await interaction.response.send_modal(modal)


async def setup(bot):
    await bot.add_cog(TicketsPanel(bot))
