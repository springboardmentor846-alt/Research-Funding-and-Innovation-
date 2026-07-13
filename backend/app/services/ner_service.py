import spacy

class NERService:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def extract(self, text):

        doc = self.nlp(text)

        organizations = []
        persons = []
        locations = []

        for entity in doc.ents:

            if entity.label_ == "ORG":
                organizations.append(entity.text)

            elif entity.label_ == "PERSON":
                persons.append(entity.text)

            elif entity.label_ in ["GPE", "LOC"]:
                locations.append(entity.text)

        return {

            "organizations": list(set(organizations)),

            "persons": list(set(persons)),

            "locations": list(set(locations))
        }