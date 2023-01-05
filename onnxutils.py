import torch 
import torch.onnx
import onnxruntime 
import numpy as np


def saveModelToOnnx(model, features, fileName):
    x = torch.randn(1, features, requires_grad=True)
    _ = model(x)
    torch.onnx.export(model, x, fileName, verbose=True, 
                input_names=['input'],
                output_names=['output'])


def loadModelFromOnnx(fileName):
    return onnxruntime.InferenceSession(fileName)

def getPrediction(onnxInferenceSession, x):
    ort_inputs = {onnxInferenceSession.get_inputs()[0].name: [x.astype(np.float32)]}
    logits = onnxInferenceSession.run(None, ort_inputs)[0]
    return np.argmax(logits)


def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()
