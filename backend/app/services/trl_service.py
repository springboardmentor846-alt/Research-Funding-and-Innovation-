class TRLService:

    def __init__(self):

        self.rules = {

            1: [
                "basic research",
                "fundamental research",
                "scientific principles"
            ],

            2: [
                "concept",
                "formulation",
                "hypothesis"
            ],

            3: [
                "proof of concept",
                "proof-of-concept",
                "feasibility study"
            ],

            4: [
                "laboratory validation",
                "lab validation",
                "experimental validation"
            ],

            5: [
                "prototype",
                "prototype developed",
                "pilot implementation"
            ],

            6: [
                "prototype demonstrated",
                "demonstration",
                "field testing"
            ],

            7: [
                "operational environment",
                "real-world testing",
                "system prototype"
            ],

            8: [
                "production ready",
                "qualified system",
                "commercial prototype"
            ],

            9: [
                "commercial deployment",
                "market ready",
                "commercialized",
                "full deployment"
            ]

        }

    def detect(self, text: str):

        if not text:
            return 1

        text = text.lower()

        detected = 1

        for trl, keywords in self.rules.items():

            for keyword in keywords:

                if keyword in text:

                    detected = max(detected, trl)

        return detected