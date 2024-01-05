## 2023-12-12 @pdxjohnny Engineering Logs

- https://github.com/madox2/vim-ai
- https://github.com/pdxjohnny/httptest/blob/56fc2cfea40519e5f06972ba4d7ae7531bb5de10/.github/workflows/tests.yml#L44-L130

```yaml
    - name: Generate SBOM
      id: generate-sbom
      uses: pdxjohnny/sbom4python@github-action
      with:
        python-version: ${{ matrix.python-version }}
        module-name: httptest
        output-directory: sbom
    - name: in-toto attestation for cyclonedx SBOM
      id: in-toto-cyclonedx
      env:
        MODULE_NAME: httptest
      run: |
        echo "attestation<<GITHUB_OUTPUT_EOF" >> $GITHUB_OUTPUT
        (python -m json.tool --sort-keys | tee -a $GITHUB_OUTPUT) <<EOF
        {
          "_type": "https://in-toto.io/Statement/v0.1",
          "subject": [
            {
              "name": "$(cd dist/ && echo *.tar.gz)",
              "digest": {"sha256": "$(cd dist/ && sha256sum $(echo *.tar.gz) | awk '{print $1}')"}
            },
            {
              "name": "$(cd dist/ && echo *.whl)",
              "digest": {"sha256": "$(cd dist/ && sha256sum $(echo *.whl) | awk '{print $1}')"}
            }
          ],
          "predicateType": "https://cyclonedx.org/bom/v1.4",
          "predicate": $(cat "${MODULE_NAME}-py${{ matrix.python-version }}.json")
        }
        EOF
        echo "GITHUB_OUTPUT_EOF" >> $GITHUB_OUTPUT
    - name: Checkout public-keys branch
      uses: actions/checkout@v4
      with:
        ref: public-keys
        path: public-keys
    - name: Generate keypair to sign SCITT statement
      id: scitt-gen-keypair
      run: |
        ssh-keygen -q -f ssh-private -t ecdsa -b 384 -N '' -I "$(date -Iseconds)" <<<y
        cat ssh-private | python -c 'import sys; from cryptography.hazmat.primitives import serialization; print(serialization.load_ssh_private_key(sys.stdin.buffer.read(), password=None).private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode().rstrip())' > private-key.pem
        cat ssh-private.pub | tee -a public-keys/authorized_keys
        rm -v ssh-private
    - name: Push new public key
      env:
        GH_TOKEN: ${{ github.token }}
      run: |
        set -xe
        cd public-keys
        gh auth setup-git
        git config --global --add safe.directory "${PWD}"
        git config --global user.email "actions@github.com"
        git config --global user.name "GitHub Actions"
        git add -A
        # If no delta clean exit
        git commit -sm "Snapshot" || exit 0
        git push -uf origin "HEAD:public-keys"
        # Wait for propagation
        set +e
        found=1
        while [ ${found} -eq 1 ]; do
          curl -vfL https://raw.githubusercontent.com/pdxjohnny/httptest/public-keys/authorized_keys | tee authorized_keys
          grep "$(cat ../ssh-private.pub)" authorized_keys
          found=$?
        done
    - name: Submit SBOM to SCITT
      id: scitt-submit-sbom
      uses: pdxjohnny/scitt-api-emulator@github-action
      with:
        issuer: did:web:raw.githubusercontent.com:pdxjohnny:httptest:public-keys:authorized_keys
        subject: pkg:github/${{ github.repository }}@${{ github.sha }}
        payload: ${{ steps.in-toto-cyclonedx.outputs.attestation }}
        private-key-pem: private-key.pem
        scitt-url: https://scitt.unstable.chadig.com
    - name: Remove private key used in keypair to sign SCITT statement
      run: |
        rm -v private-key.pem
    - name: Create Pull Request
      if: ${{ steps.generate-sbom.outputs.changed }}
      uses: peter-evans/create-pull-request@v5.0.2
      with:
        commit-message: "chore: update SBOM for Python ${{ matrix.python-version }}"
        title: "chore: update SBOM for Python ${{ matrix.python-version }}"
        branch: chore-sbom-py${{ matrix.python-version }}
        delete-branch: true
        author: GitHub Actions <actions@github.com>
        add-paths: sbom
```

- TODO
  - [x] in-toto cyclonedx for httptest to unstable SCITT instance
    - [x] `public-keys` branch based discovery of authorized notary signing keys