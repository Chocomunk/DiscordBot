import re
import os
from __main__ import send_cmd_help
from .utils.dataIO import fileIO
import discord
from discord.ext import commands
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import aiohttp

class PrimeList:
	"""My custom cog that does stuff!"""

	def __init__(self, bot):
		self.bot = bot
		self.filters = fileIO("data/warframe/filters.json", "load")

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
			for s in self._parse_table(SearchFilter("",[]), so):
				output = "```" + "\n".join(s) + "```"
				await self.bot.say(output)
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

				if server.id in self.filters:
					filt = SearchFilter("".join(filter), self.filters[server.id])
				else:
					filt = SearchFilter("".join(filter), [])

				url = "http://warframe.wikia.com/wiki/Ducats/Prices"
				async with aiohttp.get(url) as response:
					so = BeautifulSoup(await response.text(), "html.parser")
				for s in self._parse_table(filt, so):
					output = "```" + "\n".join(s) + "```"
					await self.bot.say(output)
			except:
				await self.bot.say("Couldn't load item info")

	@prime.group(name="filters", pass_context=True)
	async def prime_filters(self, ctx):
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
		if server.id not in self.filters:
			self.filters[server.id] = {}
		if filter not in self.filters[server.id]:
			val = "".join(to_search)
			self.filters[server.id][filter] = val
			fileIO("data/warframe/filters.json", "save", self.filters)
			await self.bot.say("Custom filter '{0}' added."
							   "It will correspond to the filter: '{1}'".format(filter, val))
		else:
			await self.bot.say("'{0}' already exists as a custom filter."
							   "'{0}' filters for: '{1}'".format(filter,self.filters[server.id][filter]))

	@prime_filters.command(name="del", pass_context=True)
	async def _prime_filter_del(self, ctx, filter: str):
		"""Deletes a custom filter"""
		server = ctx.message.server
		if server.id in self.filters:
			self.filters[server.id].pop(filter, None)
			fileIO("data/warframe/filters.json", "save", self.filters)
		await self.bot.say("Deleted custom filter '{0}'".format(filter))

	@prime_filters.command(name="show", pass_context=True)
	async def _prime_filter_show(self, ctx, filter: str):
		"""Shows the what [filter] filters"""
		server = ctx.message.server
		if server.id in self.filters:
			if filter in self.filters[server.id]:
				await self.bot.say("'{0}' filters for '{1}".format(filter,self.filters[server.id][filter]))
			else:
				await self.bot.say("Custom filter '{0}' does not exist on this server".format(filter))

	@prime_filters.command(name="list", pass_context=True)
	async def _prime_filter_list(self, ctx):
		"""Lists all custom filters"""
		server = ctx.message.server
		if server.id in self.filters:
			message = "```Custom Filter list:\n"
			for f in sorted(self.filters[server.id]):
				if len(message) + len(f) + 3 > 2000:
					await self.bot.say(message)
					message = "```\n"
				message += "\t{0:<15s}\t=\t{1:<}\n".format(f, self.filters[server.id][f])
			if len(message) > 4:
				message += "```"
				await self.bot.say(message)

	def _parse_table(self, filter, so):
		rows = so.find(id="mw-customcollapsible-ducatsprices").find('table').find_all('tr')
		set = []
		set.append(["{:^25s}|{:^35s}|{:^4s}|{:^4s}".format("PART","DROP LOCATION","BP","CRAFT")])
		temp = []
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

			if filter.passes([name,location,blueprint_value,crafted_value]):
				if len(temp) == 20:
					set.append(list(temp))
					temp = []
				temp.append("{:^25s}|{:^35s}|{:^4s}|{:^4s}".format(name, location, blueprint_value, crafted_value))
		set.append(list(temp))
		return set

class SearchFilter:
	
	def __init__(self, expression: str, custom_filters):
		self.expr = expression
		s_clear = False
		while(not s_clear):
			for f in custom_filters:
				self.expr = self.expr.replace(f, custom_filters[f])
			s_clear = True
			for f in custom_filters:
				s_clear = s_clear & (f not in self.expr)

		self.filters = [i.rstrip().lstrip() for i in re.split('[()&|!]', self.expr) if i.strip()!='']
		for i in self.filters:
			self.expr = self.expr.replace(i, "{:}")
		self.expr = self.expr.strip()
		self.expr = self.expr.replace('!{:}', '( not {:})')
				
	def passes(self, inp: list):
		if(self.expr == ""):
			return True
		else:
			comp = []
			for f in self.filters:
				res = False
				for i in inp:
					res = res or (f.lower() in i.lower())
					if res:
						break
				comp.append(res)
			result = eval(self.expr.format(*comp))
			return result
			
def check_folder():
	if not os.path.exists("data/warframe"):
		print("Creating data/warframe folder...")
		os.makedirs("data/warframe")


def check_files():
	filters = {}

	f = "data/warframe/filters.json"
	if not fileIO(f, "check"):
		print("Creating default warframes's filters.json...")
		fileIO(f, "save", filters)

def setup(bot):
	check_folder()
	check_files()
	if soupAvailable:
		bot.add_cog(PrimeList(bot))
	else:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")