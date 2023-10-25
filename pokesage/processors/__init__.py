"""Processor classes for PokeSage.

Classes:
    Processor: Abstract Processor class for other processor classes to extend from.
    ShowdownProcessor: Processor class for interpretting Showdown messages.
    ProgressState: Enum for the possible progress states for a processor.
"""

from .abstractprocessor import Processor, ProgressState
from .showdownprocessor import ShowdownProcessor
