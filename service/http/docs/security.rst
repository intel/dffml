Security
========

Vulnerabilities should be reported via https://intel.com/security

CORS
----

You'll want to configure the domains that should be able to request the API via
the CORS flag, if you are putting this on a different domain.

For example if you are hosting the API service on
``https://dffml.example-api.com`` and you're web UI on
``https://dffml.example.com``, you'll need to add the URL of the web UI to the
CORS list.

.. code-block:: console

    $ dffml service http server -cors 'https://dffml.example-api.com'

You may just want to throw all of this CORS business out the window when
developing (we don't blame you). In which case you could enable connections from
all origins via ``*``.

.. code-block:: console

    $ dffml service http server -cors '*'

Atomic Mode
-----------

The ``-mc-atomic`` flag will disable all routes other than those registered via
``-mc-config``. If you want the server to only respond using the specified
dataflows, and provide no other functionality, use this option.

Multitenancy
------------

The HTTP API service is **not** intended for multi-tenant use, and most likely
never will be.

This means that its currently assumed that anyone allowed to connect to the
server (TLS client authentication protects anyone you haven't given a ``.key``
and ``.pem`` file to from connecting. So two people could access it at the same
time, but they won't be stopped from clobbering each other's work.

File, Network, Etc. Access
--------------------------

Since this just exposes existing DFFML APIs, its damn near impossible for use to
lock everything down within all the plugins of DFFML you might choose to expose
via this HTTP API. So we're not going to try. What this means is that if you're
running this you should sandbox it appropriately.

For example, if you expose the DFFML CSV source using this API, it takes a
filename parameter, which is the file containing the CSV data. Now if you say
that filename is at ``/root/some/file.csv`` and you're running this as root
then it's going to have access to that file therefore, **DO NOT RUN THIS AS
ROOT**, as anyone who is able to connect will have read write access to all
files on your system, you do not want to take this chance!

Similarly, if you expose the DFFML MySQL source, when you initialize new
MySQL protocol connections they will be originating from whatever machine is
running the HTTP API. So that means it might have access to internal databases
or something listing only on ``127.0.0.1``.

Authentication
--------------

TLS client authentication is currently used. There are scripts to generate basic
functioning certs. These certs should **not** be used in a production capacity.

In the future, we'll probably support JSON Web Tokens (JWT) signed with a public
key. And then you'll be able to provision your certs in a more reasonable way
(cert-manager if Kubernetes or something else). But for now this is what we've
got.

First, generate the server key and cert. The cert generated is only valid for
``127.0.0.1``. This will produce the server's private key file, ``server.key``,
and the server's certificate, ``server.pem``.

.. code-block:: console

    $ dffml service http createtls server
    Generating a RSA private key
    ......................................++++
    .................................++++
    writing new private key to 'server.key'
    -----

Then, generate the client key and cert. It will be signed by the server cert to
make it acceptable to the server. This will produce the client's private key
file, ``client.key``, the client's certificate, ``client.pem``, and the client's
certificate signing request ``client.csr`` (which is unnecessary after the
command is run because it's already been used to create ``client.pem``).

.. code-block:: console

    $ dffml service http createtls client
    Generating a RSA private key
    .................................................++++
    ........++++
    writing new private key to 'client.key'
    -----
    Signature ok
    subject=CN = RealUser
    Getting CA Private Key

Now you can run the server without the ``-insecure`` flag.

.. code-block:: console

    $ dffml service http server -port 5000
    $ curl -w '\n' \
        --cacert server.pem \
        --cert client.pem \
        --key client.key \
        https://127.0.0.1:5000/list/sources
    ... JSON output ...
