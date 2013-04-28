from json import JSONEncoder

class Petition:
	def __init__(self, id="", title="", signatures=0):
		self.id = id
		self.title = title
		self.signatures = signatures
		self.creation_date = ""

class PetitionEncoder(JSONEncoder):
	def default(self, o):
		if isinstance(o, Petition):
			return o.__dict__
		return JSONEncoder.default(self, o)