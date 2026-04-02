from ollama import chat

def test_llama_inference_using_mlx_backend():

    model_name = "llama3.2:3b"

    system_prompt = 'When user asks you the capital of a country always provide a single word answer.'
    test_input = 'Tell me the capital of France.'
    true_answer = "Paris"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": test_input}
    ]

    response = chat(
        model=model_name,
        messages=messages
    )

    assert response.message.role == 'assistant'
    assert response.message.content == true_answer
    