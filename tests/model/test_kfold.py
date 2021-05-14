import unittest
import asyncio
import pathlib
from random import randrange

from dffml import *


class Kfold:
	async def split(
		self, source, fold_size, *args
	):  # Will split the data into required number of folds
		fold = list()
		split_data = list()
		async for record in load(source):
			fold.append(record.export())
			if len(fold) >= fold_size:
				split_data.append(fold)
				fold=[]
		return split_data

class TestKfoldTechnique(unittest.TestCase):
	def test_split(self):
		records=[Record("1",data={"features":{"A":0,"B":1}}),Record("2",data={"features":{"A":3,"B":4}}),Record("3",data={"features":{"A":1,"B":2}}),Record("4",data={"features":{"A":5,"B":3}})]
		memory_source = Sources(MemorySource(MemorySourceConfig(records=records)))
		x=Kfold()
		y=asyncio.run(x.split(memory_source,2))
		self.assertEqual(len(y),2)