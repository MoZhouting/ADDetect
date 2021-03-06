# coding = 'utf-8'


import tensorflow as tf
import numpy as np

from tensorpack.graph_builder.model_desc import ModelDesc, InputDesc
from tensorpack.models.conv2d import Conv2D
from tensorpack.models.batch_norm import BatchNorm
from tensorpack.models.pool import AvgPooling, GlobalAvgPooling
from tensorpack.models.fc import FullyConnected
from tensorpack.models.regularize import regularize_cost
from tensorpack.tfutils.summary import add_moving_summary, add_param_summary
from tensorpack.tfutils.symbolic_functions import prediction_incorrect

# 分类数量,训练时酌情修改
_SUBJECT_NUM = 1000

class Model(ModelDesc):
    def __init__(self, depth):
        super(Model, self).__init__()
        self.N = int((depth - 4)  / 3)
        self.growthRate =12

    def _get_inputs(self):
        return [InputDesc(tf.float32, (None, 64, 64, 3), 'input'), InputDesc(tf.int32, (None,), 'label')]

    def _build_graph(self, input_vars):
        image, label = input_vars
        image = image / 128.0 - 1

        def conv(name, l, channel, stride):
            return Conv2D(name, l, channel, 3, stride=stride,nl=tf.identity, use_bias=False,
                          W_init=tf.random_normal_initializer(stddev=np.sqrt(2.0/9/channel)))

        def add_layer(name, l):
            shape = l.get_shape().as_list()
            in_channel = shape[3]
            with tf.variable_scope(name) as scope:
                c = BatchNorm('bn1', l)
                c = tf.nn.relu(c)
                c = conv('conv1', c, self.growthRate, 1)
                l = tf.concat([c, l], 3)
            return l

        def add_transition(name, l):
            shape = l.get_shape().as_list()
            in_channel = shape[3]
            with tf.variable_scope(name) as scope:
                l = BatchNorm('bn1', l)
                l = tf.nn.relu(l)
                l = Conv2D('conv1', l, in_channel, 1, stride=1, use_bias=False, nl=tf.nn.relu)
                l = AvgPooling('pool', l, 2)
            return l


        def dense_net(name):

            l = conv('conv0', image, 16, 1)
            with tf.variable_scope('block1') as scope:
                for i in range(self.N):
                    l = add_layer('dense_layer.{}'.format(i), l)
                l = add_transition('transition1', l)

            with tf.variable_scope('block2') as scope:
                for i in range(self.N):
                    l = add_layer('dense_layer.{}'.format(i), l)
                l = add_transition('transition2', l)

            with tf.variable_scope('block3') as scope:
                for i in range(self.N):
                    l = add_layer('dense_layer.{}'.format(i), l)

            l = BatchNorm('bnlast', l)
            l = tf.nn.relu(l)
            l = GlobalAvgPooling('gap', l)
            l = FullyConnected('feature', l, out_dim=2048, nl=tf.identity)
            logits = FullyConnected('linear', l, out_dim=_SUBJECT_NUM, nl=tf.identity)

            return logits

        logits = dense_net("dense_net")

        prob = tf.nn.softmax(logits, name='output')

        cost = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=label)
        cost = tf.reduce_mean(cost, name='cross_entropy_loss')

        wrong = prediction_incorrect(logits, label)
        # monitor training error
        add_moving_summary(tf.reduce_mean(wrong, name='train_error'))

        # weight decay on all W
        wd_cost = tf.multiply(1e-4, regularize_cost('.*/W', tf.nn.l2_loss), name='wd_cost')
        add_moving_summary(cost, wd_cost)

        add_param_summary(('.*/W', ['histogram']))   # monitor W
        self.cost = tf.add_n([cost, wd_cost], name='cost')


    def _get_optimizer(self):
        lr = tf.get_variable('learning_rate', initializer=0.1, trainable=False)
        tf.summary.scalar('learning_rate', lr)
        return tf.train.MomentumOptimizer(lr, 0.9, use_nesterov=True)



if __name__ == '__main__':
    pass