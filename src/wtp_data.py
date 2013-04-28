from json import JSONEncoder

class Petition:
	def __init__(self, id, title, signatures):
		self.id = id
		self.title = title
		self.signatures = signatures
		self.creation_date = ""
		self.text = ""
	
	def __hash__(self):
		return hash(self.id)

	def __eq__(self, other):
		return self.id == other.id

	def add_signature(self, sig):
		self.signatures.append(sig)

	def __str__(self):
		return self.id + " - " + str(self.signatures)

class PetitionEncoder(JSONEncoder):
	def __init__(self):
		super(PetitionEncoder, self).__init__(indent=2)

	def default(self, o):
		if isinstance(o, Petition):
			return o.__dict__
		return JSONEncoder.default(self, o)

def as_json(petitions):
	return PetitionEncoder().encode(petitions)

def load_hook(d):
	if d.has_key('id') and d.has_key('title'):
		p = Petition(d['id'], d['title'], d['signatures'])
		p.creation_date = d['creation_date']
		p.text = d['text']
		return p
	return d

# Example from http://code.activestate.com/recipes/499299/
class _CaptureEq:
    'Object wrapper that remembers "other" for successful equality tests.'
    def __init__(self, obj):
        self.obj = obj
        self.match = obj
    def __eq__(self, other):
        result = (self.obj == other)
        if result:
            self.match = other
        return result
    def __getattr__(self, name):  # support hash() or anything else needed by __contains__
        return getattr(self.obj, name)

def get_eq(container, item, default=None):
    '''Gets the specific container element matched by: "item in container".

    Useful for retreiving a canonical value equivalent to "item".  For example, a
    caching or interning application may require fetching a single representative
    instance from many possible equivalent instances).

    >>> get_equivalent(set([1, 2, 3]), 2.0)             # 2.0 is equivalent to 2
    2
    >>> get_equivalent([1, 2, 3], 4, default=0)
    0
    '''
    t = _CaptureEq(item)
    if t in container:
        return t.match
    return default