"""Data management module for Excel-based storage."""
from .data_manager import (
    DataManager,
    load_data_on_startup,
    get_data_manager,
    save_working_data
)

__all__ = [
    "DataManager",
    "load_data_on_startup",
    "get_data_manager",
    "save_working_data"
]
