from django.db import models

class Entry(models.Model):
	headword = models.CharField("Perso-Arabic Headword", max_length=500)				# e.g. غنیمت
	latin_strict = models.CharField("Verbatim Latin Transliteration", max_length=500)	# e.g. ġnymt
	latin_phonetic = models.CharField("Phonetic Latin Transcription", max_length=500)	# e.g. ġanīmat

class AlternateSpelling(models.Model):
	entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
	persoarabic_alt = models.CharField("Alternate Spelling in Perso-Arabic", max_length=500)
	latinstrict_alt = models.CharField("Alternate Spelling in Verbatim Latin", max_length=500)

class PartOfSpeech(models.Model):
	abb = models.CharField("POS Abbreviation", max_length=50)	# e.g. N., V., Adj.
	name = models.CharField("POS Full Name", max_length=200)	# e.g. noun, verb, adjective
	description = models.TextField("POS Description")			# the usual, although useful for very specific Turkic grammar explanations

class Source(models.Model):
	# this is just temporary, saving more complicated stuff for later
	year = models.IntegerField("Year of Publication")
	shortname = models.CharField("Source Short Name", max_length=200) # Just for the UI, so people can identify the source
	identifier = models.CharField("Source Identifier", max_length=1000) # Unique identifiers, placeholder field, think ISBN, or NBN

class Definition(models.Model):
	entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
	pos = models.ForeignKey(PartOfSpeech, on_delete=models.CASCADE)
	definition_text = models.TextField("Definition Text")									# e.g. "booty, plunder, spoils of war"
	definition_source = models.ForeignKey(Source, on_delete=models.CASCADE)		

class UsageExample(models.Model):
	definition = models.ForeignKey(Definition, on_delete=models.CASCADE) 
	persoarabic_usage = models.TextField("Usage Example in Perso-Arabic")
	latinstrict_usage = models.TextField("Usage Example in Verbatim Latin")
	usage_source = models.ForeignKey(Source, on_delete=models.CASCADE)

class Language(models.Model):
	name = models.CharField("Language Name", max_length=200)		# e.g. Arabic, Old Turkic, Persian
	iso_code = models.CharField("ISO 639-3 Code", max_length=3)		# e.g. ara, ota, pes

class Etymology(models.Model):
	language = models.ForeignKey(Language, on_delete=models.CASCADE)	# e.g. from Arabic
	word = models.CharField("Source Word", max_length=500)				# e.g. غَنِيمَة

