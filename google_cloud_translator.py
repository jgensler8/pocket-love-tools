from typing import List
from base_translator import BaseTranslator


class GoogleCloudTranslator(BaseTranslator):
    """
    Concrete implementation of BaseTranslator using the Google Cloud Translation API.
    """

    def __init__(self, project_id: str):
        """
        Initializes the GoogleCloudTranslator with the project ID.

        Args:
            project_id (str): The Google Cloud project ID.
        """
        from google.cloud import translate_v2 as translate

        self.client = translate.Client()
        self.project_id = project_id

    def translate_batch(
        self, texts: List[str], target_language: str = "en"
    ) -> List[str]:
        """
        Translates a batch of texts to the target language using the Google Cloud Translation API.

        Args:
            texts (List[str]): The list of texts to translate.
            target_language (str): The target language code (default: "en").

        Returns:
            List[str]: A list of translated texts.
        """
        if not texts:
            return []

        results = self.client.translate(
            texts, target_language=target_language, source_language="ja", format_="text"
        )

        return [result["translatedText"] for result in results]