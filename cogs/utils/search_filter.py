import re

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