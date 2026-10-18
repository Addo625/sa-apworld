import unittest
from unittest import mock

from .. import Variables
from ..Options import DeathLinkTrigger
from ..deathlink import LinkState, on_state
from ..state import GameState
from .test_client import BASE, game_memory, received

GAME_OVER = DeathLinkTrigger.option_game_over
PLAYER = 0x3200000
PLAYER_STATE = PLAYER + Variables.ADDR_PLAYER_STATE[1]
PLAY = (Variables.PLAYER_STATE_PLAY).to_bytes(4, "little")
HIT = (Variables.PLAYER_STATE_HIT).to_bytes(4, "little")


def run(lives, in_game=True):
	return GameState(in_game, False, None, None, 1, 1, "Reimu", "Reimu A", lives, 40)


class TestOnState(unittest.TestCase):
	def test_life_lost_sends(self):
		self.assertTrue(on_state(run(2), run(1), LinkState()))

	def test_no_send_without_a_drop(self):
		link = LinkState()
		self.assertFalse(on_state(run(2), run(2), link))
		self.assertFalse(on_state(run(2), run(3), link))  # extend
		self.assertFalse(on_state(None, run(1), link))  # first poll

	def test_amnesty_forgives_then_sends(self):
		link = LinkState(amnesty=2)
		self.assertEqual([on_state(run(5), run(4), link) for _ in range(6)], [False, False, True] * 2)

	def test_game_over_trigger(self):
		link = LinkState(trigger=GAME_OVER)
		self.assertFalse(on_state(run(1), run(0), link))
		self.assertTrue(on_state(run(0), run(-1), link))  # probe 06 S10: game over is -1

	def test_game_over_with_stage_torn_down(self):
		self.assertTrue(on_state(run(0), run(-1, in_game=False), LinkState(trigger=GAME_OVER)))

	def test_game_over_counts_toward_amnesty(self):
		link = LinkState(trigger=GAME_OVER, amnesty=1)
		self.assertFalse(on_state(run(1), run(0), link))  # not a game over: not counted
		self.assertFalse(on_state(run(0), run(-1), link))
		self.assertTrue(on_state(run(0), run(-1), link))

	def test_no_send_on_menu_exit(self):
		link = LinkState()
		self.assertFalse(on_state(run(3), run(0, in_game=False), link))
		self.assertFalse(on_state(run(5, in_game=False), run(2), link))  # next run starts with fewer lives

	def test_no_send_after_game_over(self):
		self.assertFalse(on_state(run(-1), run(-1), LinkState()))

	def test_incoming_death_not_echoed(self):
		link = LinkState()
		link.incoming = True
		self.assertFalse(on_state(run(2), run(1), link))
		self.assertFalse(link.incoming)
		self.assertTrue(on_state(run(1), run(0), link))  # the next death is the player's own

	def test_unreadable_lives(self):
		self.assertFalse(on_state(run(2), run(None), LinkState()))


class ClientCase(unittest.IsolatedAsyncioTestCase):
	def context(self, *items):
		from ..Client import TouhouContext
		ctx = TouhouContext()
		ctx.patch_practice_lives = lambda controller, lives: None  # tested on its own (49)
		ctx.slot = 1
		ctx.items_received = received(*items)
		ctx.tags.add("DeathLink")
		ctx.deaths_sent = 0

		async def send_death(death_text=""):
			ctx.deaths_sent += 1
		ctx.send_death = send_death
		return ctx

	async def poll(self, ctx, lives, memory=None):
		memory = memory or game_memory(lives=lives)
		await ctx.poll(memory, run(lives), 0)
		return memory

	def received_death(self, ctx):
		ctx.on_deathlink({"time": 1.0, "source": "other"})


class TestClientDeathLink(ClientCase):
	async def test_own_death_sent(self):
		ctx = self.context()
		await self.poll(ctx, 2)
		await self.poll(ctx, 1)
		self.assertEqual(ctx.deaths_sent, 1)

	async def test_not_sent_without_tag(self):
		ctx = self.context()
		ctx.tags.discard("DeathLink")
		await self.poll(ctx, 2)
		await self.poll(ctx, 1)
		self.assertEqual(ctx.deaths_sent, 0)

	async def test_life_trap_is_not_a_death(self):
		from .. import traps
		ctx = self.context("-1 Life")
		with mock.patch.object(traps, "ENTER_DELAY", 0):
			await self.poll(ctx, 2)  # the trap writes 1
			await self.poll(ctx, 1)
		self.assertEqual(ctx.deaths_sent, 0)

	async def test_reattach_is_not_a_death(self):
		ctx = self.context()
		await self.poll(ctx, 5)
		await ctx.poll(game_memory(lives=2), None, 0)  # the game restarted: game_loop passes prev None
		self.assertEqual(ctx.deaths_sent, 0)

	async def test_connect_reads_options(self):
		ctx = self.context()
		ctx.tags.discard("DeathLink")
		ctx.on_package("Connected", {"slot_data": {"death_link": 1, "death_link_trigger": GAME_OVER, "death_link_amnesty": 3}})
		await ctx.update_death_link(True)  # what on_package schedules; the task needs a server to send
		self.assertIn("DeathLink", ctx.tags)
		self.assertEqual((ctx.link.trigger, ctx.link.amnesty), (GAME_OVER, 3))

class TestClientKill(ClientCase):
	def memory(self, player_state=PLAY):
		memory = game_memory(lives=2)
		memory.set(BASE + Variables.ADDR_PLAYER_PTR, PLAYER.to_bytes(4, "little"))
		memory.set(PLAYER_STATE, player_state)
		return memory

	async def test_kill_puts_the_player_in_the_hit_state(self):
		ctx = self.context()
		memory = self.memory()
		self.received_death(ctx)
		await self.poll(ctx, 2, memory)
		self.assertEqual(memory.writes, [(PLAYER_STATE, HIT)])
		await self.poll(ctx, 1)  # the player died
		self.assertEqual(ctx.deaths_sent, 0)  # not echoed
		self.assertFalse(ctx.link.incoming)

	async def test_kill_retried_only_after_a_pause(self):
		from .. import Client
		ctx = self.context()
		self.received_death(ctx)
		memory = self.memory()
		with mock.patch.object(Client, "time") as clock:
			for now in (100.0, 100.5, 100 + Client.KILL_RETRY_SECONDS):  # a deathbomb saved them: lives never drop
				clock.monotonic.return_value = now
				memory.set(PLAYER_STATE, PLAY)
				await self.poll(ctx, 2, memory)
		self.assertEqual(memory.writes, [(PLAYER_STATE, HIT)] * 2)  # at 100 and at the retry, not at 100.5

	async def test_receivedeath_command_kills(self):
		from ..Client import TouhouClientProcessor
		ctx = self.context()
		memory = self.memory()
		self.assertTrue(TouhouClientProcessor(ctx)._cmd_receivedeath())
		await self.poll(ctx, 2, memory)
		self.assertEqual(memory.writes, [(PLAYER_STATE, HIT)])

	async def test_receivedeath_needs_deathlink_on(self):
		from ..Client import TouhouClientProcessor
		ctx = self.context()
		ctx.tags.discard("DeathLink")
		self.assertFalse(TouhouClientProcessor(ctx)._cmd_receivedeath())
		self.assertFalse(ctx.link.incoming)

	async def test_kill_skips_a_player_not_in_play(self):
		ctx = self.context()
		memory = self.memory(player_state=(2).to_bytes(4, "little"))  # dying: hitting again would take a second life
		self.received_death(ctx)
		await self.poll(ctx, 2, memory)
		self.assertEqual(memory.writes, [])
		self.assertTrue(ctx.link.incoming)  # retried, e.g. once respawned

	async def test_deathlink_off_drops_waiting_death(self):
		from ..Client import TouhouClientProcessor
		ctx = self.context()
		self.received_death(ctx)
		TouhouClientProcessor(ctx)._cmd_deathlink("off")
		self.assertFalse(ctx.link.incoming)

	async def test_kill_waits_for_a_run(self):
		ctx = self.context()
		self.received_death(ctx)
		menu = self.memory()
		menu.set(BASE + Variables.ADDR_ENEMY_MANAGER, bytes(4))
		await ctx.poll(menu, None, 0)
		self.assertEqual(menu.writes, [])
		self.assertTrue(ctx.link.incoming)

	async def test_kill_without_a_player(self):
		ctx = self.context()
		memory = game_memory(lives=2)  # no player pointer: unreadable state
		self.received_death(ctx)
		await self.poll(ctx, 2, memory)
		self.assertEqual(memory.writes, [])
		self.assertTrue(ctx.link.incoming)


class TestCommands(unittest.IsolatedAsyncioTestCase):
	def processor(self):
		from ..Client import TouhouClientProcessor, TouhouContext
		return TouhouClientProcessor(TouhouContext())

	async def test_trigger_and_amnesty(self):
		processor = self.processor()
		self.assertTrue(processor._cmd_deathlink_trigger("game_over"))
		self.assertFalse(processor._cmd_deathlink_trigger("bogus"))
		self.assertFalse(processor._cmd_deathlink_trigger("random"))
		self.assertFalse(processor._cmd_deathlink("maybe"))
		self.assertTrue(processor._cmd_deathlink_amnesty("4"))
		self.assertFalse(processor._cmd_deathlink_amnesty("11"))
		self.assertEqual((processor.ctx.link.trigger, processor.ctx.link.amnesty), (GAME_OVER, 4))

	async def test_toggle(self):
		import asyncio
		processor = self.processor()
		processor._cmd_deathlink("on")
		await asyncio.sleep(0)
		self.assertIn("DeathLink", processor.ctx.tags)
		processor._cmd_deathlink("off")
		await asyncio.sleep(0)
		self.assertNotIn("DeathLink", processor.ctx.tags)
