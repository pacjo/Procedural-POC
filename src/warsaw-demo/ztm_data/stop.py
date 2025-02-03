class ZTMStop:
	"""Represents a single stop in the ZTM dataset."""

	zespol: int
	nazwa_zespolu: str
	slupek: int
	id_ulicy: int
	szer_geo: float
	dlug_geo: float
	kierunek: str
	obowiazuje_od: str

	def __init__(self, zespol: int, slupek: int, nazwa_zespolu: str, id_ulicy: int, szer_geo: float, dlug_geo: float, kierunek: str, obowiazuje_od: str):
		self.zespol = zespol
		self.slupek = slupek
		self.nazwa_zespolu = nazwa_zespolu
		self.id_ulicy = id_ulicy
		self.szer_geo = szer_geo
		self.dlug_geo = dlug_geo
		self.kierunek = kierunek
		self.obowiazuje_od = obowiazuje_od

	def __str__(self):
		return f'ZTMStop:\n\tzespol: {self.zespol}\n\tslupek: {self.slupek}\n\tnazwa zespolu: {self.nazwa_zespolu}\n\tid ulicy: {self.id_ulicy}\n\tlokalizacja: ({self.szer_geo}, {self.dlug_geo})\n\tkierunek: {self.kierunek}\n\tobowiazuje od: {self.obowiazuje_od}\n'

	@classmethod
	def create_from_json(cls, json_data):
		return cls(
			zespol = json_data[0]['value'],
			slupek = json_data[1]['value'],
			nazwa_zespolu = json_data[2]['value'],
			id_ulicy = json_data[3]['value'],
			szer_geo = float(json_data[4]['value']),
			dlug_geo = float(json_data[5]['value']),
			kierunek = json_data[6]['value'],
			obowiazuje_od = json_data[7]['value']
		)
