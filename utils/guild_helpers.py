#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guild Helper Functions
Utilities for multi-guild data separation
"""

import discord
from typing import Optional


def get_guild_id(interaction: discord.Interaction) -> Optional[int]:
    """
    Get the guild ID from an interaction safely.
    
    Args:
        interaction: Discord interaction object
        
    Returns:
        Guild ID if in guild context, None otherwise
    """
    return interaction.guild.id if interaction.guild else None


def ensure_guild_context(interaction: discord.Interaction) -> bool:
    """
    Verify that interaction is in a guild context.
    
    Args:
        interaction: Discord interaction object
        
    Returns:
        True if in guild, False if in DM
    """
    return interaction.guild is not None

