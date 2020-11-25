legend = {
	"D": "dalnice najezd",
	"D1": "dalnice",
	"D1-END": "konec dalnice",
	"ZO": "zacatek obce",
	"ZO-END": "konec obce",
	"X": "krizovatka",
	"KO": "kruhovy objezd",
	"PR": "prechod"
}

krizovatka = {
	"S": "so svetelnou signalizaciou",
	"B": "bez svetelnej signalizacie",
	"L": "vlavo",
	"P": "vpravo",
	"R": "rovne",
	"T": "stykova",
	"X": "prusecna",
	"Y": "vidlicova",
	"H-H": "hlavni-hlavni",
	"H-V": "hlavni-vedlejsi",
	"V-V": "vedlejsi-vedlejsi",
	"V-H": "vedlejsi-hlavni"
}

crossing = {
	"S": "nasvetleny",
	"N": "nenasvetleny",
	"S": "so svetelnou signalizaciou",
	"B": "bez svetelnej signalizacie"
}

def parse_crossing(record):
	pass


def parse_crossroads(record):
	pass


def parse_roundabout(record):
	pass


def parse_record(record):
	if record[0] == "X":
		return parse_crossroads(record)
	elif record[:2] == "KO":
		return parse_roundabout(record)
	elif record[:2] == "PR":
		return parse_crossing(record)
	else:
		return legend.get(record, None)	 

