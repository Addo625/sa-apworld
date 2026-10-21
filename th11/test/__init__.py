from test.bases import WorldTestBase

from .. import DISPLAY_NAME


class TH11TestBase(WorldTestBase):
	game = DISPLAY_NAME

	def world_setup(self, *args, **kwargs):
		# Captures default to on since 24; the core tests count locations and fill without them unless they ask.
		self.options = {"spell_card_keys": False, **self.options}
		super().world_setup(*args, **kwargs)
