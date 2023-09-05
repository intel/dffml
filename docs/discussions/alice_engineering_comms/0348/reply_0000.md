- https://github.com/LemmyNet/lemmy/blob/main/docker/Dockerfile
  - https://join-lemmy.org/docs/administration/configuration.html
  - https://join-lemmy.org/docs/contributors/04-api.html#curl-examples
  - https://github.com/LemmyNet/lemmy-js-client/blob/main/src/types/CreatePost.ts

```
$ RUST_BACKTRACE=1 lemmy_server
thread 'main' panicked at 'Error connecting to postgres://lemmy:password@localhost:5432/lemmy: connection to server at "localhost" (127.0.0.1), port 5432 failed: could not initiate GSSAPI security context: Unspecified GSS failure.  Minor code may provide more information: Ticket expired
connection to server at "localhost" (127.0.0.1), port 5432 failed: FATAL:  password authentication failed for user "lemmy"
connection to server at "localhost" (127.0.0.1), port 5432 failed: FATAL:  password authentication failed for user "lemmy"
', crates/db_schema/src/utils.rs:217:56
stack backtrace:
   0: rust_begin_unwind
             at /rustc/eb26296b556cef10fb713a38f3d16b9886080f26/library/std/src/panicking.rs:593:5
   1: core::panicking::panic_fmt
             at /rustc/eb26296b556cef10fb713a38f3d16b9886080f26/library/core/src/panicking.rs:67:14
   2: lemmy_db_schema::utils::run_migrations
   3: lemmy_server::start_lemmy_server::{{closure}}
   4: tokio::runtime::park::CachedParkThread::block_on
   5: tokio::runtime::context::runtime::enter_runtime
   6: tokio::runtime::runtime::Runtime::block_on
   7: lemmy_server::main
note: Some details are omitted, run with `RUST_BACKTRACE=full` for a verbose backtrace.
$ ldd /usr/bin/lemmy_server
        linux-vdso.so.1 (0x00007ffc95d6c000)
        libssl.so.3 => /lib/x86_64-linux-gnu/libssl.so.3 (0x00007fc88180d000)
        libcrypto.so.3 => /lib/x86_64-linux-gnu/libcrypto.so.3 (0x00007fc8813cb000)
        libpq.so.5 => /lib/x86_64-linux-gnu/libpq.so.5 (0x00007fc881379000)
        libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007fc881359000)
        libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007fc881272000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fc881048000)
        /lib64/ld-linux-x86-64.so.2 (0x00007fc884c88000)
        libgssapi_krb5.so.2 => /lib/x86_64-linux-gnu/libgssapi_krb5.so.2 (0x00007fc880ff4000)
        libldap-2.5.so.0 => /lib/x86_64-linux-gnu/libldap-2.5.so.0 (0x00007fc880f95000)
        libkrb5.so.3 => /lib/x86_64-linux-gnu/libkrb5.so.3 (0x00007fc880eca000)
        libk5crypto.so.3 => /lib/x86_64-linux-gnu/libk5crypto.so.3 (0x00007fc880e9b000)
        libcom_err.so.2 => /lib/x86_64-linux-gnu/libcom_err.so.2 (0x00007fc880e95000)
        libkrb5support.so.0 => /lib/x86_64-linux-gnu/libkrb5support.so.0 (0x00007fc880e85000)
        liblber-2.5.so.0 => /lib/x86_64-linux-gnu/liblber-2.5.so.0 (0x00007fc880e74000)
        libsasl2.so.2 => /lib/x86_64-linux-gnu/libsasl2.so.2 (0x00007fc880e59000)
        libgnutls.so.30 => /lib/x86_64-linux-gnu/libgnutls.so.30 (0x00007fc880c6e000)
        libkeyutils.so.1 => /lib/x86_64-linux-gnu/libkeyutils.so.1 (0x00007fc880c67000)
        libresolv.so.2 => /lib/x86_64-linux-gnu/libresolv.so.2 (0x00007fc880c53000)
        libp11-kit.so.0 => /lib/x86_64-linux-gnu/libp11-kit.so.0 (0x00007fc880b16000)
        libidn2.so.0 => /lib/x86_64-linux-gnu/libidn2.so.0 (0x00007fc880af5000)
        libunistring.so.2 => /lib/x86_64-linux-gnu/libunistring.so.2 (0x00007fc88094b000)
        libtasn1.so.6 => /lib/x86_64-linux-gnu/libtasn1.so.6 (0x00007fc880933000)
        libnettle.so.8 => /lib/x86_64-linux-gnu/libnettle.so.8 (0x00007fc8808ed000)
        libhogweed.so.6 => /lib/x86_64-linux-gnu/libhogweed.so.6 (0x00007fc8808a3000)
        libgmp.so.10 => /lib/x86_64-linux-gnu/libgmp.so.10 (0x00007fc880821000)
        libffi.so.8 => /lib/x86_64-linux-gnu/libffi.so.8 (0x00007fc880814000)
```

- TODO
  - https://join-lemmy.org/docs/administration/configuration.html

```
cd server
./db-init.sh
```