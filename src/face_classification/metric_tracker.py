import pytorch_lightning as pl
import torch
import wandb
from pytorch_lightning.callbacks import Callback

wandb.login()
wandb_logger = pl.loggers.WandbLogger(project="face_classification")


class MetricTracker(Callback):
    """Metric tracker for logging metrics to wandb"""

    def __init__(self, val_samples, num_samples=8):
        super().__init__()
        self.val_imgs, self.val_labels = val_samples
        self.val_imgs = self.val_imgs[:num_samples]
        self.val_labels = self.val_labels[:num_samples]

    def on_validation_epoch_end(self, trainer, pl_module):
        val_imgs = self.val_imgs.to(device=pl_module.device)

        logits = pl_module(val_imgs)
        preds = torch.argmax(logits, 1)

        trainer.logger.experiment.log(
            {
                "examples": [
                    wandb.Image(x, caption=f"Pred:{pred}, Label:{y}")
                    for x, pred, y in zip(val_imgs, preds, self.val_labels)
                ],
                "global_step": trainer.global_step,
            }
        )
