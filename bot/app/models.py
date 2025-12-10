# Все модели + платные/бесплатные
MODELS = {
    # ChatGPT
    "chatgpt_instant": {
        "provider": "ChatGPT",
        "name": "Instant",
        "paid": True,
    },
    "chatgpt_thinking": {
        "provider": "ChatGPT",
        "name": "Thinking",
        "paid": True,
    },
    "chatgpt_gpt5": {
        "provider": "ChatGPT",
        "name": "GPT-5",
        "paid": False,
    },

    "deepseek_default": {
        "provider": "Deepseek",
        "name": "Обычный",
        "paid": False,
    },
    "deepseek_thinking": {
        "provider": "Deepseek",
        "name": "Thinking",
        "paid": False,
    },

    "perplexity_search": {
        "provider": "Perplexity",
        "name": "Поиск",
        "paid": False,
    },
    "perplexity_research": {
        "provider": "Perplexity",
        "name": "Исследование",
        "paid": True,
    },
    "perplexity_labs": {
        "provider": "Perplexity",
        "name": "Лаборатории",
        "paid": True,
    },
}

# какие модели у какого семейства
PROVIDER_MODELS = {
    "chatgpt": [
        "chatgpt_instant",
        "chatgpt_thinking",
        "chatgpt_gpt5",
    ],
    "deepseek": [
        "deepseek_default",
        "deepseek_thinking",
    ],
    "perplexity": [
        "perplexity_search",
        "perplexity_research",
        "perplexity_labs",
    ],
}

PROVIDER_TITLES = {
    "chatgpt": "ChatGPT",
    "deepseek": "Deepseek",
    "perplexity": "Perplexity",
}