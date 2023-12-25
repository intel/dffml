import pathlib
import shutil
import statistics
from typing import AsyncIterator, Type
import numpy
import tensorflow as tf

from dffml import (
    config,
    field,
    entrypoint,
    SimpleModel,
    ModelNotTrained,
    Feature,
    Features,
    SourcesContext,
    Record,
)


tf.compat.v1.disable_eager_execution()

@config
class MyTFSLRModelConfig:
    features: Features = field(
        "Features to train on (mytfslr only supports one)"
    )
    predict: Feature = field("Label or the value to be predicted")
    location: pathlib.Path = field("Location where state should be saved")


@entrypoint("mytflr")
class MyTFSLRModel(SimpleModel):
    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type = MyTFSLRModelConfig

    def __init__(self, config):
        super().__init__(config)
        # Simple linear regression only supports a single input feature
        if len(self.config.features) != 1:
            raise ValueError("Model only support a single feature")

    async def train(self, sources: SourcesContext) -> None:
        # X and Y data
        train_X=[]
        train_Y=[]
        # Go through all records that have the feature we're training on and the
        # feature we want to predict.
        async for record in sources.with_features(
            [self.config.features[0].name, self.config.predict.name]
        ):
            train_X.append(record.feature(self.config.features[0].name))
            train_Y.append(record.feature(self.config.predict.name))
        # Use self.logger to report how many records are being used for training
        self.logger.debug("Number of training records: %d", len(train_X))
        # Save m, b, and accuracy
        train_X=numpy.array(train_X)
        train_Y=numpy.array(train_Y)
        n_samples = train_X.shape[0]   


        learning_rate = 0.01     
        training_epochs = 1000   
        display_step = 50       


        X = tf.compat.v1.placeholder(tf.float32,name="Input")
        Y = tf.compat.v1.placeholder(tf.float32)


        # set bias to 0, set random weights
        W = tf.Variable(tf.compat.v1.random_uniform([1]))
        b = tf.Variable(tf.zeros([1]))


        #  y = x*w + b
        pred = tf.add(tf.multiply(X, W), b)

        y=tf.identity(pred, name="Output") 
        # MSE
        cost = tf.reduce_sum(tf.pow(pred-Y, 2))/(2*n_samples)
        #  Gradient descent
        #  Note, minimize() knows to modify W and b because Variable objects are trainable=True by default
        optimizer = tf.compat.v1.train.GradientDescentOptimizer(learning_rate).minimize(cost)

       
        init = tf.compat.v1.global_variables_initializer()



        # Start training
        sess=tf.compat.v1.Session()
            # Run the initializer
        sess.run(init)
        # Fit all training data
        for epoch in range(training_epochs):
            sess.run(optimizer, feed_dict={X:train_X, Y: train_Y})
            # Display logs per epoch step
            if (epoch+1) % display_step == 0:
                c = sess.run(cost, feed_dict={X: train_X, Y:train_Y})
                print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(c), \
                    "W=", sess.run(W), "b=", sess.run(b))

        print("Optimization Finished!")
        training_cost = sess.run(cost, feed_dict={X: train_X, Y: train_Y})
        print("Training cost=", training_cost, "W=", sess.run(W), "b=", sess.run(b), '\n')

        ######self.storage["regression_line"] = best_fit_line(x, y)

        
        shutil.rmtree(r"./my_tf_model_simple_dffml")
        tf.compat.v1.saved_model.simple_save(sess,
                        r"./my_tf_model_simple_dffml",
                        inputs={X.name: X},
                        outputs={y.name: y}) 
