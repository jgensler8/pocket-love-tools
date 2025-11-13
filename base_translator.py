import abc
from typing import List

class BaseTranslator(abc.ABC):
    """
    Abstract base class for translation services.

    """

    @abc.abstractmethod
    def translate_batch(self, texts: List[str]) -> List[str]:
        """Translates a list of strings from source to target language."""
        pass