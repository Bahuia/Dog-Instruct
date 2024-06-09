import json
import random
import fire
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
import re


template = "Below is an instruction that describes a task. "\
           "Write a response that appropriately completes the request."\
           "\n\n### Instruction:\n{}\n\n### Response:\n"
instruction_for_wrapping = "Design a task based on the given text.\n{}"


def convert_response_to_task(response: str):
    response = response.rstrip("</s>")
    pattern = re.compile(r'#(?P<instruction>instruction)#:(?P<instruction_content>.*?)(?=#input#| #output#|$)'
                         r'(#(?P<input>input)#:(?P<input_content>.*?)(?=#output#|$))?'
                         r'(#(?P<output>output)#:(?P<output_content>.*)|$)?', re.DOTALL)
    match = pattern.match(response)
    task = {}
    if match:
        task.update(match.groupdict())
        task.pop(None, None)  # Remove None key added by groupdict()
        task['instruction'] = task.pop('instruction_content', None).strip(" \"\n")
        task['input'] = task.pop('input_content', None).strip(' ').strip(" \"\n")
        task['output'] = task.pop('output_content', None).strip(' ').strip(" \"\n")
    return task


def main(
    base_model_path: str = "",
    lora_adapter_path: str = "",
    data_path: str = "document.json",
    output_path: str = "task.json",
    temperature: float = 0.0,
    top_p = 0.95,
    max_tokens = 2048
):

    examples = json.load(open(data_path))

    prompts = []
    for ex in examples:
        content = instruction_for_wrapping.format(ex['text'])
        prompt = template.format(content)
        prompts.append(prompt)

    sampling_params = SamplingParams(temperature=temperature,
                                     top_p=top_p,
                                     max_tokens=max_tokens)

    llm = LLM(model=base_model_path,
              enable_lora=True,
              max_model_len=max_tokens,
              gpu_memory_utilization=0.8)

    outputs = llm.generate(prompts,
                           sampling_params,
                           lora_request=LoRARequest("dog_adapter",
                                                    1,
                                                    lora_adapter_path))

    results = []
    for i, output in enumerate(outputs):
        prompt = output.prompt
        response = output.outputs[0].text.strip()

        try:
            task = convert_response_to_task(response)
        except:
            continue
        results.append(task)

    json.dump(results,
              open(output_path, 'w', encoding='utf-8'),
              indent=2,
              ensure_ascii=False)

if __name__ == '__main__':
    fire.Fire(main)
