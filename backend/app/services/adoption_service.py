class AdoptionService:

    def score(
        self,
        stars,
        forks,
        watchers
    ):

        score = (

            stars * 0.5 +

            forks * 0.3 +

            watchers * 0.2

        )

        return round(score)