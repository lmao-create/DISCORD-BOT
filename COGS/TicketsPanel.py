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

        try:
            # Check if bot has permissions
            if not channel.permissions_for(interaction.guild.me).send_messages:
                embed = discord.Embed(
                    title='❌ Missing Permissions',
                    description=f'I don\'t have permission to send messages in {channel.mention}',
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
                description='To create a ticket click one of the buttons below',
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            panel_embed.add_field(
                name='🆘 Support System',
                value='Select a category and describe your issue. Our team will respond shortly.',
                inline=False
            )
            panel_embed.set_footer(text='Your ticket will be reviewed by our support team')

            # Create button view
            view = TicketPanelView(self.bot)

            # Send the panel message
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

        except discord.Forbidden:
            embed = discord.Embed(
                title='❌ Permission Error',
                description='I don\'t have permission to perform this action.',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title='❌ Error',
                description=f'Failed to create panel: {str(e)[:100]}',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            print(f'Error creating ticket panel: {e}')

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
    """View for the ticket panel with Create Ticket buttons for each category"""

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label='🐛 Bug',
        style=discord.ButtonStyle.red,
        custom_id='create_ticket_bug'
    )
    async def bug_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle bug ticket creation"""
        await self._create_ticket_modal(interaction, 'bug')

    @discord.ui.button(
        label='💡 Feature',
        style=discord.ButtonStyle.blurple,
        custom_id='create_ticket_feature'
    )
    async def feature_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle feature ticket creation"""
        await self._create_ticket_modal(interaction, 'feature')

    @discord.ui.button(
        label='❓ Support',
        style=discord.ButtonStyle.green,
        custom_id='create_ticket_support'
    )
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle support ticket creation"""
        await self._create_ticket_modal(interaction, 'support')

    @discord.ui.button(
        label='📝 General',
        style=discord.ButtonStyle.grey,
        custom_id='create_ticket_general'
    )
    async def general_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle general ticket creation"""
        await self._create_ticket_modal(interaction, 'general')

    async def _create_ticket_modal(self, interaction: discord.Interaction, category: str):
        """Show modal for ticket creation with pre-selected category"""
        try:
            tickets_cog = self.bot.get_cog('Tickets')

            if not tickets_cog:
                embed = discord.Embed(
                    title='❌ Error',
                    description='Tickets system not found. Please try again later.',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Create modal for ticket creation
            class TicketCreateModal(discord.ui.Modal, title=f'Create {category.capitalize()} Ticket'):
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
                    try:
                        # Validate inputs
                        if not self.title_input.value or not self.description_input.value:
                            error_embed = discord.Embed(
                                title='❌ Invalid Input',
                                description='Please fill in all required fields.',
                                color=discord.Color.red()
                            )
                            await modal_interaction.response.send_message(embed=error_embed, ephemeral=True)
                            return

                        if tickets_cog:
                            ticket_id = tickets_cog.create_ticket(
                                modal_interaction.user.id,
                                self.title_input.value,
                                self.description_input.value,
                                category,
                                modal_interaction.guild_id
                            )

                            # Success embed
                            embed = discord.Embed(
                                title='✅ Ticket Created Successfully',
                                description='Your support ticket has been created and our team will review it shortly.',
                                color=discord.Color.green(),
                                timestamp=datetime.now()
                            )
                            embed.add_field(name='Ticket ID', value=f'`{ticket_id}`', inline=False)
                            embed.add_field(name='Category', value=category.capitalize(), inline=True)
                            embed.add_field(name='Status', value='🟢 Open', inline=True)
                            embed.add_field(name='Title', value=self.title_input.value, inline=False)
                            embed.add_field(
                                name='📌 Note',
                                value='You can use `/viewticket` to check the status of your ticket.',
                                inline=False
                            )
                            embed.set_footer(text='Thank you for reaching out to our support team')

                            await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                        else:
                            error_embed = discord.Embed(
                                title='❌ Error',
                                description='Failed to create ticket. Tickets system not found.',
                                color=discord.Color.red()
                            )
                            await modal_interaction.response.send_message(embed=error_embed, ephemeral=True)

                    except Exception as e:
                        error_embed = discord.Embed(
                            title='❌ Something went wrong',
                            description=f'Failed to create ticket. Please try again later.',
                            color=discord.Color.red()
                        )
                        error_embed.add_field(name='Error Details', value=f'```{str(e)[:100]}```', inline=False)
                        try:
                            await modal_interaction.response.send_message(embed=error_embed, ephemeral=True)
                        except:
                            pass
                        print(f'Error creating ticket: {e}')

            modal = TicketCreateModal()
            await interaction.response.send_modal(modal)

        except Exception as e:
            print(f'Error in _create_ticket_modal: {e}')
            try:
                error_embed = discord.Embed(
                    title='❌ Error',
                    description='Failed to open ticket form. Please try again.',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
            except:
                pass


async def setup(bot):
    await bot.add_cog(TicketsPanel(bot))
