from random import choice, randint
from names import firstnames, lastnames

def pod_name():
	return choice(firstnames) + '-' + choice(lastnames) + '-' + str(randint(1000,9999))

