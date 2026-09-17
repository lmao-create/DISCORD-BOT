import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from typing import Optional
import uuid

class Tickets(commands.Cog):
    """Ticket management system for support and issues"""

    def __init__(self, bot):
        self.bot = bot
        self.tickets_file = 'tickets_data.json'
        self.tickets_config_file = 'tickets_config.json'
        self.load_tickets()
        self.load_config()

    def load_tickets(self):
        """Load tickets from JSON file"""
        if os.path.exists(self.tickets_file):
            try:
                with open(self.tickets_file, 'r') as f:
                    self.tickets = json.load(f)
            except:
                self.tickets = {}
        else:
            self.tickets = {}

    def save_tickets(self):
        """Save tickets to JSON file"""
        with open(self.tickets_file, 'w') as f:
            json.dump(self.tickets, f, indent=2)

    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.tickets_config_file):
            try:
                with open(self.tickets_config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            self.config = {}

    def save_config(self):
        """Save configuration to JSON file"""
        with open(self.tickets_config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def create_ticket(self, user_id: int, title: str, description: str,
                     category: str = 'general', guild_id: Optional[int] = None) -> str:
        """Create a new ticket"""
        ticket_id = str(uuid.uuid4())[:8]

        ticket_data = {
            'id': ticket_id,
            'user_id': user_id,
            'title': title,
            'description': description,
            'category': category,
            'status': 'open',
            'priority': 'medium',
            'assigned_to': None,
            'guild_id': guild_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'closed_at': None,
            'comments': []
        }

        self.tickets[ticket_id] = ticket_data
        self.save_tickets()
        return ticket_id

    def add_comment(self, ticket_id: str, user_id: int, username: str, content: str):
        """Add a comment to a ticket"""
        if ticket_id not in self.tickets:
            return False

        comment = {
            'id': str(uuid.uuid4())[:8],
            'user_id': user_id,
            'username': username,
            'content': content,
            'created_at': datetime.now().isoformat()
        }

        self.tickets[ticket_id]['comments'].append(comment)
        self.tickets[ticket_id]['updated_at'] = datetime.now().isoformat()
        self.save_tickets()
        return True

    def update_ticket_status(self, ticket_id: str, status: str):
        """Update ticket status"""
        if ticket_id not in self.tickets:
            return False

        self.tickets[ticket_id]['status'] = status
        self.tickets[ticket_id]['updated_at'] = datetime.now().isoformat()

        if status == 'closed':
            self.tickets[ticket_id]['closed_at'] = datetime.now().isoformat()

        self.save_tickets()
        return True

    def assign_ticket(self, ticket_id: str, user_id: int):
        """Assign ticket to a user"""
        if ticket_id not in self.tickets:
            return False

        self.tickets[ticket_id]['assigned_to'] = user_id
        self.tickets[ticket_id]['updated_at'] = datetime.now().isoformat()
        self.save_tickets()
        return True

    def set_ticket_priority(self, ticket_id: str, priority: str):
        """Set ticket priority"""
        if ticket_id not in self.tickets:
            return False

        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if priority not in valid_priorities:
            return False

        self.tickets[ticket_id]['priority'] = priority
        self.tickets[ticket_id]['updated_at'] = datetime.now().isoformat()
        self.save_tickets()
        return True

    @app_commands.command(name='createticket', description='Create a support ticket')
    @app_commands.describe(
        title='Ticket title',
        description='Ticket description',
        category='Ticket category (general, bug, feature, support)'
    )
    @app_commands.choices(category=[
        app_commands.Choice(name='General', value='general'),
        app_commands.Choice(name='Bug Report', value='bug'),
        app_commands.Choice(name='Feature Request', value='feature'),
        app_commands.Choice(name='Support', value='support')
    ])
    async def create_ticket(self, interaction: discord.Interaction, title: str,
                           description: str, category: str = 'general'):
        """Create a new support ticket"""
        ticket_id = self.create_ticket(
            interaction.user.id,
            title,
            description,
            category,
            interaction.guild_id
        )

        embed = discord.Embed(
            title='✅ Ticket Created',
            description=f'Your support ticket has been created',
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name='Ticket ID', value=f'`{ticket_id}`', inline=False)
        embed.add_field(name='Title', value=title, inline=True)
        embed.add_field(name='Category', value=category.capitalize(), inline=True)
        embed.add_field(name='Status', value='🟢 Open', inline=True)
        embed.add_field(name='Description', value=description[:256] + ('...' if len(description) > 256 else ''), inline=False)
        embed.set_footer(text='Use /viewticket to check status')

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='viewticket', description='View a ticket')
    @app_commands.describe(ticket_id='The ticket ID to view')
    async def view_ticket(self, interaction: discord.Interaction, ticket_id: str):
        """View ticket details"""
        if ticket_id not in self.tickets:
            embed = discord.Embed(
                title='❌ Ticket Not Found',
                description=f'No ticket found with ID: `{ticket_id}`',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        ticket = self.tickets[ticket_id]

        # Check permission
        if ticket['user_id'] != interaction.user.id and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title='❌ Permission Denied',
                description='You can only view your own tickets',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        status_colors = {
            'open': discord.Color.yellow(),
            'in_progress': discord.Color.blurple(),
            'closed': discord.Color.green(),
            'resolved': discord.Color.green()
        }

        embed = discord.Embed(
            title=f'🎫 {ticket["title"]}',
            description=ticket['description'],
            color=status_colors.get(ticket['status'], discord.Color.blurple()),
            timestamp=datetime.now()
        )
        embed.add_field(name='Ticket ID', value=f'`{ticket["id"]}`', inline=False)
        embed.add_field(name='Status', value=ticket['status'].capitalize(), inline=True)
        embed.add_field(name='Priority', value=ticket['priority'].capitalize(), inline=True)
        embed.add_field(name='Category', value=ticket['category'].capitalize(), inline=True)
        embed.add_field(name='Created', value=f"<t:{int(datetime.fromisoformat(ticket['created_at']).timestamp())}:R>", inline=True)
        embed.add_field(name='Last Updated', value=f"<t:{int(datetime.fromisoformat(ticket['updated_at']).timestamp())}:R>", inline=True)

        if ticket['assigned_to']:
            embed.add_field(name='Assigned To', value=f"<@{ticket['assigned_to']}>", inline=True)

        if ticket['comments']:
            comments_text = '\n'.join([f"**{c['username']}**: {c['content'][:50]}..." for c in ticket['comments'][-3:]])
            embed.add_field(name=f'Recent Comments ({len(ticket["comments"])})', value=comments_text, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='mytickets', description='View your tickets')
    async def my_tickets(self, interaction: discord.Interaction):
        """View user's tickets"""
        user_tickets = [t for t in self.tickets.values() if t['user_id'] == interaction.user.id]

        if not user_tickets:
            embed = discord.Embed(
                title='📋 My Tickets',
                description='You have not created any tickets yet',
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title='📋 My Tickets',
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )

        for ticket in user_tickets[-10:]:
            status_emoji = '🟢' if ticket['status'] == 'open' else '🔵' if ticket['status'] == 'in_progress' else '⚫'
            embed.add_field(
                name=f'{status_emoji} {ticket["title"][:50]}',
                value=f"ID: `{ticket['id']}`\nStatus: {ticket['status'].capitalize()}\nCreated: <t:{int(datetime.fromisoformat(ticket['created_at']).timestamp())}:R>",
                inline=False
            )

        embed.set_footer(text=f'Total: {len(user_tickets)} tickets')
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='alltickets', description='View all tickets (Admin only)')
    async def all_tickets(self, interaction: discord.Interaction):
        """View all tickets"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title='❌ Permission Denied',
                description='Only administrators can view all tickets',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not self.tickets:
            embed = discord.Embed(
                title='📋 All Tickets',
                description='No tickets have been created yet',
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title='📋 All Tickets',
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )

        open_count = len([t for t in self.tickets.values() if t['status'] == 'open'])
        in_progress = len([t for t in self.tickets.values() if t['status'] == 'in_progress'])
        closed = len([t for t in self.tickets.values() if t['status'] == 'closed'])

        embed.add_field(
            name='📊 Summary',
            value=f'**Open**: {open_count}\n**In Progress**: {in_progress}\n**Closed**: {closed}',
            inline=False
        )

        # Show recent tickets
        recent = sorted(self.tickets.values(), key=lambda x: x['created_at'], reverse=True)[:10]

        for ticket in recent:
            status_emoji = '🟢' if ticket['status'] == 'open' else '🔵' if ticket['status'] == 'in_progress' else '⚫'
            embed.add_field(
                name=f'{status_emoji} {ticket["title"][:40]}',
                value=f"ID: `{ticket['id']}`\nCategory: {ticket['category'].capitalize()}\nCreated: <t:{int(datetime.fromisoformat(ticket['created_at']).timestamp())}:R>",
                inline=False
            )

        embed.set_footer(text=f'Total: {len(self.tickets)} tickets | Showing 10 most recent')
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='closeticket', description='Close a ticket')
    @app_commands.describe(ticket_id='The ticket ID to close')
    async def close_ticket(self, interaction: discord.Interaction, ticket_id: str):
        """Close a ticket"""
        if ticket_id not in self.tickets:
            embed = discord.Embed(
                title='❌ Ticket Not Found',
                description=f'No ticket found with ID: `{ticket_id}`',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        ticket = self.tickets[ticket_id]

        # Check permission
        if ticket['user_id'] != interaction.user.id and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title='❌ Permission Denied',
                description='You can only close your own tickets',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.update_ticket_status(ticket_id, 'closed')

        embed = discord.Embed(
            title='✅ Ticket Closed',
            description=f'Ticket `{ticket_id}` has been closed',
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name='Title', value=ticket['title'], inline=False)
        embed.add_field(name='Closed By', value=interaction.user.mention, inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
