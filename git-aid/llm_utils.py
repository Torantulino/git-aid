import openai

def message_llm(
        system_prompt: str,
        prompt: str,
        model="gpt-4",
        temperature=0.7,
        max_tokens=3000,
    ):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0]['message']['content'].strip()