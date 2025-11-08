# https://huggingface.co/facebook/mbart-large-50-many-to-many-mmt

from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

article_ja = "このゲームは"
# article_ja = "ko no - ge mu"

model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")

# The tokenizer needs to know the source language.
# For Japanese, the language code is "ja_XX".
tokenizer.src_lang = "ja_XX"

# Encode the Japanese text to get input tensors for the model.
encoded_ja = tokenizer(article_ja, return_tensors="pt")

# Generate the translation. We force the output to start with the
# token for English ("en_XX").
generated_tokens = model.generate(
    **encoded_ja,
    forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"]
)

# Decode the generated tokens to get the translated text.
translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
print(f"Original (ja): {article_ja}")
print(f"Translated (en): {translated_text[0]}")
