"""Q-LoRA Fine-Tuning Pipeline for Gemma-2B / MedGemma Mental Wellness LLM.

Uses 4-bit quantization (bitsandbytes), PEFT LoRA, and TRL SFTTrainer to fine-tune
an instruction-tuned causal language model on the mental health conversational SFT dataset.
"""
import os
import sys
import torch
import logging
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==============================================================================
# CONFIGURABLE HYPERPARAMETERS & PATHS
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_ID = "google/gemma-2b-it"  # Base model ID on Hugging Face (or medgemma checkpoint)
DATASET_PATH = os.path.join(BASE_DIR, "training", "data", "mental_health_sft.jsonl")
OUTPUT_DIR = os.path.join(BASE_DIR, "models", "medgemma_wellness_lora")

# LoRA Configuration
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]

# Training Arguments (Optimized for 6GB VRAM RTX 4050 GPU)
PER_DEVICE_TRAIN_BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 4
LEARNING_RATE = 2e-4
NUM_TRAIN_EPOCHS = 1
MAX_SEQ_LENGTH = 512
WARMUP_RATIO = 0.03
LOGGING_STEPS = 10
SAVE_STEPS = 100


def main():
    logger.info("Initializing QLoRA Fine-Tuning Setup...")

    # 1. Check GPU & CUDA Availability
    if not torch.cuda.is_available():
        logger.error("CUDA is not available! QLoRA training requires an NVIDIA GPU.")
        sys.exit(1)

    device_name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
    logger.info(f"Detected GPU: {device_name} ({vram_gb:.2f} GB VRAM)")

    # 2. Check Dataset File Existence
    if not os.path.exists(DATASET_PATH):
        logger.error(f"SFT Dataset file not found at: {DATASET_PATH}")
        logger.error("Please run 'python training/prepare_sft_dataset.py' first.")
        sys.exit(1)

    logger.info(f"Loading SFT dataset from: {DATASET_PATH}")
    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
    logger.info(f"Dataset loaded successfully with {len(dataset)} samples.")

    # 3. Configure 4-Bit BitsAndBytes Quantization
    logger.info("Configuring 4-bit NF4 Quantization (BitsAndBytes)...")
    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True,
    )

    # 4. Load Tokenizer & Model
    logger.info(f"Loading Base Tokenizer & Model from Hugging Face: '{MODEL_ID}'...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    # Enable Gradient Checkpointing & Prepare Model for k-bit Training
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    # 5. Configure PEFT LoRA Adapters
    logger.info("Setting up PEFT LoRA Configuration...")
    peft_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=TARGET_MODULES,
    )

    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 6. Configure Training Arguments
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    use_bf16 = torch.cuda.is_bf16_supported()
    use_fp16 = not use_bf16

    sft_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=PER_DEVICE_TRAIN_BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        num_train_epochs=NUM_TRAIN_EPOCHS,
        max_seq_length=MAX_SEQ_LENGTH,
        logging_steps=LOGGING_STEPS,
        save_steps=SAVE_STEPS,
        save_total_limit=2,
        fp16=use_fp16,
        bf16=use_bf16,
        optim="paged_adamw_8bit",
        warmup_ratio=WARMUP_RATIO,
        lr_scheduler_type="cosine",
        report_to="none",
    )

    # 7. Initialize TRL SFTTrainer
    logger.info("Initializing TRL SFTTrainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        processing_class=tokenizer,
        args=sft_args,
    )

    # 8. Start Fine-Tuning
    logger.info("Starting QLoRA Fine-Tuning Execution...")
    trainer.train()

    # 9. Save Fine-Tuned LoRA Adapter & Tokenizer
    logger.info(f"Fine-tuning complete! Saving LoRA adapters to: {OUTPUT_DIR}")
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    logger.info("Successfully exported LoRA adapter weights!")


if __name__ == "__main__":
    main()
