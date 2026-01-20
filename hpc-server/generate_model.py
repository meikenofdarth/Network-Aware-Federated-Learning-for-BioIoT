import torch
import torch.nn as nn
import torch.onnx
import os

class BioModel(nn.Module):
    def __init__(self):
        super(BioModel, self).__init__()
        self.lin = nn.Linear(1, 1)
        self.lin.weight.data = torch.tensor([[1.0]])
        self.lin.bias.data = torch.tensor([-80.0])
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        return self.sigmoid(self.lin(x))

model = BioModel()
dummy_input = torch.randn(1, 1)

# Save to the CURRENT directory (root) so Docker can see it
output_path = "bio_logic.onnx"
torch.onnx.export(model, dummy_input, output_path, 
                  input_names=['input'], output_names=['output'])

if os.path.exists(output_path):
    print(f"✅ Success: '{output_path}' generated in root directory.")
else:
    print("❌ Error: Failed to generate model.")