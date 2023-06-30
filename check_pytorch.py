import torch

print("PyTorch version:", torch.__version__)
print("CUDA version:", torch.version.cuda)
print("cuDNN version:", torch.backends.cudnn.version())

if torch.cuda.is_available():
    device = torch.device("cuda")          # a CUDA device object
    print('PyTorch is using the GPU')
    print("GPU name:", torch.cuda.get_device_name(device))
else:
    device = torch.device("cpu")
    print('PyTorch is using the CPU')
