"""
Instagram Growth Suite
Sistema completo de automação para Instagram
"""

__version__ = "2.0.0"
__author__ = "Instagram Growth Suite"
__license__ = "MIT"

from .bot import InstagramBot
from .config import Config, config
from .utils import (
    HumanBehavior,
    RateLimiter,
    logger,
    safe_execute,
    print_banner,
    print_success,
    print_error,
    print_info,
    print_warning
)

__all__ = [
    'InstagramBot',
    'Config',
    'config',
    'HumanBehavior',
    'RateLimiter',
    'logger',
    'safe_execute',
    'print_banner',
    'print_success',
    'print_error',
    'print_info',
    'print_warning'
]
