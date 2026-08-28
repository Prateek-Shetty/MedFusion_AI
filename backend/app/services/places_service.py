from urllib.parse import quote


class PlacesService:
    """
    Creates Google Maps search URLs for nearby medical specialists.

    No Google Maps API key is required.
    """

    # ========================================================
    # SPECIALIST SEARCH TERMS
    # ========================================================

    SPECIALIST_SEARCH_TERMS = {

        "Neurosurgery":
            "neurosurgery hospital",

        "Neuro-oncology":
            "neuro oncology hospital",

        "Endocrinology":
            "endocrinology hospital",

        "Neuroradiology":
            "neuroradiology hospital",
    }

    # ========================================================
    # CREATE GOOGLE MAPS SEARCH URL
    # ========================================================

    @staticmethod
    def create_maps_search_url(
        specialist: str,
        latitude: float,
        longitude: float,
    ) -> str:
        """
        Create a Google Maps search URL centered around the
        user's current latitude and longitude.

        Example search:

            neurosurgery hospital near 12.9716,77.5946
        """

        # ----------------------------------------------------
        # Get specialist-specific search term
        # ----------------------------------------------------

        search_term = (
            PlacesService.SPECIALIST_SEARCH_TERMS.get(
                specialist,
                specialist,
            )
        )

        # ----------------------------------------------------
        # Build search query
        # ----------------------------------------------------

        query = (
            f"{search_term} near "
            f"{latitude},{longitude}"
        )

        # ----------------------------------------------------
        # Encode query safely
        # ----------------------------------------------------

        encoded_query = quote(
            query
        )

        # ----------------------------------------------------
        # Return Google Maps URL
        # ----------------------------------------------------

        return (
            "https://www.google.com/maps/search/"
            "?api=1&query="
            + encoded_query
        )


# ============================================================
# GLOBAL SERVICE INSTANCE
# ============================================================

places_service = PlacesService()