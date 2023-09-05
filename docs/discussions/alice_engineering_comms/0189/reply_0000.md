## 2023-02-25 @pdxjohnny Engineering Logs

- https://github.com/WebOfTrustInfo/rwot11-the-hague/compare/master...Klingefjord:rwot11-the-hague:master
  - https://github.com/WebOfTrustInfo/rwot11-the-hague/blob/master/advance-readings/Multi-dimensional%20reputation%20systems%20using%20webs-of-trust.md
- https://github.com/cli/cli/blob/trunk/docs/install_linux.md#fedora-centos-red-hat-enterprise-linux-dnf

```console
$ sudo dnf install 'dnf-command(config-manager)'
$ sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
$ sudo dnf install gh
```

- https://developer.hashicorp.com/packer/downloads

```console
$ wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
$ echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
$ sudo apt update && sudo apt install packer
```

```console
$ sudo dnf install -y dnf-plugins-core
$ sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/fedora/hashicorp.repo
$ sudo dnf -y install packer
```

- kcp -> k8s -> cf push -> webhook service -> dataflow to create activitypub event -> dwn-cli send -> webrtc -> dwn-cli recv -> alice threats listen activitypub -stdin -> alice shouldi contribute -> alice please contribute -> soft-serve/github repo pull request -> webhook service
- https://docs.docker.com/engine/install/fedora/

```console
$ sudo dnf -y install dnf-plugins-core
$ sudo dnf config-manager \
    --add-repo \
    https://download.docker.com/linux/fedora/docker-ce.repo
$ sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
$ sudo systemctl enable --now docker
```

- https://kind.sigs.k8s.io/docs/user/quick-start/

```console
$ curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.17.0/kind-linux-amd64
$ chmod +x ./kind
$ sudo mv ./kind /usr/local/bin/kind
```

- https://github.com/cloudfoundry/korifi/blob/main/INSTALL.kind.md

```console
$ ROOT_NAMESPACE="cf"
$ KORIFI_NAMESPACE="korifi-system"
$ ADMIN_USERNAME="kubernetes-admin"
$ BASE_DOMAIN="apps-127-0-0-1.nip.io"
$ cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF
```

- Restart loop

```console
$ while [ ! -f stop ]; do FDQN=vcs.activitypub.securitytxt.dffml.chadig.com WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=push ADMIN_USERNAME=admin ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run start; done
```

- Why do we want notifications broadcast? Because within a poly repo setup or a helper entity setup, we need to be able to provide feedback on opted into please help here areas (contributions of recommended community standards, etc.)
- Package install as feature flags, adding functions to the mix for even more granular feature flags
  - You get all this for free by mirroring events into JSONLD/schema
- `@context/$schema` manifest style content of `Note`, translate to grpc for deno/arua (kris nova's project)
- https://regex101.com/codegen?language=SED

```python
# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re

regex = r"throw new(.*)\);"

test_str = "throw new Error(`Received ${res.status} fetching actor.`);"

subst = "console.error(new\\1));"

# You can manually specify the number of replacements by changing the 4th argument
result = re.sub(regex, subst, test_str, 0, re.MULTILINE)

if result:
    print (result)

# Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.

```

```diff
diff --git a/src/activitypub.ts b/src/activitypub.ts
index a6a90e4..e51aff9 100644
--- a/src/activitypub.ts
+++ b/src/activitypub.ts
@@ -65,13 +65,18 @@ activitypub.post("/:actor/inbox", async (req, res) => {
 
   switch (body.type) {
     case "Follow": {
-      await send(actor, body.actor, {
-        "@context": "https://www.w3.org/ns/activitystreams",
-        id: uri,
-        type: "Accept",
-        actor,
-        object: body,
-      });
+      try {
+        await send(actor, body.actor, {
+          "@context": "https://www.w3.org/ns/activitystreams",
+          id: uri,
+          type: "Accept",
+          actor,
+          object: body,
+        });
+      } catch (err) {
+        console.error(err);
+        return res.sendStatus(401);
+      }
 
       createFollower({ actor: body.actor, uri: body.id });
       break;
diff --git a/src/admin.ts b/src/admin.ts
index d36be9e..55a00ff 100644
--- a/src/admin.ts
+++ b/src/admin.ts
@@ -22,6 +22,7 @@ if (ADMIN_USERNAME && ADMIN_PASSWORD) {
 }
 
 admin.post("/create", async (req, res) => {
+  try {
   const actor: string = req.app.get("actor");
 
   const create = type({ object: omit(Object, ["id"]) });
@@ -59,6 +60,10 @@ admin.post("/create", async (req, res) => {
   }
 
   return res.sendStatus(204);
+  } catch (err) {
+    console.error(err);
+    return res.sendStatus(500);
+  }
 });
 
 admin.post("/follow/:actor/:hostname/:port/:proto", async (req, res) => {
@@ -69,13 +69,19 @@ admin.post("/follow/:actor/:hostname/:port/:proto", async (req, res) => {
   })(req.params);
   const endpoint: string = (FDQN != null ? FDQN: `${HOSTNAME}:${PORT}`);
   const uri = `${PROTO}://${endpoint}/@${crypto.randomUUID()}`;
-  await send(actor, object, {
-    "@context": "https://www.w3.org/ns/activitystreams",
-    id: uri,
-    type: "Follow",
-    actor,
-    object,
-  });
+  try {
+    await send(actor, object, {
+      "@context": "https://www.w3.org/ns/activitystreams",
+      id: uri,
+      type: "Follow",
+      actor,
+      object,
+    });
+  } catch (err) {
+    console.error(err);
+    res.sendStatus(500);
+    return;
+  }
 
   createFollowing({ actor: object, uri });
   res.sendStatus(204);
@@ -88,18 +94,23 @@ admin.delete("/follow/:actor", async (req, res) => {
   const following = getFollowing(object);
   if (!following) return res.sendStatus(204);
 
-  await send(actor, object, {
-    "@context": "https://www.w3.org/ns/activitystreams",
-    id: following.uri + "/undo",
-    type: "Undo",
-    actor: actor,
-    object: {
-      id: following.uri,
-      type: "Follow",
-      actor,
-      object,
-    },
-  });
+  try {
+    await send(actor, object, {
+      "@context": "https://www.w3.org/ns/activitystreams",
+      id: following.uri + "/undo",
+      type: "Undo",
+      actor: actor,
+      object: {
+        id: following.uri,
+        type: "Follow",
+        actor,
+        object,
+      },
+    });
+  } catch (err) {
+    console.error(err);
+    return res.sendStatus(500);
+  }
 
   deleteFollowing({ actor: object, uri: following.uri });
   return res.sendStatus(204);
```

```
src/admin.ts:64:53 - error TS7030: Not all code paths return a value.
                                               
64 admin.post("/follow/:actor/:hostname/:port/:proto", async (req, res) => {
```