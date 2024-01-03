## 2023-12-15 @pdxjohnny Engineering Logs

- [puerco](https://github.com/puerco) created new OpenVEX GitHub Action
  - https://github.com/openvex/generate-vex/pull/1
    - Once we issue vulns using Vulnerability Description Ontology (VDO) we’ll have all the basics for our decentralized Data Analysis Control loop
      - 🛤️🛤️🛤️🛤️🛤️🛤️🛤️

```yaml
    - uses: openvex/generate-vex@159b7ee4845fb48f1991395ce8501d6263407360
      name: Run vexctl
      id: vexctl
      with:
        product: pkg:github/${{ github.repository }}@${{ github.sha }}
    - name: Submit OpenVEX to SCITT
      id: scitt-submit-openvex
      uses: scitt-community/scitt-api-emulator@f1f5c16630a28511e970b6903fbc4c0db6c07654
      with:
        issuer: did:web:raw.githubusercontent.com:intel:dffml:public-keys:authorized_keys
        subject: pkg:github/${{ github.repository }}@${{ github.sha }}
        payload: ${{ steps.vexctl.outputs.openvex }}
        private-key-pem: private-key.pem
        scitt-url: https://scitt.unstable.chadig.com
```

![chaos-for-the-chaos-god](https://github.com/intel/dffml/assets/5950433/636969a1-1f0f-4c96-8812-f10fa403e79c)

- https://loop.online/claw
- TODO
  - [x] Submit OpenVEX to SCITT
    - https://github.com/openvex/generate-vex/pull/1
    - https://github.com/intel/dffml/actions/runs/7225714933/job/19689765921
    - https://view.scitt.unstable.chadig.com/entry/sha384:c6b4005b1442fd02c825b50ebbb83dc4e4a245f9b3504461c7a3c6a88c61b6eae1d0733d41f70bc99c7ff34a09de8c40/