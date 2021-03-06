# -*- coding: utf-8 -*-
"""text-model-onnx-probability-test.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ywqO-j6L9Pk6jLTnFHxNEfveno8f20LD
"""

from google.colab import drive
drive.mount('/content/drive')

# install necessary libraries
!pip install onnxruntime
!pip install onnx
!pip3 install ktrain==0.26.4
!pip install tf2onnx
!pip install torch==1.5.0
!pip install transformers=='3.0.2'

!pip install 'h5py==2.10.0'

import onnxruntime
import numpy
import onnx
import tensorflow
import ktrain
from tensorflow.python.keras.models import load_model
import tf2onnx
import time
import numpy as np
import torch
from transformers import AutoTokenizer
from transformers.convert_graph_to_onnx import convert
from transformers import AutoModelForSequenceClassification
from pathlib import Path
from transformers import AutoTokenizer
import transformers
from scipy.special import softmax
import pandas as pd
transformers.__version__

# create ONNX session
def create_onnx_session(onnx_model_path, provider='CPUExecutionProvider'):
    """
    Creates ONNX inference session from provided onnx_model_path
    """

    from onnxruntime import GraphOptimizationLevel, InferenceSession, SessionOptions, get_all_providers
    assert provider in get_all_providers(), f"provider {provider} not found, {get_all_providers()}"

    # Few properties that might have an impact on performances (provided by MS)
    options = SessionOptions()
    options.intra_op_num_threads = 0
    options.graph_optimization_level = GraphOptimizationLevel.ORT_ENABLE_ALL

    # Load the model as a graph and prepare the CPU backend 
    session = InferenceSession(onnx_model_path, options, providers=[provider])
    session.disable_fallback()
    return session

data_of_comments = pd.read_csv('/content/drive/MyDrive/text_model_new/test_data_20220622_new.csv')

data_of_comments[:1000]

docs = data_of_comments[:1000]['emails_text_clean'].values.tolist()

docs

predictor = ktrain.load_predictor('/content/drive/MyDrive/text_model_new')
maxlen = predictor.preproc.maxlen
class_names = predictor.preproc.get_classes()

tokenizer = predictor.preproc.get_tokenizer()

sess = create_onnx_session("/content/drive/MyDrive/text_model_new_pt_onnx/model.onnx")
input = 'Give me money immediate this is not a spam I repeat'
tokens = tokenizer.encode_plus(input, max_length=maxlen, truncation=True)
tokens = {name: np.atleast_2d(value) for name, value in tokens.items()}
print()
print()
print("predicted class: %s" % (class_names[np.argmax(sess.run(None, tokens)[0])]))
softmax(sess.run(None,tokens)[0][0],axis=0)

prob_checker = 0

def isclose(a, b, rel_tol=1e-06, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


for i in docs:
  tokens = tokenizer(str(i), max_length=maxlen, truncation=True)
  tokens = {name: np.atleast_2d(value) for name, value in tokens.items()}
  prob_onnx = softmax(sess.run(None,tokens)[0][0],axis=0)
  prob_predictor = predictor.predict_proba(str(i))
  #For one test case checking both non spam and spam probabilities 
  if isclose(prob_onnx[0], prob_predictor[0]) and isclose(prob_onnx[1],prob_predictor[1]) == False:
    prob_checker = prob_checker + 1
print(prob_checker)

#For industry classifier
predictor = ktrain.load_predictor('/content/drive/MyDrive/predictor_industry_classifier_en')
maxlen = predictor.preproc.maxlen
class_names = predictor.preproc.get_classes()

tokenizer = predictor.preproc.get_tokenizer()

sess = create_onnx_session("/content/drive/MyDrive/predictor_industry_classifier_en_pt_onnx/model.onnx")
input = 'Give me money immediate this is not a spam I repeat'
tokens = tokenizer.encode_plus(input, max_length=maxlen, truncation=True)
tokens = {name: np.atleast_2d(value) for name, value in tokens.items()}
print()
print()
print("predicted class: %s" % (class_names[np.argmax(sess.run(None, tokens)[0])]))
softmax(sess.run(None,tokens)[0][0],axis=0)

predictor.predict_proba(input)

softmax(sess.run(None,tokens)[0][0],axis=0).sum()

predictor.predict_proba(input).sum()

