import logging
from typing import List
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from base_translator import BaseTranslator

class LiquidAITranslator(BaseTranslator):
    """
    Concrete implementation of BaseTranslator using the LiquidAI/LFM2-350M-ENJP-MT model.
    """
    def __init__(self, model_name: str = "LiquidAI/LFM2-350M-ENJP-MT"):
        """
        Initializes the LiquidAITranslator by loading the model and tokenizer.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )

    def translate_batch(self, texts: List[str]) -> List[str]:
        """
        Translates a batch of Japanese strings to English using the Liquid AI model.
        """
        if not texts:
            return []

        translated_texts = []
        for i, text in enumerate(texts):
            chat = [
                {"role": "system", "content": "Translate to English."},
                {"role": "user", "content": text}
            ]
            prompt = self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True).to(self.model.device)
            outputs = self.model.generate(**inputs, max_new_tokens=256, pad_token_id=self.tokenizer.eos_token_id)
            input_length = inputs.input_ids.shape[1]
            generated_tokens = outputs[0][input_length:]
            translated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            translated_texts.append(translated_text)
            logging.info(f"translated: {i}/{len(texts)}")
        return translated_texts