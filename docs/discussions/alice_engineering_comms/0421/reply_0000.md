## 2023-10-15 @pdxjohnny Engineering Logs

- Prep for OpenVEX meeting tomorrow
  - Objective: Minimal SCITT payload of VEX broadcast over ActivityPub
- https://codeberg.org/bovine/bovine/src/branch/main/bovine_herd/FEDERATION.md
  - https://www.darkreading.com/cloud/-cattle-not-pets-the-rise-of-security-as-code
  - https://zitadel.com/docs/blog/treat-clusters-as-cattle
    - > ![clusters-are-cattle-not-pets](https://github.com/intel/dffml/assets/5950433/77d2673f-ed5f-4202-bb44-25f76060f45f)
- https://codeberg.org/bovine/bovine
  - Most of the tools need to be run from the directory with the SQLite database in them (`bovine.sqlite3`)
- https://bovine-herd.readthedocs.io/en/latest/deployment.html
  - Bovine and associated libraries **require Python 3.11 or greater!!!**

```console
$ python --version
Python 3.11.5
```

```console
python -m venv .venv && \
. .venv/bin/activate && \
pip install -U pip setuptools wheel && \
pip install \
  toml \
  bovine{-store,-process,-pubsub,-herd,-tool} \
  'https://codeberg.org/pdxjohnny/bovine/archive/activitystreams_collection_helper_enable_multiple_iterations.tar.gz#egg=bovine&subdirectory=bovine' \
  'https://codeberg.org/pdxjohnny/mechanical_bull/archive/event_loop_on_connect_call_handlers.tar.gz#egg=mechanical-bull'
```

```python
from quart import Quart

from bovine_herd import BovineHerd
from bovine_pubsub import BovinePubSub

app = Quart(__name__)
BovinePubSub(app)
BovineHerd(app)
```

```console
$ hypercorn app:app
```

- https://blog.mymath.rocks/2023-03-25/BIN2_Moo_Client_Registration_Flow
- https://codeberg.org/bovine/bovine/src/branch/main/bovine_store/bovine_store/actor/test_register.py
- We need to register a user first
- https://codeberg.org/bovine/bovine/src/branch/main/bovine_tool

```console
$ export HANDLE_NAME=alice
$ export BOVINE_NAME=$(python -m bovine_tool.register "${HANDLE_NAME}" --domain http://localhost:8000 | awk '{print $NF}')
$ echo $BOVINE_NAME
alice_80cde26c-e4a7-4941-95ed-77cf8af14810
$ sqlite3 bovine.sqlite3 "SELECT * FROM bovineactor;"
1|__bovine__application_actor__|bovine|{}|2023-10-15 18:37:25.678942+00:00|2023-10-15 18:37:25.678976+00:00
2|alice_b0412432-cdb6-44d5-8789-b9fcf0cd04bc|alice|{}|2023-10-15 19:12:17.408055+00:00|2023-10-15 19:12:17.408070+00:00
$ sqlite3 bovine.sqlite3 "SELECT * FROM sqlite_master WHERE type='table';"
$ curl -s "http://localhost:8000/.well-known/webfinger?resource=acct:${HANDLE_NAME}@localhost:8000" | jq
```

```json
{
  "links": [
    {
      "href": "http://localhost:8000/endpoints/IlCKASjVegMJEKtNg_JLmmMQjJksrjnTEJH_xvmrvjY",
      "rel": "self",
      "type": "application/activity+json"
    }
  ],
  "subject": "acct:alice@localhost:8000"
}
```

- https://bovine.readthedocs.io/en/latest/tutorial_client.html
  - https://codeberg.org/bovine/mechanical_bull
    - We can use the client APIs via the mechanical-bull library's abstraction.
      - https://codeberg.org/bovine/mechanical_bull/src/branch/main/examples/moocow_handler.py
    - We first generate a config file (`config.toml`) for the user we which to automate actions for.
    - Add user with `--accept` to automate the accepting of follow requests.

```console
$ python -m mechanical_bull.add_user --accept "${HANDLE_NAME}" http://localhost:8000
Adding new user to config.toml
Please add did:key:z6MkeygVtzoxnLjWBewVr1PspbqqfvzURsE5e4ipsjxFJ8px to the access list of your ActivityPub actor
```

```toml
[alice]
secret = "z3u2U84hz8wxvB29HKwDhadxAKLxfv65qSNfYTK6vedzH9fn"
host = "http://localhost:8000"

[alice.handlers]
"mechanical_bull.actions.accept_follow_request" = true
```

- https://bovine-store.readthedocs.io/en/latest/reference/bovine_store.html#bovine_store.BovineAdminStore.add_identity_string_to_actor
  - > This will create the account @moocow@cows.example which can be accessed through Moo-Auth-1 with the secret corresponding to the did.
  - > Modifies an Actor by adding a new identity to it. name is used to identity the identity and serves little functional purpose.
  - Future ref SCITT DID
- https://codeberg.org/bovine/bovine/src/branch/main/bovine_tool#managing-users
  - The `bovine_tool.manage` command which we use to add dids to a user takes the `bovine_name`, the unique name for a user within the DB, NOT the handle.
  - https://codeberg.org/bovine/bovine/src/commit/5967146abbdd0b1f7a11f56336f8fe8fcd2b87e8/bovine_store/bovine_store/models.py#L60

```console
$ sqlite3 -csv -header bovine.sqlite3 "SELECT * FROM sqlite_master WHERE type='table' AND name='bovineactor';"
```

```csv
type,name,tbl_name,rootpage,sql
table,bovineactor,bovineactor,2,"CREATE TABLE ""bovineactor"" (
    ""id"" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    ""bovine_name"" VARCHAR(255) NOT NULL UNIQUE,
    ""handle_name"" VARCHAR(255) NOT NULL,
    ""properties"" JSON NOT NULL,
    ""created"" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    ""last_sign_in"" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
)"
```

- If you are looking up the handle from a config you can run the following. Otherwise you will have gotten the `bovine_name` from `bovine_tool.register`.

```bash
export HANDLE_NAME=$(cat config.toml | python -c 'import sys, tomllib; print(list(tomllib.load(sys.stdin.buffer).keys())[0])')
export BOVINE_NAME=$(sqlite3 -csv bovine.sqlite3 "SELECT bovine_name FROM bovineactor WHERE handle_name='${HANDLE_NAME}';")
```

- Let's add that key so mechanical bull can start accepting follow requests
  - We need to add the public portion of the key, be sure to convert from the private form if you extract from the `toml` file.

```console
$ python -m bovine_tool.manage "${BOVINE_NAME}" --did_key key0 $(cat config.toml | python -c 'import sys, tomllib, bovine.crypto; print(bovine.crypto.private_key_to_did_key(tomllib.load(sys.stdin.buffer)[sys.argv[-1]]["secret"]))' "${HANDLE_NAME}")
$ sqlite3 -header -csv bovine.sqlite3 "SELECT * FROM bovineactorkeypair WHERE name='key0';" 
id,name,private_key,public_key,bovine_actor_id
4,key0,"",did:key:did:key:z6MkeyGwWnSn1DFxm48HJ6L7j9m1vxYniEseGRY46fKHu6v4,1
```

- Within the file `scitt_handler.py` we've defined our demo handler
  - We need to enable it within the mechanical bull config file (`config.toml`)
    before we run mechanical bull.

```console
$ python -c 'import sys, pathlib, toml; path = pathlib.Path(sys.argv[-3]); obj = toml.loads(path.read_text()); obj[sys.argv[-2]]["handlers"][sys.argv[-1]] = True; path.write_text(toml.dumps(obj))' config.toml "${HANDLE_NAME}" scitt_handler
```

- Now we run the automations for our client actor (Alice) via mechanical bull.

```console
$ PYTHONPATH=$PYTHONPATH:$PWD python -m mechanical_bull.run
INFO:mechanical_bull.event_loop:Connected
INFO:root:/home/pdxjohnny/Documents/fediverse/bovine/hacking/scitt_handler.py:handle(handler_event=HandlerEvent.OPENED)
client: BovineClient(actor_id='http://localhost:8000/endpoints/KUMjPaGP8Ei1eXoy3udib5uLirzABP8YqAdD8yysrDI', public_key_url=None, access_token=None, secret='z3u2aZCG3JJQrsn7fcH9ZeRrod6NGUBdbWnptgYFsQtXWVXy', domain='http://localhost:8000', client=<bovine.clients.moo_auth.MooAuthClient object at 0x7f3f59907350>, session=<aiohttp.client.ClientSession object at 0x7f3f5b0a0f90>)
outbox: <bovine.activitystreams.collection_helper.CollectionHelper object at 0x7f3f5a5065d0>
Begin iteration 0 over outbox
End iteration 0 over outbox
No messages in outbox, creating activity
creating activity: {'@context': 'https://www.w3.org/ns/activitystreams', 'type': 'Announce', 'actor': 'http://localhost:8000/endpoints/KUMjPaGP8Ei1eXoy3udib5uLirzABP8YqAdD8yysrDI', 'to': ['https://www.w3.org/ns/activitystreams#Public'], 'cc': ['http://localhost:8000/endpoints/aT4gehUFZzgc1sf_UNosuO-Fyle1eN2D6NBLviXMtzs']}
created activity: {'@context': 'https://www.w3.org/ns/activitystreams', 'type': 'Announce', 'actor': 'http://localhost:8000/endpoints/KUMjPaGP8Ei1eXoy3udib5uLirzABP8YqAdD8yysrDI', 'to': ['https://www.w3.org/ns/activitystreams#Public'], 'cc': ['http://localhost:8000/endpoints/aT4gehUFZzgc1sf_UNosuO-Fyle1eN2D6NBLviXMtzs']}
Begin iteration 1 over outbox
Iteration 1 Message 1 in outbox: {'@context': 'about:bovine', 'actor': {'id': 'http://localhost:8000/endpoints/KUMjPaGP8Ei1eXoy3udib5uLirzABP8YqAdD8yysrDI', 'inbox': 'http://localhost:8000/endpoints/qGqejyzZnUBXL5vpPh5MKlXW2SktpkERFBqfHnp70MQ', 'name': 'alice', 'outbox': 'http://localhost:8000/endpoints/g5PJ-7QJ58p0aMHn3h1m0SnokPPtO6myZ1otwwV0no4', 'preferredUsername': 'alice', 'publicKey': 'http://localhost:8000/endpoints/KUMjPaGP8Ei1eXoy3udib5uLirzABP8YqAdD8yysrDI#serverKey', 'type': 'Person'}, 'cc': ['http://localhost:8000/endpoints/aT4gehUFZzgc1sf_UNosuO-Fyle1eN2D6NBLviXMtzs'], 'id': 'http://localhost:8000/objects/0a8fa278-c079-421e-87f8-76bd2dfb8cf8', 'to': ['as:Public'], 'type': 'Announce'}
End iteration 1 over outbox
```

[![asciicast](https://asciinema.org/a/614553.svg)](https://asciinema.org/a/614553)

- https://bovine.readthedocs.io/en/latest/message.html
  - We'll try creating two users and sending a message. Is that the same as a post? How can we make a regular post?
  - This also uses Moo auth, ideally we use something more standard like OIDC to not rock the boat too much.
- https://codeberg.org/bovine/mechanical_bull/src/commit/a13fc7d3d04629eeb72f3b2f0fa976e52860de68/mechanical_bull/run.py#L18
  - https://docs.python.org/3/library/asyncio-task.html?highlight=taskgroup#asyncio.TaskGroup
    - New in Python 3.11
- Okay we can now start and ActivityPub server, create an actor, create posts, and accept follows.

```bash
#!/usr/bin/env bash
set -xeuo pipefail

rm -rf .venv && \
python -m venv .venv && \
. .venv/bin/activate && \
pip install -U pip setuptools wheel && \
pip install \
  toml \
  bovine{-store,-process,-pubsub,-herd,-tool} \
  'https://codeberg.org/pdxjohnny/bovine/archive/activitystreams_collection_helper_enable_multiple_iterations.tar.gz#egg=bovine&subdirectory=bovine' \
  'https://codeberg.org/pdxjohnny/mechanical_bull/archive/event_loop_on_connect_call_handlers.tar.gz#egg=mechanical-bull'

export HYPERCORN_PID=0
function kill_hypercorn() {
  kill "${HYPERCORN_PID}"
}
hypercorn app:app &
export HYPERCORN_PID=$!
trap kill_hypercorn EXIT
sleep 1

export HANDLE_NAME=alice
export BOVINE_NAME=$(python -m bovine_tool.register "${HANDLE_NAME}" --domain http://localhost:8000 | awk '{print $NF}')
python -m mechanical_bull.add_user --accept "${HANDLE_NAME}" http://localhost:8000
python -m bovine_tool.manage "${BOVINE_NAME}" --did_key key0 $(cat config.toml | python -c 'import sys, tomllib, bovine.crypto; print(bovine.crypto.private_key_to_did_key(tomllib.load(sys.stdin.buffer)[sys.argv[-1]]["secret"]))' "${HANDLE_NAME}")

python -c 'import sys, pathlib, toml; path = pathlib.Path(sys.argv[-3]); obj = toml.loads(path.read_text()); obj[sys.argv[-2]]["handlers"][sys.argv[-1]] = True; path.write_text(toml.dumps(obj))' config.toml "${HANDLE_NAME}" scitt_handler

PYTHONPATH=${PYTHONPATH:-''}:$PWD timeout 5s python -m mechanical_bull.run
```

- Time to integrate into SCITT
  - We'll leverage the work we did on OIDC for plugin helper infra and instantiation of the federation class.
- The only event that seems relevant at the moment is the creation of a receipt and it's registration at a given entry ID.

[![asciicast](https://asciinema.org/a/614595.svg)](https://asciinema.org/a/614595)

```

^C(.venv) $ rm -f ~/Documents/fediverse/scitt_federation_bob/config.toml && BOVINE_DB_URL="sqlite://${HOME}/Documents/fediverse/bovine/hacking/bovine.sqlite3" scitt-emulator server --workspace workspace_bob/ --tree-alg CCF --port 6000     --federation scitt_emulator.federation_activitypub_bovine:SCITTFederationActivityPubBovine     --federation-config-path ~/Documents/fediverse/scitt_federation_bob/config.json
Adding new user to config.toml
Please add did:key:z6MkjdrmchDwER5aZfveSE9sF3rvjgwtV2mmJkxo8LGNSrfS to the access list of your ActivityPub actor
Service parameters: workspace_bob/service_parameters.json
 * Serving Flask app 'scitt_emulator.server'
 * Debug mode: off
INFO:mechanical_bull.event_loop:Connected
INFO:root:/home/pdxjohnny/Documents/python/scitt-api-emulator/scitt_emulator/federation_activitypub_bovine.py:handle(handler_event=HandlerEvent.OPENED)
INFO:scitt_emulator.federation_activitypub_bovine:Attempting UNIX bind at '/home/pdxjohnny/Documents/fediverse/scitt_federation_bob/federate_created_entries_socket'
INFO:scitt_emulator.federation_activitypub_bovine:Awaiting receipts to federate at '/home/pdxjohnny/Documents/fediverse/scitt_federation_bob/federate_created_entries_socket'
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:6000
 * Running on http://192.168.1.122:6000
Press CTRL+C to quit
Leaf hash: e3e0fd1c01f0caa89f39301056d57f9b5a4cb1c2d0467e36c10ec6f8838a045a
Root: 44bb75e0a070ac888f5c0f94a7c1c3b95df82305522e523e66295675dc76e092
Receipt written to workspace_bob/storage/10.receipt.cbor
Claim written to workspace_bob/storage/10.cose
127.0.0.1 - - [16/Oct/2023 04:36:13] "POST /entries HTTP/1.1" 201 -
INFO:scitt_emulator.federation_activitypub_bovine:federate_created_entry() Reading... <StreamReader transport=<_SelectorSocketTransport fd=8 read=polling write=<idle, bufsize=0>>>
INFO:scitt_emulator.federation_activitypub_bovine:federate_created_entry() Read: b"\x82X1\xa3jservice_idhemulatorhtree_algcCCFiissued_at\x1ae- -\x84X@\x8d\xf4@\x9d>\x0b\xb8\x80%\xdb\xbe\xab~\x92\xc3IM-\x8c\xc5u\x8a\xb1\xf7t\xbe\x0bplr\xed\xf0\x9f\xb2\x15*(\xb8M\xe6\x04\x9e\x805\xa9\x1e\x02\xe9\x8eK\xb9\xa9\x9b!\xba\xff\x89\xe4\x10\xb1\xcf\xbd\x03~Y\x01$0\x82\x01 0\x81\xc7\xa0\x03\x02\x01\x02\x02\x14+\xbbG>\n\nd@\xdbo\t\xde\x00\x89\xa0\xfc\xcf\xd7C\x8c0\n\x06\x08*\x86H\xce=\x04\x03\x020\x121\x100\x0e\x06\x03U\x04\x03\x0c\x07service0\x1e\x17\r231016101902Z\x17\r241015101902Z0\x0f1\r0\x0b\x06\x03U\x04\x03\x0c\x04node0Y0\x13\x06\x07*\x86H\xce=\x02\x01\x06\x08*\x86H\xce=\x03\x01\x07\x03B\x00\x04x(\x193\x9aD\xad\x86\x1e\xde\x83}9-\x84\xcdY\x86W\xef\xbc\xed<\xefg\xfd\x1e\x19~*\xb3\x97[\x8f\xe9(,\xf28\x9c\\\xae*b\x12\x1f\xa0U\xa5\xf1I\xcb-\xfc\xfc\x0c\xf1\xad&\x1f\x97[\x1c\xc30\n\x06\x08*\x86H\xce=\x04\x03\x02\x03H\x000E\x02!\x00\x82\xd4\xc4\x8ax\xc4\xa2\xec\xb4\xc3\xac[\xe2\xf2\x11\xfb'\x8d\xdcF\xda\x0e\xae`I5u\xad%QZ\xdc\x02 a\xea\xe6Ti\x9b\x8c+\xde\x7f{i'\xfc\xc0\x1e\xc7\xaf\xe4\xf0\xa1\x9e\xa0A\xd7\xc6\x8fw\xb7g\xf7\xd7\x86\x82\xf5X \xd3F\xc1/n\x08f!n\x87\xa3\xf8D\x84\xebs\xd5\xb4\t\x0f\xccD\xf7O\x00b\xa1\xe2\x15Rp\xe4\x82\xf5X (|\x90\xae\xab\xcf\x98\x04\x1c\x8c\x15\r\xa4d\x81\x02\xa8\x00\x80W\x10b\x9cW:D\x04S\xe2K\xf6\x86\x82\xf5X \xda\x94\xde\x8f\xc1\xa6i\x13x\xc9d\x06\x91\xef\xfbw\x92\x8e\x16t\xd1\n\xc37cQ\x16\xd7jS\x1af\x82\xf5X p\xa2\xd6\x13\xa4\x9b\xb4\xed2\xc9\x94\x9e\xa36`\x0b7\x1b=\r\xea\xc9g\xa7\x1e\xb1\xa6-\xe8\x7f.\xb0\x82\xf5X \xb4\x11\xde\xd0\x12\xae\xb3\x1d\xbf\x00\xf8'\xc6\x11\xe1\xb4\xbe\x198X\xa4\x12\x8c,\xc2\x9aL>\x99\xad\xc4\x8c\x82\xf5X 9\xdc\x96\x86\x1dV\xb3\xd1\\\x0f\x17u\x01_8\xec%\xd5\x96\xff?\x11\xc4\x8e\xd5y\x13\x01#\xef\xa6\xc2\x82X \xb5\xa2\xc9bPa#f\xea'/\xfa\xc6\xd9tJ\xafKE\xaa\xcd\x96\xaa|\xfc\xb91\xee;U\x82YB10"
INFO:scitt_emulator.federation_activitypub_bovine:Sending... {'@context': 'https://www.w3.org/ns/activitystreams', 'type': 'Create', 'actor': 'http://localhost:5000/endpoints/HFtWA19wdwkSXBwKCoQ_qHVujRYHDvkukUZ_FGhfzoM', 'to': ['https://www.w3.org/ns/activitystreams#Public'], 'cc': ['http://localhost:5000/endpoints/YjT5WQV9x5Fe-p8SopWEgYXGt-gI_gb6b_HOCN7Wp_c'], 'object': {'@context': 'https://www.w3.org/ns/activitystreams', 'type': 'Note', 'attributedTo': 'http://localhost:5000/endpoints/HFtWA19wdwkSXBwKCoQ_qHVujRYHDvkukUZ_FGhfzoM', 'to': ['https://www.w3.org/ns/activitystreams#Public'], 'cc': ['http://localhost:5000/endpoints/YjT5WQV9x5Fe-p8SopWEgYXGt-gI_gb6b_HOCN7Wp_c'], 'content': 'glgxo2pzZXJ2aWNlX2lkaGVtdWxhdG9yaHRyZWVfYWxnY0NDRmlpc3N1ZWRfYXQaZS0gLYRYQI30QJ0+C7iAJdu+q36Sw0lNLYzFdYqx93S+C3Bscu3wn7IVKii4TeYEnoA1qR4C6Y5LuambIbr/ieQQsc+9A35ZASQwggEgMIHHoAMCAQICFCu7Rz4KCmRA228J3gCJoPzP10OMMAoGCCqGSM49BAMCMBIxEDAOBgNVBAMMB3NlcnZpY2UwHhcNMjMxMDE2MTAxOTAyWhcNMjQxMDE1MTAxOTAyWjAPMQ0wCwYDVQQDDARub2RlMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEeCgZM5pErYYe3oN9OS2EzVmGV++87TzvZ/0eGX4qs5dbj+koLPI4nFyuKmISH6BVpfFJyy38/AzxrSYfl1scwzAKBggqhkjOPQQDAgNIADBFAiEAgtTEinjEouy0w6xb4vIR+yeN3EbaDq5gSTV1rSVRWtwCIGHq5lRpm4wr3n97aSf8wB7Hr+TwoZ6gQdfGj3e3Z/fXhoL1WCDTRsEvbghmIW6Ho/hEhOtz1bQJD8xE908AYqHiFVJw5IL1WCAofJCuq8+YBByMFQ2kZIECqACAVxBinFc6RART4kv2hoL1WCDalN6PwaZpE3jJZAaR7/t3ko4WdNEKwzdjURbXalMaZoL1WCBwotYTpJu07TLJlJ6jNmALNxs9DerJZ6cesaYt6H8usIL1WCC0Ed7QEq6zHb8A+CfGEeG0vhk4WKQSjCzCmkw+ma3EjIL1WCA53JaGHVaz0VwPF3UBXzjsJdWW/z8RxI7VeRMBI++mwoJYILWiyWJQYSNm6icv+sbZdEqvS0WqzZaqfPy5Me47VYJZQjEw'}}
127.0.0.1 - - [16/Oct/2023 04:36:13] "GET /entries/10/receipt HTTP/1.1" 200 -
client: BovineClient(actor_id='http://localhost:5000/endpoints/HFtWA19wdwkSXBwKCoQ_qHVujRYHDvkukUZ_FGhfzoM', public_key_url=None, access_token=None, secret='z3u2bd6bF1dtGRagzZGK3g1JM7FAnXs6VeYpxGHBorYtAZ6Y', domain='http://localhost:5000', client=<bovine.clients.moo_auth.MooAuthClient object at 0x7f0e5a3493d0>, session=<aiohttp.client.ClientSession object at 0x7f0e594f2250>)
outbox: <bovine.activitystreams.collection_helper.CollectionHelper object at 0x7f0e5945f510>
Message 1 in outbox: {'@context': 'about:bovine', 'actor': {'id': 'http://localhost:5000/endpoints/HFtWA19wdwkSXBwKCoQ_qHVujRYHDvkukUZ_FGhfzoM', 'inbox': 'http://localhost:5000/endpoints/KBP5AmUfUS-c6ef71KRk_WB4-_WfYOYFPppAGsDJ92w', 'name': 'bob', 'outbox': 'http://localhost:5000/endpoints/1s6fHKVfhI6pmpDBz3DFuWG-JTao6ftpVX6215zAxJY', 'preferredUsername': 'bob', 'publicKey': 'http://localhost:5000/endpoints/HFtWA19wdwkSXBwKCoQ_qHVujRYHDvkukUZ_FGhfzoM#serverKey', 'type': 'Person'}, 'cc': ['http://localhost:5000/endpoints/YjT5WQV9x5Fe-p8SopWEgYXGt-gI_gb6b_HOCN7Wp_c'], 'id': 'http://localhost:5000/objects/658e3bfe-6565-41d4-aa4a-848fe76e64ec', 'object': {'attributedTo': 'http://localhost:5000/endpoints/HFtWA19wdwkSXBwKCoQ_qHVujRYHDvkukUZ_FGhfzoM', 'cc': ['http://localhost:5000/endpoints/YjT5WQV9x5Fe-p8SopWEgYXGt-gI_gb6b_HOCN7Wp_c'], 'content': 'glgxo2pzZXJ2aWNlX2lkaGVtdWxhdG9yaHRyZWVfYWxnY0NDRmlpc3N1ZWRfYXQaZS0gLYRYQI30QJ0+C7iAJdu+q36Sw0lNLYzFdYqx93S+C3Bscu3wn7IVKii4TeYEnoA1qR4C6Y5LuambIbr/ieQQsc+9A35ZASQwggEgMIHHoAMCAQICFCu7Rz4KCmRA228J3gCJoPzP10OMMAoGCCqGSM49BAMCMBIxEDAOBgNVBAMMB3NlcnZpY2UwHhcNMjMxMDE2MTAxOTAyWhcNMjQxMDE1MTAxOTAyWjAPMQ0wCwYDVQQDDARub2RlMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEeCgZM5pErYYe3oN9OS2EzVmGV++87TzvZ/0eGX4qs5dbj+koLPI4nFyuKmISH6BVpfFJyy38/AzxrSYfl1scwzAKBggqhkjOPQQDAgNIADBFAiEAgtTEinjEouy0w6xb4vIR+yeN3EbaDq5gSTV1rSVRWtwCIGHq5lRpm4wr3n97aSf8wB7Hr+TwoZ6gQdfGj3e3Z/fXhoL1WCDTRsEvbghmIW6Ho/hEhOtz1bQJD8xE908AYqHiFVJw5IL1WCAofJCuq8+YBByMFQ2kZIECqACAVxBinFc6RART4kv2hoL1WCDalN6PwaZpE3jJZAaR7/t3ko4WdNEKwzdjURbXalMaZoL1WCBwotYTpJu07TLJlJ6jNmALNxs9DerJZ6cesaYt6H8usIL1WCC0Ed7QEq6zHb8A+CfGEeG0vhk4WKQSjCzCmkw+ma3EjIL1WCA53JaGHVaz0VwPF3UBXzjsJdWW/z8RxI7VeRMBI++mwoJYILWiyWJQYSNm6icv+sbZdEqvS0WqzZaqfPy5Me47VYJZQjEw', 'id': 'http://localhost:5000/objects/4a7ca61d-2d7c-4b0d-8c93-e4278e158c03', 'likes': 'http://localhost:5000/objects/4a7ca61d-2d7c-4b0d-8c93-e4278e158c03/likes', 'replies': 'http://localhost:5000/objects/4a7ca61d-2d7c-4b0d-8c93-e4278e158c03/replies', 'shares': 'http://localhost:5000/objects/4a7ca61d-2d7c-4b0d-8c93-e4278e158c03/shares', 'to': ['as:Public'], 'type': 'Note'}, 'to': ['as:Public'], 'type': 'Create'}
End of messages in outbox, total: 1
```

[![asciicast](https://asciinema.org/a/614633.svg)](https://asciinema.org/a/614633)

- TODO
  - [ ] Could we issue OIDC tokens off the mechanical bull manged keys?
    - It looks like `bovine.clients.bearer` is used to talk to Mastodon's API. If we wanted to make Bovine accept token auth from a client signed OIDC token we could add routes to the Herd server for the jwks
  - [ ] KCP based config for accounts
    - https://cloud.redhat.com/blog/an-introduction-to-kcp
  - [ ] https://codeberg.org/bovine/mechanical_bull/issues/13
  - [ ] https://github.com/scitt-community/scitt-api-emulator/pull/37
    - https://github.com/pdxjohnny/scitt-api-emulator/tree/bovine_activitypub_federation
    - [federation-asciinema.txt](https://github.com/intel/dffml/files/12915715/federation-asciinema.txt)