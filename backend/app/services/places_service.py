from urllib.parse import quote


class PlacesService:
    """
    Creates Google Maps search URLs for nearby medical specialists.

    No Google Maps API key is required.
    """

    SPECIALIST_SEARCH_TERMS = {
        "Neurosurgery": "neurosurgery",
        "Neuro-oncology": "neuro oncology",
        "Endocrinology": "endocrinology",
        "Neuroradiology": "neuroradiology",
    }

    @staticmethod
    def create_maps_search_url(
        specialist: str,
        latitude: float,
        longitude: float,
    ) -> str:

        search_term = (
            PlacesService.SPECIALIST_SEARCH_TERMS.get(
                specialist,
                specialist,
            )
        )

        query = (
            f"{search_term} near "
            f"{latitude},{longitude}"
        )

        return (
            "https://www.google.com/maps/search/"
            "?api=1&query="
            + quote(query)
        )


places_service = PlacesService()

