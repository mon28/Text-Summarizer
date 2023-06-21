import os
from transformers import (AutoModelForSeq2SeqLM, 
                          AutoTokenizer, 
                          DataCollatorForSeq2Seq,
                          TrainingArguments, 
                          Trainer)
from datasets import load_from_disk
import torch
from textSummarizer.entity import ModelTrainerConfig


class ModelTrainer(object):
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_ckpt = self.config.model_ckpt
        tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
        model_pegasus = AutoModelForSeq2SeqLM.from_pretrained(model_ckpt).to(device)
        seq2seq_data_collator = DataCollatorForSeq2Seq(tokenizer, model=model_pegasus)

        # loading dataset
        dataset_samsum_pt = load_from_disk(self.config.data_path)

        # initialize training args
        training_args = TrainingArguments(self.config.root_dir, num_train_epochs=self.config.num_train_epochs, 
                                          warmup_steps=self.config.warmup_steps, 
                                          per_device_train_batch_size=self.config.per_device_train_batch_size, 
                                          per_device_eval_batch_size=self.config.per_device_train_batch_size,
                                          weight_decay=self.config.weight_decay, logging_steps=self.config.logging_steps,
                                          evaluation_strategy=self.config.evaluation_strategy, 
                                          eval_steps=self.config.eval_steps, save_steps=self.config.save_steps,
                                          gradient_accumulation_steps=self.config.gradient_accumulation_steps
                                          )
        # begin training
        trainer = Trainer(
            model=model_pegasus, args=training_args, 
            tokenizer=tokenizer, data_collator=seq2seq_data_collator,
            train_dataset=dataset_samsum_pt["train"],
            eval_dataset=dataset_samsum_pt["validation"])
        
        trainer.train()

        # save model
        model_pegasus.save_pretrained(os.path.join(self.config.root_dir, "pegasus-samsum-model"))

        # save tokenizer
        tokenizer.save_pretrained(os.path.join(self.config.root_dir, "tokenizer"))