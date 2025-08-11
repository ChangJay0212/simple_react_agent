import abc


class GenAIOperator(abc.ABC):
    @abc.abstractmethod
    def _connect(*args, **kwargs):
        """
        Abstract method to connect to a GenAI service.

        Args:
            *args: Positional arguments (implementation-defined).
            **kwargs: Keyword arguments (implementation-defined).

        Returns:
            Any: Connection object or status.
        """
        pass

    @abc.abstractmethod
    def chat(*args, **kwargs):
        """
        Abstract method to send a chat request to the GenAI service.

        Args:
            *args: Positional arguments (implementation-defined).
            **kwargs: Keyword arguments (implementation-defined).

        Returns:
            Any: Response from the GenAI service.
        """
        pass
