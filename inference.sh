
CUDA_VISIBLE_DEVICES=0 python inference.py \
    --base_model_path Llama-2-7b-hf \
    --lora_adapter_path dog-instruct-wrapper-7b-lora \
    --data_path document.json \
    --output_path task.json \
    --temperature 0.0 \
    --top_p 0.95 \
    --max_tokens 2048
