import torch
import omegaconf

# Allowlist the global if you trust it
torch.serialization.add_safe_globals([omegaconf.listconfig.ListConfig])

def upgrade_checkpoint(file):
    # Load the checkpoint with CPU mapping and weights_only set to False
    checkpoint = torch.load(file, map_location=torch.device('cpu'), weights_only=False)
    # Perform any necessary upgrades here
    # Save the upgraded checkpoint
    torch.save(checkpoint, file)

def main():
    # Replace with the actual path to your checkpoint file
    file = 'C:\\Python310\\lib\\site-packages\\whisperx\\assets\\pytorch_model.bin'
    upgrade_checkpoint(file)

if __name__ == "__main__":
    main()