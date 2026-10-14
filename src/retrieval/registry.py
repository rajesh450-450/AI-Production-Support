from src.retrieval.providers.base import RetrievalProvider


class ProviderRegistry:
    """
    Internal registry used by RetrievalPipeline.

    This class is intentionally simple and is not exposed
    outside the retrieval subsystem.
    """

    def __init__(self):
        self._providers: dict[str, RetrievalProvider] = {}

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(self, provider: RetrievalProvider) -> None:
        """
        Register a retrieval provider.

        Raises:
            ValueError:
                If a provider with the same name
                is already registered.
        """

        if provider.provider_name in self._providers:
            raise ValueError(
                f"Provider '{provider.provider_name}' is already registered."
            )

        self._providers[provider.provider_name] = provider

    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def providers(self) -> list[RetrievalProvider]:
        """
        Return all registered providers.
        """

        return list(self._providers.values())

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all providers.
        """

        self._providers.clear()

    def count(self) -> int:
        """
        Return number of registered providers.
        """

        return len(self._providers)