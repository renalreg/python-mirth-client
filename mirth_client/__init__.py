"""
Main module containing the MirthAPI class for interacting with a Mirth instance
"""

from .channels import Channel
from .mirth import MirthAPI

__all__ = ["MirthAPI", "Channel"]
