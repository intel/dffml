## 2024-03-09 @pdxjohnny Engineering Logs

- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/pull/196
- https://github.com/svix/svix-webhooks/tree/main/bridge#svix-bridge-beta
- https://github.com/risingwavelabs/risingwave
- https://github.com/postgresml/postgresml
- https://the-fonz.gitlab.io/posts/postgres-notify/
- https://docs.hatchet.run/home/tutorials/fastapi-react/result-streaming
- https://github.com/sigstore/scaffolding
- https://github.com/sigstore/scaffolding/blob/24f4e5b777fee691e76b51706689058961d5eb45/actions/setup/action.yml#L56-L155

**sigstore_scaffolding.sh**

```bash
      set -ex


      # Determine which version to install
      # - if version is "latest-release", look up latest release.
      # - otherwise, install the specified version.
      case ${{ inputs.version }} in
      latest-release | main)
        tag=$(curl -s -u "username:${{ github.token }}" https://api.github.com/repos/sigstore/scaffolding/releases/latest | jq -r '.tag_name')
        ;;
      *)
        tag="${{ inputs.version }}"
      esac


      # At release v0.5.0 we added support for TSA. Check if we're running
      # greater than v0.5.0 and install it.
      # the install process, so check to see if we are running >=5
      MINOR=$(echo $tag | cut -d '.' -f 2)
      INSTALL_TSA="false"
      if [ ${MINOR} -ge 5 ]; then
        INSTALL_TSA="true"
      fi
      # Anything older than 0.4.0 is not supported.
      if [ ${MINOR} -lt 4 ]; then
        echo Unsupported version, only support versions >= 0.4.0
        exit 1
      fi


      if [ ${{ inputs.sigstore-only }} == "false" ]; then
        # Configure DockerHub mirror
        tmp=$(mktemp)
        jq '."registry-mirrors" = ["https://mirror.gcr.io"]' /etc/docker/daemon.json > "$tmp"
        sudo mv "$tmp" /etc/docker/daemon.json
        sudo service docker restart


        echo "Installing kind and knative using release"


        if [ "${{ inputs.version }}" != "main" ]; then
          curl -fLo ./setup-kind.sh https://github.com/sigstore/scaffolding/releases/download/${tag}/setup-kind.sh
        else
          cp ${{ github.action_path }}/../../hack/setup-kind.sh .
        fi


        chmod u+x ./setup-kind.sh
        ./setup-kind.sh \
          --registry-url ${{ inputs.registry-name }}:${{ inputs.registry-port }} \
          --cluster-suffix ${{ inputs.cluster-suffix }} \
          --k8s-version ${{ inputs.k8s-version }} ${{ inputs.knative-version != '' && format('--knative-version {0}', inputs.knative-version) || '' }}
      fi


      if [ "${{ inputs.version }}" != "main" ]; then
        echo "Installing sigstore scaffolding @ ${tag}"
        curl -fLo /tmp/setup-scaffolding-from-release.sh https://github.com/sigstore/scaffolding/releases/download/${tag}/setup-scaffolding-from-release.sh
      else
        cp ${{ github.action_path }}/../../hack/setup-scaffolding-from-release.sh /tmp/
      fi
      # Temp hack to address issuer mismatch issue.
      # Can be removed with the next release, after v0.6.5
      sed -i "s@kubectl apply -f \"\${FULCIO}\"@curl -Ls \"\${FULCIO}\" | sed 's#\"IssuerURL\": \"https://kubernetes.default.svc\",#\"IssuerURL\": \"https://kubernetes.default.svc.cluster.local\",#' | kubectl apply -f -@" /tmp/setup-scaffolding-from-release.sh
      chmod u+x /tmp/setup-scaffolding-from-release.sh
      cat /tmp/setup-scaffolding-from-release.sh
      if [ "${{ inputs.version }}" != "main" ]; then
        /tmp/setup-scaffolding-from-release.sh --release-version ${tag}
      else
        /tmp/setup-scaffolding-from-release.sh
      fi


      TUF_MIRROR=$(kubectl -n tuf-system get ksvc tuf -ojsonpath='{.status.url}')
      echo "TUF_MIRROR=$TUF_MIRROR" >> $GITHUB_ENV
      # Grab the trusted root
      kubectl -n tuf-system get secrets tuf-root -ojsonpath='{.data.root}' | base64 -d > ${{ inputs.working-directory }}/root.json


      # Make copy of the tuf root in the default namespace for tests
      kubectl -n tuf-system get secrets tuf-root -oyaml | sed 's/namespace: .*/namespace: default/' | kubectl create -f -


      echo "Installing and running scaffolding tests to verify we are up and running"
      curl -fL https://github.com/sigstore/scaffolding/releases/download/${tag}/testrelease.yaml | kubectl create -f -


      kubectl wait --for=condition=Complete --timeout=180s job/sign-job
      kubectl wait --for=condition=Complete --timeout=180s job/verify-job


      REKOR_URL=$(kubectl -n rekor-system get ksvc rekor -ojsonpath='{.status.url}')
      FULCIO_URL=$(kubectl -n fulcio-system get ksvc fulcio -ojsonpath='{.status.url}')
      FULCIO_GRPC_URL=$(kubectl -n fulcio-system get ksvc fulcio-grpc -ojsonpath='{.status.url}')
      CTLOG_URL=$(kubectl -n ctlog-system get ksvc ctlog -ojsonpath='{.status.url}')
      ISSUER_URL=$(kubectl get ksvc gettoken -ojsonpath='{.status.url}')
      if [ $INSTALL_TSA == "true" ] ; then
        TSA_URL=$(kubectl -n tsa-system get ksvc tsa -ojsonpath='{.status.url}')
        echo "TSA_URL=$TSA_URL" >> $GITHUB_ENV
      fi


      # Grab an OIDC token too.
      OIDC_TOKEN=$(curl -s $ISSUER_URL)
      echo "OIDC_TOKEN=$OIDC_TOKEN" >> $GITHUB_ENV


      # And set the env variables for Github action visibility
      echo "REKOR_URL=$REKOR_URL" >> $GITHUB_ENV
      echo "FULCIO_URL=$FULCIO_URL" >> $GITHUB_ENV
      echo "FULCIO_GRPC_URL=$FULCIO_GRPC_URL" >> $GITHUB_ENV
      echo "CTLOG_URL=$CTLOG_URL" >> $GITHUB_ENV
      echo "ISSUER_URL=$ISSUER_URL" >> $GITHUB_ENV
```