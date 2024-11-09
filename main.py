from extract import Extractor
from extract.jdmLoad import JDMWordsStore

# jdm = JDMWordsStore("pute")

extractor = Extractor()

# extractor.display_words()

# # phrase = " l'aventure river Serment des Horaces is there Serment des Horaces"
phrase = "le petit chat boit du lait"
# phrase = "petit"
extractor(phrase)
# extractor.plot_graph()
