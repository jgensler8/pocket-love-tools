# https://huggingface.co/facebook/mbart-large-50-many-to-many-mmt

from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

def facebook():
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


# second model
from transformers import T5ForConditionalGeneration, T5Tokenizer

def madlad():
    model_name = 'jbochi/madlad400-3b-mt'
    model = T5ForConditionalGeneration.from_pretrained(model_name, device_map="auto")
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    texts = ["<2en> このゲームは", "<2en> こえを かけようとすると\nはずかしそうに にげていった..."]
    for text in texts:
        input_ids = tokenizer(text, return_tensors="pt", padding=True).input_ids.to(model.device)
        outputs = model.generate(input_ids=input_ids,
            repetition_penalty=2.0,          # Apply a penalty to repeated tokens
            no_repeat_ngram_size=5,          # Prevent repeating 5-word phrases
            max_new_tokens=256, # Set this high enough for a long sentence
            num_beams=3,
            do_sample=False)
        translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"out: {translated}")


from transformers import pipeline
def fugumt():
    fugu_translator = pipeline('translation', model='staka/fugumt-ja-en')
    translated = fugu_translator('このゲームは')
    print(f"out: {translated}")
    translated = fugu_translator('こえを かけようとすると\nはずかしそうに にげていった...')
    print(f"out: {translated}")


def opus():
    opus_translator = pipeline('translation', model='Helsinki-NLP/opus-mt-mul-en')
    translated = opus_translator('このゲームは')
    print(f"out: {translated}")
    translated = opus_translator('こえを かけようとすると\nはずかしそうに にげていった...')
    print(f"out: {translated}")

def facebook_2():
    nllb_translator = pipeline(task='translation', model='facebook/nllb-200-distilled-1.3B', src_lang="jpn_Jpan", tgt_lang="eng_Latn",)
    translated = nllb_translator('このゲームは')
    print(f"out: {translated}")
    translated = nllb_translator('こえを かけようとすると\nはずかしそうに にげていった...')
    print(f"out: {translated}")

def liquid():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch

    model_name = "LiquidAI/LFM2-350M-ENJP-MT"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="auto")

    texts_to_translate = ['このゲームは', 'こえを かけようとすると\nはずかしそうに にげていった...']

    for text in texts_to_translate:
        chat = [
            {"role": "system", "content": "Translate to English."},
            {"role": "user", "content": text}
        ]
        prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt", padding=True).to(model.device)

        outputs = model.generate(**inputs, max_new_tokens=256, pad_token_id=tokenizer.eos_token_id)
        # To get only the translated text, we decode the output tokens that come after the input tokens.
        input_length = inputs.input_ids.shape[1]
        generated_tokens = outputs[0][input_length:]
        translated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        print(f"out: {translated_text}")

# facebook()
# madlad()
# fugumt()
# opus()
#facebook_2()
liquid()