from mlx_lm import load, generate
import re


def extract_role_from_prediction(prediction:str) -> str:
    pattern = r'<\|start_header_id\|>(\w+)<\|end_header_id\|>'
    match = re.search(pattern, prediction)
    if not match:
        raise RuntimeError(f"Failed to parse role from prediction!! Role = {prediction}")
    return match.group(1)


def test_llama_inference_using_mlx_backend():

    model_name = "mlx-community/Llama-3.2-3B-Instruct-4bit"
    model, tokenizer = load(model_name)

    system_prompt = 'When user asks you the capital of a country always provide a single word answer.'
    test_input = 'Tell me the capital of France.'
    true_answer = "Paris"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": test_input}
    ]

    prompt = tokenizer.apply_chat_template(
        messages, return_dict=False
    )

    response = generate(model, tokenizer, prompt=prompt, verbose=True)

    # Parse out the output
    role = extract_role_from_prediction(response)
    predicted_answer = response.split('\n\n')[-1]

    assert role == 'assistant'
    assert true_answer == predicted_answer
    
