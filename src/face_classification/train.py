import torch
import typer
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from torch.profiler import profile, ProfilerActivity, tensorboard_trace_handler

from metric_tracker import MetricTracker
from model import PretrainedResNet34
from data import FaceDataset

app = typer.Typer()

# Hyperparameters
BATCH_SIZE = 32
EPOCHS = 10
USE_PROFILER = True

@app.command()
def train(batch_size: int = BATCH_SIZE, epochs: int = EPOCHS) -> None:
    if USE_PROFILER:
        with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True, profile_memory=True, on_trace_ready=tensorboard_trace_handler("./logs/PretrainedResNet34")) as prof:
            run_training(batch_size, epochs)
            # print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=10))
            # print(prof.key_averages(group_by_input_shape=True).table(sort_by="cpu_time_total", row_limit=30))
            prof.export_chrome_trace("./logs/train_trace.json")
    else:
        run_training(batch_size, epochs)

def run_training(batch_size: int, epochs: int) -> None:
    """Train our model on the Face Dataset."""
    print("Training day and night")

    train_set = FaceDataset(mode="train")
    val_set = FaceDataset(mode="val")
    train_dataloader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, num_workers=4)
    val_dataloader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, num_workers=4)

    model = PretrainedResNet34(num_classes=16)
    checkpoint_callback = ModelCheckpoint(
        monitor="val_acc",
        dirpath="checkpoints/",
        filename="model-{epoch:02d}-{val_acc:.2f}",
        save_top_k=3,
        mode="max",
    )
    metric_tracker = MetricTracker()

    trainer = Trainer(max_epochs=epochs, callbacks=[checkpoint_callback, metric_tracker], accelerator="auto")
    trainer.fit(model, train_dataloader, val_dataloaders=val_dataloader)
    print("Training finished")

if __name__ == "__main__":
    typer.run(train)
