# -*- coding: utf-8 -*-
"""lab2v4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dIDmlHf6e-AbZ9OQAj9b7gYwNmfVY104
"""

!nvidia-smi

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import numpy
import tensorflow as tf
import datetime
import keras
from keras.layers import *
from keras.optimizers import *
from keras.applications import *
from keras.models import Model
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.preprocessing.image import ImageDataGenerator
import sys
import os
from PIL import Image
from PIL import ImageFile
import h5py
import collections
from collections import Counter
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions

from google.colab import drive
drive.mount('/content/drive')

img_width = 150
img_height = 150
input_shape = (img_width, img_height,3)
batch_size = 200
nb_classes = 2
ImageFile.LOAD_TRUNCATED_IMAGES = True
train_dir = '/content/drive/MyDrive/catsANDdogs/data/train'
val_dir = '/content/drive/MyDrive/catsANDdogs/data/validation'

inc_model = Xception(input_shape=(img_width, img_height, 3), weights='imagenet', include_top=False)

for layer in inc_model.layers:
    layer.trainable = False

datagen = ImageDataGenerator(rescale=1./255)  #собственно, генератор
    
train_generator = datagen.flow_from_directory(train_dir,
                                              target_size=(150, 150),
                                              batch_size=batch_size,
                                              class_mode='categorical')

validation_generator = datagen.flow_from_directory(val_dir,
                                                  target_size=(150, 150),
                                                  batch_size=batch_size,
                                                  class_mode='categorical')

sample_training_images, _ = next(train_generator)

def plotImages(images_arr):
    fig, axes = plt.subplots(1, 5, figsize=(20,20))
    axes = axes.flatten()
    for img, ax in zip(images_arr, axes):
        ax.imshow(img)
    plt.tight_layout()
    plt.show()

plotImages(sample_training_images[:5])

x = inc_model.output
x = GlobalAveragePooling2D()(x)
predictions = Dense(nb_classes, activation='softmax')(x)
model = Model(inc_model.input, predictions)
model.summary()

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard

log_dir = "/content/drive/MyDrive/catsANDdogs/logs/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

model.compile(optimizer="rmsprop", loss='categorical_crossentropy', metrics=['accuracy'])

history = model.fit(train_generator,
                    steps_per_epoch = train_generator.n // batch_size,
                    epochs=7,
                    validation_data = validation_generator,
                    validation_steps = validation_generator.n // batch_size,
                    verbose=1,
                    callbacks = [tensorboard_callback])

# Commented out IPython magic to ensure Python compatibility.
# %tensorboard --logdir /content/drive/MyDrive/catsANDdogs/logs

model.save_weights("/content/drive/MyDrive/catsANDdogs/weights/wieghts.h5")
model.save("/content/drive/MyDrive/catsANDdogs/weights/model.h5")

model.load_weights("/content/drive/MyDrive/catsANDdogs/weights/wieghts.h5")

"""Определяем является ли мой кот котом по мнению сети"""

def print_picture(path):
  img = keras.preprocessing.image.load_img(path=path)
  plt.imshow(img)

#Class: Cat - 1, Dog - 0
def dog_cat_predict(model, image_file):
  img = keras.preprocessing.image.load_img(image_file,
    target_size=(150, 150))
  img_arr = np.expand_dims(img, axis=0) / 255.0
  result = model.predict(img_arr)
  if (result[0][0] > 0.5):
    plt.imshow(img)
    print("Cat: %.2f%%" % (result[0][0]*100)) #predict cat%
  if (result[0][0] < 0.5):
    plt.imshow(img)
    print("Dog: %.2f%%" % ((1-result[0][0])*100)) #predict dog%

model = tf.keras.models.load_model('/content/drive/MyDrive/catsANDdogs/weights/model.h5')
dog_cat_predict(model, "/content/drive/MyDrive/catsANDdogs/data/my_cat/1.jpg")

dog_cat_predict(model, "/content/drive/MyDrive/catsANDdogs/data/my_cat/2.jpg")

dog_cat_predict(model, "/content/drive/MyDrive/catsANDdogs/data/my_cat/4.jpg")

dog_cat_predict(model, "/content/drive/MyDrive/catsANDdogs/data/test/dogs/3006.jpg")

dog_cat_predict(model, "/content/drive/MyDrive/catsANDdogs/data/test/dogs/3008.jpg")

dog_cat_predict(model, "/content/drive/MyDrive/catsANDdogs/data/test/dogs/3011.jpg")

dog_cat_predict(model, "/content/drive/MyDrive/catsANDdogs/data/enot.jpg") #енот > кот

dog_cat_predict(model, "/content/drive/MyDrive/catsANDdogs/data/cat_dog.jpg")

dog_cat_predict(model, "/content/drive/MyDrive/catsANDdogs/data/cat_dog2.jpg")

test_datagen = ImageDataGenerator(rescale=1./255)
pred_generator = test_datagen.flow_from_directory('/content/drive/MyDrive/catsANDdogs/data/test',
                                                     target_size=(150,150),
                                                     batch_size=200,
                                                     class_mode='categorical')

model.evaluate(pred_generator)

"""Карта признаков (первые 5 слоев)"""

def drawFeatureMap(model_t, image_tensor):
  blocks = []

  for i, layer in enumerate(model_t.layers):
    if 'conv' in layer.name and not '_conv' in layer.name:
        blocks.append(i + 2)
  b = 0     
  for layer_index in blocks:
    model_f = keras.models.Model(inputs=model_t.inputs, 
                              outputs=model_t.layers[layer_index].output)
    
    feature_maps = model_f.predict(image_tensor)
    plt.figure(figsize=[150, 150])
    for i, feature_map in enumerate([feature_maps[0, :, :, j] for j in range(feature_maps.shape[-1])]):
      plt.subplot(20, 20, i+1, xticks=([]), yticks=([]))
      plt.imshow(feature_map, cmap='gray')
    plt.show()
    b+=1
    if (b == 5):
      break

import keras 
from keras.preprocessing.image import load_img, img_to_array, array_to_img

image_path = '/content/drive/MyDrive/catsANDdogs/data/my_cat/1.jpg'
img = keras.preprocessing.image.load_img(image_path,
    target_size=(150, 150))
tensor = np.expand_dims(img_to_array(img), axis=0) / 255.
plt.imshow(image)

drawFeatureMap(model, tensor)

"""Добавление шума"""

def get_noise(image):
  noise = np.random.normal(128, 20, (image.shape[0], image.shape[1]))
  return np.dstack((noise, noise, noise)).astype(np.uint8)

def set_noise(image):
  noise = get_noise(image)
  noise_image = cv2.add(image.astype(np.float64), noise.astype(np.float64))
  cv2.normalize(noise_image, noise_image, 0, 255, cv2.NORM_MINMAX)
  return noise_image

test_path = '/content/drive/MyDrive/catsANDdogs/data/test'
gen_noise = ImageDataGenerator(rescale=1./255, 
                                           preprocessing_function=set_normal_noise).flow_from_directory(test_path,
                                            target_size=(150,150),
                                            batch_size=200,)

import random
import cv2
from google.colab.patches import cv2_imshow
image_dirs = [
              os.path.join(test_path, 
                           'cats'),
              os.path.join(test_path, 
                           'dogs'),
]
for i, path in zip(list(range(0, 9, 3)),[os.path.join(dir, random.choice(os.listdir(dir))) for dir in image_dirs]):
  image = cv2.resize(cv2.imread(path), (250, 250))
  cv2_imshow(np.concatenate((image, get_noise(image), set_noise(image)), axis=1))

loss, accuracy = model.evaluate(gen_noise)