Gitter ML Inference Chatbot
===========================

This tutorial shows how to use configs in DFFML operations. We'll be implementing
a Gitter chatbot. Let's take a look at the final result before moving forward.

.. image:: ./data/gitter.gif

Okay, Let's start!!
We'll be using the Gitter's Streamping API to collect chats, for this we need an
authorization token from Gitter. Go to https://developer.gitter.im/apps
and get the personal access token for your chatbot (If you are redirected to the Gitter docs
from this URL, sign in and try again).

Our dataflow will take a Gitter room URI as input (For https://gitter.im/dffml/community
``dffml/community`` is the URI), listens to chats in the room and replies to
messages which are directed to our bot.

.. note::

    All the code for this example is located under the
    `examples/dataflow/chatbot <https://github.com/intel/dffml/blob/master/examples/dataflow/chatbot>`_
    directory of the DFFML source code.

You'll need to install `aiohttp <https://github.com/aio-libs/aiohttp>`_
and ``dffml-model-scikit`` (The model used for prediction).

.. code-block:: console

    $ pip install aiohttp dffml-model-scikit

We'll write the operations for this dataflow in **operations.py**

Adding necessary imports and defining ``Definitions`` for operation
inputs.

**operations.py**

.. literalinclude:: /../examples/dataflow/chatbot/operations.py
    :lines: 1-15

Defining config for our operations

**operations.py**

.. literalinclude:: /../examples/dataflow/chatbot/operations.py
    :lines: 18-20

All requests to Gitter's API requires the room id of our room.
``get_room_id`` gets the ``room id`` from room name (The input to
our dataflow).

**operations.py**

.. literalinclude:: /../examples/dataflow/chatbot/operations.py
    :lines: 23-48

We listen to new messages directed to our bot.

**operations.py**

.. literalinclude:: /../examples/dataflow/chatbot/operations.py
    :lines: 51-85

We'll use this op to send replies back to the chatroom

**operations.py**

.. literalinclude:: /../examples/dataflow/chatbot/operations.py
    :lines: 88-120

This is the operation where all the logic for interpreting the messages
go. If you have a Natural Language Understanding module It'd go here, so
that you can parse unstructered data.

**operations.py**

.. literalinclude:: /../examples/dataflow/chatbot/operations.py
    :lines: 123-247

Our operations are ``get_room_id, stream_chat, send_message and interpret_message``.
All of them use at least one config. The common config being INISecretConfig which
loads secret token and bot name from the ini config file.

**configs.ini**

.. literalinclude:: /../examples/dataflow/chatbot/configs.ini

Detour: What are imp_enter and ctx_enter?
-----------------------------------------

.. code-block:: python

    config_cls=GitterChannelConfig,
    imp_enter={"secret": lambda self: self.config.secret},
    ctx_enter={"sctx": lambda self: self.parent.secret()},

This piece of code in the op decorator tells that the operation will be using
``GitterChannelConfig``. ``imp_enter`` and ``ctx_enter`` are basically shortcuts for
the double context entry followed in dffml.

``"secret": lambda self: self.config.secret``: sets the ``secret`` attribute of parent
to what is returned by the function; in this case it returns BaseSecret.

``"sctx": lambda self: self.parent.secret()``: calls the function and assigns the
return value to ``sctx`` attribute.

So in the operation instead of

.. code-block:: python

    with self.config.secret() as secret:
        with sctx as secret():
            sctx.call_a_method()

we can do

.. code-block:: python

    self.sctx.call_a_method()

Running the dataflow
--------------------

**run.py**

.. literalinclude:: /../examples/dataflow/chatbot/run.py

set the room name, config file name and run the dataflow

.. code-block:: console

    $ python run.py

Or using the command line to, create the dataflow

.. code-block:: console

    $ dffml dataflow create \
        operations:get_room_id \
        operations:stream_chat \
        operations:send_message \
        operations:interpret_message \
        -config \
            ini=operations:get_room_id.secret.plugin \
            configs.ini=operations:get_room_id.secret.config.filename \
            ini=operations:stream_chat.secret.plugin \
            configs.ini=operations:stream_chat.secret.config.filename \
            ini=operations:send_message.secret.plugin \
            configs.ini=operations:send_message.secret.config.filename \
            ini=operations:interpret_message.secret.plugin \
            configs.ini=operations:interpret_message.secret.config.filename \
        > chatbot_df.json

And run it by providing the ``room_name`` as the input

.. code-block:: console

    $ dffml dataflow run single \
        -dataflow ./chatbot_df.json \
        -inputs test_community1/community=room_name
