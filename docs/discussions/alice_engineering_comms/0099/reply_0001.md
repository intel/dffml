## 2022-11-27 @pdxjohnny Engineering Logs

- https://github.com/IntelAI/models/releases/tag/v2.9.0
  - > Supported Frameworks
    > - Intel® Optimizations for TensorFlow v2.10.0
    > - PyTorch v1.13.0 and Intel® Extension for PyTorch v1.13.0
    > - Intel® Extension for PyTorch v1.10.200+gpu
    > - Intel® Extension for TensorFlow v1.0.0
    >
    > New models
    > - PyTorch AphlaFold2
    > - New precisions BF32 and FP16 for PyTorch BERT Large
    >
    > New features
    >
    > - dGPU support for Intel® Data Center GPU Flex Series using Intel® Extension for PyTorch v1.10.200+gpu and Intel® Extension for TensorFlow v1.0.0
    > - Intel® Neural Compressor Int8 quantized models support for TensorFlow image recognitions topologies (ResNet50, ResNet101, MobileNet v1, Inception V3)
    > - Add support for running TensorFlow and PyTorch inference on Windows client
    > - Add support for running models on Ubuntu 22.04
    > - Updated Transfer Learning Jupyter notebooks
- TODO
  - [ ] Alice, wrap and distributed as PyPi packages all pretrained models from IntelAI/models
    - Automated package creation code for on demand packages: https://github.com/intel/dffml/blob/1513484a4bf829b86675dfb654408674495687d3/dffml/operation/stackstorm.py