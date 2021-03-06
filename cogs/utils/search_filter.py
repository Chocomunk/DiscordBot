import re

class InvalidSearch(Exception):
	def __init__(self, str, complaint=None):
		self.message = "Invalid Search: '{0}'{1}".format(str, (', '+complaint if complaint!=None else ''))
		Exception.__init__(self, self.message)

class InvalidParenthesis(InvalidSearch):
	def __init__(self, str):
		InvalidSearch.__init__(self, str, complaint="Invalid Parenthesis")

class InvalidCategorySearchStructure(InvalidSearch):
	def __init__(self, str):
		InvalidSearch.__init__(self, str, complaint="Invalid Category Search Structure")

class InvalidIsolatorStructure(InvalidSearch):
	def __init__(self, str):
		InvalidSearch.__init__(self, str, complaint="Invalid Isolator Structure")

class SearchFilter:
	
	def __init__(self, expression: str, custom_filters):
		self.custom_filters = custom_filters
		self.expr = self.replace_custom_filters(expression, custom_filters)

		filts = self.get_filters(self.expr)
		self.filters = self.compile_filters(filts)

		for i in filts:
			self.expr = self.expr.replace(i[0], "$$#%^#")
		self.expr = self.expr.strip().replace('[', '(').replace(']',')').replace('{','(').replace('}',')').replace('!$', '(not $$#%^#)').replace('$$#%^#','{:}')
	
	def get_filters(self, expr:str):
		filters = []
		curr_filt = ''
		s_e = False
		s_c = False
		s_c_c = False
		s_p = False
		a_c = False
		for c in expr:
			if c == '[' and not s_e:
				if s_c:
					raise InvalidCategorySearchStructure(expr)
				s_c = True
			elif c == ':' and not s_e:
				if not s_c or s_c_c:
					raise InvalidCategorySearchStructure(expr)
				s_c_c = True
				curr_filt += c
			elif c == ']' and not s_e:
				if not s_c or not s_c_c:
					raise InvalidCategorySearchStructure(expr)
				v = curr_filt.rstrip().lstrip()
				if v.strip()!='': filters.append((v, True))
				s_c = False
				s_c_c = False
				a_c = True
				curr_filt = ''
			elif c == '{' and not s_c:
				if s_e:
					raise InvalidIsolatorStructure(expr)
				s_e = True
			elif c == '}' and not s_c:
				if not s_e:
					raise InvalidIsolatorStructure(expr)
				v = curr_filt
				if v.strip()!='': filters.append((v, False))
				s_e = False
				curr_filt = ''
			elif c == '(':
				s_p = True
			elif c == ')':
				if not s_p:
					raise InvalidParenthesis(expr)
				s_p = False
			elif c in '&|':
				if not (s_e or s_c):
					if curr_filt.strip() == '' and not a_c:
						raise InvalidSearch(expr)
					v = curr_filt.rstrip().lstrip()
					if v.strip()!='': filters.append((v, False))
					curr_filt = ''
					a_c = False
				else:
					curr_filt += c
			elif c != "!":
				curr_filt += c
		if curr_filt.strip() != '':
			filters.append((curr_filt.rstrip().lstrip(), False))
		if s_e:
			raise InvalidIsolatorStructure(expr)
		if s_c:
			raise InvalidCategorySearchStructure(expr)
		if s_p:
			raise InvalidParenthesis(expr)
		return filters

	def compile_filters(self, filts: list):
		filters = []
		for s in filts:
			if s[1]:
				try:
					cat_search = [j.rstrip().lstrip() for j in s[0].split(':')]
					filters.append( ((cat_search[0] if cat_search[0].strip()!='' else None), cat_search[1]) )
				except IndexError:
					print(s)
			else:
				filters.append((None, s[0]))
		return filters

	def replace_custom_filters(self, expr: str, custom_filters):
		s_clear = False
		while(not s_clear):
			for f in custom_filters:
				expr = expr.replace(f, custom_filters[f])
			s_clear = True
			for f in custom_filters:
				s_clear = s_clear & (f not in expr)
		return expr

	def passes(self, inp: dict):
		if(self.expr == ""):
			return True
		else:
			comp = []
			for f in self.filters:
				res = False
				if f[0]!=None:
					k_f = SearchFilter(f[0], self.custom_filters)
					v_f = SearchFilter(f[1], self.custom_filters)
					for k,v in inp.items():
						res = res or (k_f.passes({'arg':k}) and v_f.passes({'arg':v}))
						if res:
							break
				else:
					for i in inp:
						res = res or (f[1].lower() in inp[i].lower())
						if res:
							break
				comp.append(res)
			result = eval(self.expr.format(*comp))
			return result