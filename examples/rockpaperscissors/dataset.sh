curl -LO https://storage.googleapis.com/laurencemoroney-blog.appspot.com/\{rps,rps-test-set,rps-validation\}.zip
sha384sum -c - << EOF
c6a9119b0c6a0907b782bd99e04ce09a0924c0895df6a26bc6fb06baca4526f55e51f7156cceb4791cc65632d66085e8  rps.zip
fc45a0ebe58b9aafc3cd5a60020fa042d3a19c26b0f820aee630b9602c8f53dd52fd40f35d44432dd031dea8f30a5f66  rps-test-set.zip
375457bb95771ffeace2beedab877292d232f31e76502618d25e0d92a3e029d386429f52c771b05ae1c7229d2f5ecc29  rps-validation.zip
EOF