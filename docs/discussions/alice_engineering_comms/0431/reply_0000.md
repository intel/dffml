## 2023-10-25 @pdxjohnny Engineering Logs

- https://github.com/scitt-community/scitt-api-emulator/pull/37/commits/eec108d4cd0405fb54251fd647fa7d4340816129

[![asciicast](https://asciinema.org/a/617161.svg)](https://asciinema.org/a/617161)

```
$ caddy run --config Caddyfile
```

```caddyfile
vcs.activitypub.securitytxt.dffml.chadig.com {
  reverse_proxy http://localhost:8000
}

scitt.alice.chadig.com {
  reverse_proxy http://localhost:6000
}

scitt.bob.chadig.com {
  reverse_proxy http://localhost:7000
}

scitt.pdxjohnny.chadig.com {
  reverse_proxy http://localhost:9000
}
```

```console
$ curl -vfL https://scitt.alice.chadig.com/.well-known/webfinger?resource=acct:alice@scitt.alice.chadig.com 2>&1 | grep -A 9999 HTTP\/2\ 404
< HTTP/2 404
< alt-svc: h3=":443"; ma=2592000
< content-type: application/json
< date: Wed, 25 Oct 2023 21:13:22 GMT
< server: Caddy
< server: hypercorn-h11
< content-length: 28
* The requested URL returned error: 404
* TLSv1.2 (OUT), TLS header, Supplemental data (23):
} [5 bytes data]
* stopped the pause stream!
  0    28    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
* Connection #0 to host (nil) left intact
curl: (22) The requested URL returned error: 404
$ curl -sfL https://scitt.bob.chadig.com/.well-known/webfinger?resource=acct:bob@scitt.bob.chadig.com | jq
{
  "links": [
    {
      "href": "https://scitt.bob.chadig.com/endpoints/ze5hNSaB3WsbIBQ_cPmu3wjo6zTo7_amyhxbE3KDuj4",
      "rel": "self",
      "type": "application/activity+json"
    }
  ],
  "subject": "acct:bob@scitt.bob.chadig.com"
}
```


```console
$ ssh -nNT -R 127.0.0.1:7000:0.0.0.0:7000 alice@scitt.alice.chadig.com
$ ssh -nNT -R 127.0.0.1:6000:0.0.0.0:6000 alice@scitt.bob.chadig.com
```