'''This is a reproduction of the IRNN experiment
with pixel-by-pixel sequential MNIST in
"A Simple Way to Initialize Recurrent Networks of Rectified Linear Units"
by Quoc V. Le, Navdeep Jaitly, Geoffrey E. Hinton

arXiv:1504.00941v2 [cs.NE] 7 Apr 201
http://arxiv.org/pdf/1504.00941v2.pdf

Optimizer is replaced with RMSprop which yields more stable and steady
improvement.

Reaches 0.93 train/test accuracy after 900 epochs
(which roughly corresponds to 1687500 steps in the original paper.)
'''

from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.initializations import normal, identity
from keras.layers.recurrent import SimpleRNN, LSTM
from keras.optimizers import RMSprop
from keras.utils import np_utils

from keras.models import model_from_json
import json


def im2Window(image,wSize):
    xdim    = image.shape[1] - wSize + 1
    ydim    = image.shape[0] - wSize + 1
    #numWins = xdim*ydim
    output  = []
    [ output.append(np.ndarray.flatten(image[y:y+wSize,x:x+wSize]))  for y in range(0,ydim) for x in range(0,xdim)]
    return np.array(output)

def autoEncode(image,wSize,model):
    xdim    = image.shape[1] - wSize + 1
    ydim    = image.shape[0] - wSize + 1
    #numWins = xdim*ydim
    output  = []
    #print(image[0:0+wSize,0:0+wSize])
    #temp    = np.reshape(np.ndarray.flatten(image[0:0+wSize,0:0+wSize]),(1,wSize**2))
    
    #print(model.predict(temp))
    #print("I did it")
    [ output.append(model.predict(np.reshape(np.ndarray.flatten(image[y:y+wSize,x:x+wSize]),(1,wSize**2)))[0])  for y in range(0,ydim) for x in range(0,xdim)]
    return np.array(output)
    
def loadThatModel(folder):
    with open(folder+".json",'rb') as f:
        #json_string     = json.load(f)
        json_string     = f.read()
    model = model_from_json(json_string)
    model.load_weights(folder+".h5")
    for i in range(0,len(model.layers)):
        print(model.get_weights()[i].shape,end="")
        print(" "+str(i))
    return model

batch_size      = 32
nb_classes      = 10
nb_epochs       = 200
hidden_units    = 100
wSize           = 10

learning_rate   = 1e-6
clip_norm       = 1.0

# the data, shuffled and split between train and test sets
(X_train_raw, y_train), (X_test_raw, y_test) = mnist.load_data()

cutoff          = 10
X_train_raw     = X_train_raw[:cutoff]
X_test_raw      = X_test_raw[:cutoff]
X_train_raw     = X_train_raw.astype('float32')
X_test_raw      = X_test_raw.astype('float32')
X_train_raw     /= 255
X_test_raw      /= 255

y_train         = y_train[:cutoff]
y_test          = y_test[:cutoff]

autoencoder     = loadThatModel("../models/autoEncoder")


X_train  = []
X_test   = []
[X_train.append(autoEncode(image,wSize,autoencoder)) for image in X_train_raw]
[X_test.append(autoEncode(image,wSize,autoencoder)) for image in X_test_raw]
X_train     = np.array(X_train)
X_test      = np.array(X_test)

#X_train = X_train.reshape(X_train.shape[0], -1, 1)
#X_test = X_test.reshape(X_test.shape[0], -1, 1)
#X_train = X_train.astype('float32')
#X_test = X_test.astype('float32')
#X_train /= 255
#X_test /= 255
print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
Y_train = np_utils.to_categorical(y_train, nb_classes)
Y_test = np_utils.to_categorical(y_test, nb_classes)


del autoencoder




print('Evaluate IRNN...')
model = Sequential()
model.add(SimpleRNN(output_dim=hidden_units,
                    init=lambda shape: normal(shape, scale=0.001),
                    inner_init=lambda shape: identity(shape, scale=1.0),
                    activation='relu', input_shape=X_train.shape[1:]))
model.add(Dense(nb_classes))
model.add(Activation('softmax'))
rmsprop = RMSprop(lr=learning_rate)
model.compile(loss='categorical_crossentropy', optimizer=rmsprop)

model.fit(X_train, Y_train, batch_size=batch_size, nb_epoch=nb_epochs,
          show_accuracy=True, verbose=1, validation_data=(X_test, Y_test))

scores = model.evaluate(X_test, Y_test, show_accuracy=True, verbose=0)
print('IRNN test score:', scores[0])
print('IRNN test accuracy:', scores[1])





#
#print('Compare to LSTM...')
#model = Sequential()
#model.add(LSTM(hidden_units, input_shape=X_train.shape[1:]))
#model.add(Dense(nb_classes))
#model.add(Activation('softmax'))
#rmsprop = RMSprop(lr=learning_rate)
#model.compile(loss='categorical_crossentropy', optimizer=rmsprop)
#
#model.fit(X_train, Y_train, batch_size=batch_size, nb_epoch=nb_epochs,
#          show_accuracy=True, verbose=1, validation_data=(X_test, Y_test))
#
#scores = model.evaluate(X_test, Y_test, show_accuracy=True, verbose=0)
#print('LSTM test score:', scores[0])
#print('LSTM test accuracy:', scores[1])
