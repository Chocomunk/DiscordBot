import os
from __main__ import send_cmd_help
from .utils.dataIO import fileIO
from .utils.search_filter import *
import discord
from discord.ext import commands
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import aiohttp

class Warframe:
	"""Warframe utility module"""

	def __init__(self, bot):
		self.bot = bot
		self.prime_filters = fileIO("data/warframe/prime_filters.json", "load")
		self.trader_filters = fileIO("data/warframe/trader_filters.json", "load")

	@commands.group(name="prime", pass_context=True)
	async def prime(self, ctx):
		"""Prime item's command"""
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)
			return

	@prime.command(name="list")
	async def _prime_list(self):
		"""Lists info for all prime items"""
		try:
			await self.bot.say("Gathering Item Data, Please wait ...")

			url = "http://warframe.wikia.com/wiki/Ducats/Prices"
			async with aiohttp.get(url) as response:
				so = BeautifulSoup(await response.text(), "html.parser")
			for s in self._parse_prime_table(SearchFilter("",[]), so):
				await self.bot.say(s)
		except:
			await self.bot.say("Couldn't load item info")

	@prime.command(name="search", pass_context=True)
	async def _prime_search(self, ctx, *filter):
		"""Searches for prime item info with a filter"""
		server = ctx.message.server
		if(len(filter) == 0):
			await send_cmd_help(ctx)
			return
		else:
			try:
				await self.bot.say("Gathering Item Data, Please wait ...")

				if server.id in self.prime_filters:
					filt = SearchFilter(" ".join(filter), self.prime_filters[server.id])
				else:
					filt = SearchFilter(" ".join(filter), [])

				url = "http://warframe.wikia.com/wiki/Ducats/Prices"
				async with aiohttp.get(url) as response:
					so = BeautifulSoup(await response.text(), "html.parser")
				for s in self._parse_prime_table(filt, so):
					await self.bot.say(s)
			except:
				await self.bot.say("Couldn't load item info")

	@prime.group(name="filters", pass_context=True)
	async def prime_filters(ctx):
		"""Options for Search Filters"""
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)
			return
		else:
			sub_cm = ctx.invoked_subcommand.name
			if ctx.command.name in sub_cm:
				sub_cm = sub_cm.strip(ctx.command.name)
			if sub_cm is "":
				await send_cmd_help(ctx)
				return
		
	@prime_filters.command(name="add", pass_context=True)
	async def _prime_filter_add(self, ctx, filter: str, *to_search):
		"""Adds a custom filter"""
		server = ctx.message.server
		if server.id not in self.prime_filters:
			self.prime_filters[server.id] = {}
		if filter == " ".join(to_search):
			await self.bot.say("Custom filter name cannot be the same as the filter")
			return
		if filter not in self.prime_filters[server.id]:
			val = " ".join(to_search)
			self.prime_filters[server.id][filter] = val
			fileIO("data/warframe/prime_filters.json", "save", self.prime_filters)
			await self.bot.say("Custom filter '{0}' added."
							   "It will correspond to the filter: '{1}'".format(filter, val))
		else:
			await self.bot.say("'{0}' already exists as a custom filter."
							   "'{0}' filters for: '{1}'".format(filter,self.prime_filters[server.id][filter]))

	@prime_filters.command(name="del", pass_context=True)
	async def _prime_filter_del(self, ctx, filter: str):
		"""Deletes a custom filter"""
		server = ctx.message.server
		if server.id in self.prime_filters:
			self.prime_filters[server.id].pop(filter, None)
			fileIO("data/warframe/prime_filters.json", "save", self.prime_filters)
		await self.bot.say("Deleted custom filter '{0}'".format(filter))

	@prime_filters.command(name="show", pass_context=True)
	async def _prime_filter_show(self, ctx, filter: str):
		"""Shows the what [filter] filters"""
		server = ctx.message.server
		if server.id in self.prime_filters:
			if filter in self.prime_filters[server.id]:
				await self.bot.say("'{0}' filters for '{1}".format(filter,self.prime_filters[server.id][filter]))
			else:
				await self.bot.say("Custom filter '{0}' does not exist on this server".format(filter))

	@prime_filters.command(name="list", pass_context=True)
	async def _prime_filter_list(self, ctx):
		"""Lists all custom filters"""
		server = ctx.message.server
		if server.id in self.prime_filters:
			if len(self.prime_filters[server.id]) > 0:
				message = "```Custom Filter list:\n"
				for f in sorted(self.prime_filters[server.id]):
					if len(message) + len(f) + 3 > 2000:
						await self.bot.say(message)
						message = "```\n"
					message += "\t{0:<15s}\t=\t{1:<}\n".format(f, self.prime_filters[server.id][f])
				if len(message) > 4:
					message += "```"
					await self.bot.say(message)
			else:
				await self.bot.say("This server does not have any filters")
		else:
			await self.bot.say("This server does not have any filters")

	@commands.group(name="voidtrader", pass_context="True")
	async def voidtrader(self, ctx):
		"""Provides information on Baro Ki'Teer"""
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)
			return

	@voidtrader.command(name="update")
	async def _trader_update(self):
		"""Provides update on Baro Ki'Teer"""
		try:
			await self.bot.say("Gathering Update Data, Please wait ...")

			url = "http://warframe.wikia.com/wiki/Baro_Ki'Teer"
			async with aiohttp.get(url) as response:
				so = BeautifulSoup(await response.text(), "html.parser")
			info = so.find('span', attrs={'data-toggle': '.post-countdown'}).find('span').get_text()

			await self.bot.say("Currently, the Void Trader is scheduled to arrive on {0}".format(info))
		except:
			await self.bot.say("Couldn't load item info")

	@voidtrader.command(name="list")
	async def _trader_list(self):
		"""Lists info for all trader items"""
		try:
			await self.bot.say("Gathering Item Data, Please wait ...")

			url = "http://warframe.wikia.com/wiki/Baro_Ki'Teer/Trades"
			async with aiohttp.get(url) as response:
				so = BeautifulSoup(await response.text(), "html.parser")
			for s in self._parse_trader_table(SearchFilter("",[]), so):
				await self.bot.say(s)
		except:
			await self.bot.say("Couldn't load item info")

	@voidtrader.command(name="search", pass_context=True)
	async def _trader_search(self, ctx, *filter):
		"""Searches for trader items with a filter"""
		server = ctx.message.server
		if(len(filter) == 0):
			await send_cmd_help(ctx)
			return
		else:
			try:
				await self.bot.say("Gathering Item Data, Please wait ...")

				if server.id in self.trader_filters:
					filt = SearchFilter(" ".join(filter), self.trader_filters[server.id])
				else:
					filt = SearchFilter(" ".join(filter), [])

				url = "http://warframe.wikia.com/wiki/Baro_Ki'Teer/Trades"
				async with aiohttp.get(url) as response:
					so = BeautifulSoup(await response.text(), "html.parser")
				for s in self._parse_trader_table(filt, so):
					await self.bot.say(s)
			except:
				await self.bot.say("Couldn't load item info")

	@voidtrader.group(name="filters", pass_context=True)
	async def trader_filters(ctx):
		"""Options for Search Filters"""
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)
			return
		else:
			sub_cm = ctx.invoked_subcommand.name
			if ctx.command.name in sub_cm:
				sub_cm = sub_cm.strip(ctx.command.name)
			if sub_cm is "":
				await send_cmd_help(ctx)
				return
		
	@trader_filters.command(name="add", pass_context=True)
	async def _trader_filter_add(self, ctx, filter: str, *to_search):
		"""Adds a custom filter"""
		server = ctx.message.server
		if server.id not in self.trader_filters:
			self.trader_filters[server.id] = {}
		if filter == " ".join(to_search):
			await self.bot.say("Custom filter name cannot be the same as the filter")
			return
		if filter not in self.trader_filters[server.id]:
			val = " ".join(to_search)
			self.trader_filters[server.id][filter] = val
			fileIO("data/warframe/trader_filters.json", "save", self.trader_filters)
			await self.bot.say("Custom filter '{0}' added."
							   "It will correspond to the filter: '{1}'".format(filter, val))
		else:
			await self.bot.say("'{0}' already exists as a custom filter."
							   "'{0}' filters for: '{1}'".format(filter,self.trader_filters[server.id][filter]))

	@trader_filters.command(name="del", pass_context=True)
	async def _trader_filter_del(self, ctx, filter: str):
		"""Deletes a custom filter"""
		server = ctx.message.server
		if server.id in self.trader_filters:
			self.trader_filters[server.id].pop(filter, None)
			fileIO("data/warframe/trader_filters.json", "save", self.trader_filters)
		await self.bot.say("Deleted custom filter '{0}'".format(filter))

	@trader_filters.command(name="show", pass_context=True)
	async def _trader_filter_show(self, ctx, filter: str):
		"""Shows the what [filter] filters"""
		server = ctx.message.server
		if server.id in self.trader_filters:
			if filter in self.trader_filters[server.id]:
				await self.bot.say("'{0}' filters for '{1}".format(filter,self.trader_filters[server.id][filter]))
			else:
				await self.bot.say("Custom filter '{0}' does not exist on this server".format(filter))

	@trader_filters.command(name="list", pass_context=True)
	async def _trader_filter_list(self, ctx):
		"""Lists all custom filters"""
		server = ctx.message.server
		if server.id in self.trader_filters:
			if len(self.trader_filters[server.id]) > 0:
				message = "```Custom Filter list:\n"
				for f in sorted(self.trader_filters[server.id]):
					if len(message) + len(f) + 3 > 2000:
						await self.bot.say(message)
						message = "```\n"
					message += "\t{0:<15s}\t=\t{1:<}\n".format(f, self.trader_filters[server.id][f])
				if len(message) > 4:
					message += "```"
					await self.bot.say(message)
			else:
				await self.bot.say("This server does not have any filters")
		else:
			await self.bot.say("This server does not have any filters")

	def _parse_prime_table(self, filter, so):
		rows = so.find(id="mw-customcollapsible-ducatsprices").find('table').find_all('tr')
		set = []
		msg = "```{:^25s}|{:^35s}|{:^2s}|{:^5s}\n".format("PART","DROP LOCATION","BP","CRAFT")
		del rows[0]
		for row in rows:
			cells = row.find_all('td')
			descriptors = cells[0].find_all('a')
			name = descriptors[1].get_text().rstrip()
			lcs = cells[1].get_text(separator='\n').splitlines()
			location = lcs[0]
			del lcs[0]
			for l in lcs:
				location += ", " + l
			blueprint_value = (cells[2].get_text().rstrip()[:2]).replace("N/","NA")
			crafted_value = (cells[3].get_text().rstrip()[:2]).replace("N/","NA")

			if filter.passes({'part|name|item': name,'drop location': location,'blueprint|bp': blueprint_value,'crafted value': crafted_value}):
				tmp = "{0:^25s}|{1:^35s}|{2:^2s}|{3:^5s}".format(name, location, blueprint_value, crafted_value)
				if len(msg) + len(tmp) + 3 > 2000:
					set.append(msg + "```")
					msg = "```\n"
				msg += tmp + "\n"
		if len(msg) > 4:
			msg += "```"
			set.append(msg)
		return set

	def _parse_trader_table(self, filter, so):
		rows = so.find(id="mw-customcollapsible-itemsale").find('table').find_all('tr')
		set = []
		msg = "```{:^40s}|{:^10s}|{:^8s}\n".format("ITEM","CREDITS","DUCATS")
		del rows[0]
		for row in rows:
			cells = row.find_all('td')
			descriptors = cells[0].find_all('a')
			prices = cells[1].find_all('span')

			name = descriptors[1].get_text().rstrip()
			credits = "C"+prices[0].get_text().rstrip()
			ducats = "D"+prices[1].get_text().rstrip()

			if filter.passes({'part|name|item': name,'credits': credits,'ducats': ducats}):
				tmp = "{:^40s}|{:^10s}|{:^8s}".format(name, credits, ducats)
				if len(msg) + len (tmp) + 3 > 2000:
					set.append(msg + "```")
					msg = "```\n"
				msg += tmp + "\n"
		if len(msg) > 4:
			msg += "```"
			set.append(msg)
		return set

def check_folder():
	if not os.path.exists("data/warframe"):
		print("Creating data/warframe folder...")
		os.makedirs("data/warframe")


def check_files():
	default = {}

	files = ["prime_filters", "trader_filters"]
	for f in files:
		loc = "data/warframe/{}.json".format(f)
		if not fileIO(loc, "check"):
			print("Creating default warframes's {}.json...".format(f))
			fileIO(loc, "save", default)

def setup(bot):
	check_folder()
	check_files()
	if soupAvailable:
		bot.add_cog(Warframe(bot))
	else:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")