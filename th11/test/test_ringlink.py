import asyncio
import unittest
from unittest import mock

from .. import Variables
from ..ringlink import delta, receive
from ..state import GameState
from .test_client import BASE, game_memory, received


def run(power, in_game=True, lives=2):
	return GameState(in_game, False, None, None, 1, 1, "Reimu", "Reimu A", lives, power)


def memory_with(power):
	memory = game_memory()
	memory.set(BASE + Variables.ADDR_POWER, power.to_bytes(4, "little"))
	return memory


class TestDelta(unittest.TestCase):
	def test_gain_and_loss(self):
		self.assertEqual(delta(run(40), run(43)), 3)  # one ring per 0.05 power, as in MoF
		self.assertEqual(delta(run(40), run(20)), -20)
		self.assertEqual(delta(run(40), run(40)), 0)

	def test_nothing_outside_a_run(self):
		self.assertEqual(delta(None, run(10)), 0)  # first poll
		self.assertEqual(delta(run(40), run(0, in_game=False)), 0)  # menu exit
		self.assertEqual(delta(run(0, in_game=False), run(40)), 0)  # a run starts
		self.assertEqual(delta(run(40, lives=0), run(30, lives=-1)), 0)  # game over

	def test_unreadable_power(self):
		self.assertEqual(delta(run(40), run(None)), 0)
		self.assertEqual(delta(run(None), run(40)), 0)


class TestReceive(unittest.TestCase):
	def test_adds_power(self):
		self.assertEqual(receive(run(40), 5), [(Variables.ADDR_POWER, 45)])
		self.assertEqual(receive(run(40), -5), [(Variables.ADDR_POWER, 35)])

	def test_capped_and_floored(self):
		self.assertEqual(receive(run(78), 5), [(Variables.ADDR_POWER, 80)])
		self.assertEqual(receive(run(3), -5), [(Variables.ADDR_POWER, 0)])
		self.assertEqual(receive(run(80), 5), [])
		self.assertEqual(receive(run(0), -5), [])

	def test_only_in_a_run(self):
		self.assertEqual(receive(run(40, in_game=False), 5), [])
		self.assertEqual(receive(run(40, lives=-1), 5), [])
		self.assertEqual(receive(run(None), 5), [])


class TestClientRingLink(unittest.IsolatedAsyncioTestCase):
	def context(self, *items):
		from ..Client import TouhouContext
		ctx = TouhouContext()
		ctx.slot = 1
		ctx.items_received = received(*items)
		ctx.tags.add("RingLink")
		ctx.bounced = []

		async def send_msgs(msgs):
			ctx.bounced += [msg["data"]["amount"] for msg in msgs if msg["cmd"] == "Bounce"]
		ctx.send_msgs = send_msgs
		return ctx

	async def poll(self, ctx, power, memory=None):
		memory = memory or memory_with(power)
		await ctx.poll(memory, run(power), 0)
		return memory

	def bounce(self, ctx, amount, source="other"):
		ctx.on_package("Bounced", {"tags": ["RingLink"], "data": {"time": 1.0, "source": source, "amount": amount}})

	async def test_own_change_sent(self):
		ctx = self.context()
		await self.poll(ctx, 40)
		await self.poll(ctx, 44)
		self.assertEqual(ctx.bounced, [4])

	async def test_not_sent_without_tag(self):
		ctx = self.context()
		ctx.tags.discard("RingLink")
		await self.poll(ctx, 40)
		await self.poll(ctx, 44)
		self.assertEqual(ctx.bounced, [])

	async def test_own_items_not_sent(self):
		ctx = self.context()
		await self.poll(ctx, 40)
		ctx.items_received = received("+0.50 Power")
		memory = await self.poll(ctx, 40)  # the item writes 50
		await self.poll(ctx, 50, memory)
		self.assertEqual(ctx.bounced, [])

	async def test_own_traps_not_sent(self):
		from .. import traps
		ctx = self.context("-50% Power")
		with mock.patch.object(traps, "ENTER_DELAY", 0):
			memory = await self.poll(ctx, 40)  # the trap writes 20
			await self.poll(ctx, 20, memory)
		self.assertEqual(ctx.bounced, [])

	async def test_received_applied_and_not_echoed(self):
		ctx = self.context()
		await self.poll(ctx, 40)
		self.bounce(ctx, 3)
		self.bounce(ctx, 2)
		memory = await self.poll(ctx, 40)
		self.assertEqual(memory.writes, [(BASE + Variables.ADDR_POWER, (45).to_bytes(4, "little"))])
		await self.poll(ctx, 45, memory)
		self.assertEqual(ctx.bounced, [])

	async def test_own_bounce_skipped(self):
		ctx = self.context()
		self.bounce(ctx, 3, source=ctx.ring_link_id)
		self.bounce(ctx, "3")  # malformed amounts from other clients are ignored
		self.assertEqual(ctx.rings, 0)

	async def test_received_outside_a_run_dropped(self):
		ctx = self.context()
		self.bounce(ctx, 3)
		menu = memory_with(40)
		menu.set(BASE + Variables.ADDR_ENEMY_MANAGER, bytes(4))
		await ctx.poll(menu, None, 0)
		self.assertEqual(menu.writes, [])
		memory = await self.poll(ctx, 40)
		self.assertEqual(memory.writes, [])

	async def test_connect_reads_option(self):
		ctx = self.context()
		ctx.tags.discard("RingLink")
		ctx.on_package("Connected", {"slot_data": {"ring_link": 1}})
		await ctx.update_ring_link(True)  # what on_package schedules; the task needs a server to send
		self.assertIn("RingLink", ctx.tags)

	async def test_toggle(self):
		from ..Client import TouhouClientProcessor, TouhouContext
		processor = TouhouClientProcessor(TouhouContext())
		self.assertFalse(processor._cmd_ringlink("maybe"))
		processor._cmd_ringlink("on")
		await asyncio.sleep(0)
		self.assertIn("RingLink", processor.ctx.tags)
		processor._cmd_ringlink("off")
		await asyncio.sleep(0)
		self.assertNotIn("RingLink", processor.ctx.tags)
