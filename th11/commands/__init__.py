"""
The client's /commands, by kind. AP's CommandMeta merges the commands of processor base classes, so the client's
processor just inherits the three groups.
"""
from .debug import DebugCommands, log_build
from .links import LinkCommands
from .play import PlayCommands


class TouhouClientProcessor(PlayCommands, LinkCommands, DebugCommands):
	pass
