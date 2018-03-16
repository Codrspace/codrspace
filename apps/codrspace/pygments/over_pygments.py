import random

css_classes_to_recolor = set(["s-Atom", "n", "na", "nc", "no", "nd", "ni", "ne", "nf", "nl", "nn", "nt", "nv", "vc", "vg", "vi"])

RED_RANGE = 128
RED_MINIMUM = 35
GREEN_RANGE = 128
GREEN_MINIMUM = 30
BLUE_RANGE = 128
BLUE_MINIMUM = 35


def add_colors_to( text ):
	def color_of( word ):
		def to_ff(x):
			y = hex( x )
			if x < 16:
				return "0"+y[-2]
			else:
				return y[-3:-1]
	
		random.seed(word)
		word_n = random.getrandbits(24)
		r = (word_n % RED_RANGE) + RED_MINIMUM
		g = ( (word_n >> 8) % GREEN_RANGE) + GREEN_MINIMUM
		b = ( (word_n >> 16) % BLUE_RANGE) + BLUE_MINIMUM
		return to_ff(r) + to_ff(g) + to_ff(b)


	split_by_span = text.split('</span>')
	recolored_pieces = []
	for piece in split_by_span[:-1]:
		split_by_bracket = piece.split('>')
		word = split_by_bracket[-1]
		class_name = split_by_bracket[-2].split('\"')[-2]
		if class_name in css_classes_to_recolor:
			old = 'class=\"' + class_name + '\"'
			new = 'style=\"color:#' + color_of(word) + ';\"'
			recolored_pieces += [piece.replace(old, new)]
		else:
			recolored_pieces += [piece]
	recolored_pieces += [split_by_span[-1]]
	return '</span>'.join(recolored_pieces)
