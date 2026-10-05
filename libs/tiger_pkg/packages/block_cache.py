from typing import Callable
from dataclasses import dataclass


@dataclass
class Cached_Block:
	epoch: int
	data: bytes


class Block_Cache:
	max_blocks: int
	blocks: dict[int, Cached_Block]
	epoch: int

	def __init__(self):
		self.max_blocks = 32  # maybe less or more?
		self.blocks = {}
		self.epoch = 0

	def get(self, block_index: int, reader: Callable[[int], bytes]) -> bytes:
		if block_index in self.blocks:
			return self.blocks[block_index].data

		data: bytes = reader(block_index)

		self.blocks[block_index] = Cached_Block(
			self.epoch,
			data
		)

		self.epoch += 1

		if len(self.blocks) > self.max_blocks:
			oldest = min(
				self.blocks,
				key=lambda k: self.blocks[k].epoch
			)
			del self.blocks[oldest]

		return data
