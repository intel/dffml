## 2024-03-25 @pdxjohnny Engineering Logs

```bash
(set -x; for dir in $(find . -name pyproject.toml -or -name setup.cfg -or -name setup.py | sed -e 's/\/pyproject.toml//g' -e 's/\/setup\..*//g' | sort | uniq | grep -v skel/ | grep -v tutorials/ | tee /dev/stderr); do mkdir -p build_logs/${dir}; (python -m build $dir | tee build_logs/${dir}/logs.txt) & done; set +x)
echo Wait for all processes to complete
for package_name in $(find build_logs/ -name logs.txt -exec bash -ec "grep creating\  {} | head -n 1" \; | sed -E 's/\-([0-9])+.*//g;t' | awk '{print $NF}'); do curl -sfL "https://pypi.org/pypi/${package_name}/json" 2>/dev/null 1>&2 || echo $package_name does not exist in pypi; done
```

- https://www.markhneedham.com/blog/2023/10/03/mistral-ai-own-machine-ollama/
  - https://docs.llamaindex.ai/en/stable/
- https://github.com/ollama/ollama/blob/main/docs/faq.md#setting-environment-variables-on-linux
- https://python.langchain.com/docs/integrations/chat/ollama_functions
- https://huggingface.co/teknium/OpenHermes-2.5-Mistral-7B
- https://python.langchain.com/docs/integrations/vectorstores/pgvector
- https://github.com/pgvector/pgvector?tab=readme-ov-file#docker
- https://langchain-doc.readthedocs.io/en/latest/modules/indexes/chain_examples/vector_db_qa_with_sources.html
- https://docs.litellm.ai/docs/proxy/call_hooks
- https://medium.com/@sauravjoshi23/enhancing-rag-with-decision-making-agents-and-neo4j-graph-chain-tools-using-langchain-templates-and-0ee7d1185e48

```json
{
    "issuer": "/",
    "jwks": {
        "keys": {
            "NOTE This is the /token/issue key\"PoeK6pwcxtUVnzLs9u0ObI9ifi8FqXQlSdg-odiAR1g": {
                "d": "GuJgS6DVkn_EbpgrTP1nGqQaNRxfeSn_dwe4kVgHcyxv9kLuamZQjlC2d4Wuy94hlib-GGHt6FuwcNieER2fLZhNqmhzbI-z4P0hD7qam1D0oZ522y14VTWqyqb9pIA32s5IdNNwh-0_wRaoWsWHhqrVj-Mg51wWcJnAvUYO2OzjLWgqMgePOk1WfVmZHfsNSY87jEvG3ypdtN4-P-biJVEWEa1psYFYIRBonJVZfM8UmSxTN0-sIlnqC2_Hwv7OJPxBNFO0_0p_K00FVCGuY8Uyc_x0n6sAfNmVz6s-Rm6TSj1R8sGrNnIY2oKge0Trok1C4vV39kiAjbuT5zL4WQ",
                "dp": "LqnFJ9IMwwcgedMcqismOezp9APaVGhwt27ZBuOZWDmCkEYsNRlxIfmSBJN6kFOo4gPwe9FrT-bfwKmoe65H8ECOC20t4V0qKPZN5xu-bkCKL9GUmdDcpQCLBP6aEzLrMUnRbtrS_-l8wt308pxbX6ATWfbMgVVW-jRH5EWGfzk",
                "dq": "Vvx4txZ5Zho2guZ0GNh9qpAjwic2GoHvRHxrD3mG6y5pH4A6BHbx2EoF0iw_d0rHQ2kEtkWI35c7cTc3OhbFbPn6ONirl8N-6Pkb79W9ZVRq65N300SncKsbxC9fZEMV5qlgpuUDg5heMhUUH1T1UFd80BzRPhwB714tzq1MgpE",
                "e": "AQAB",
                "kty": "RSA",
                "n": "x6f2QMResjMZEToq-18lYxR_eR-dh2hMrCWOLw5RPxloqgVBfar1ODTC-nw93SSowWSW-bLM1CIqyi6hRQLqrVvyAlawge-5WnVjPngYBHRpspdmH8oHSVt5Qs81Ju8IWR7hemUBnQdAFYlv8AqgRIfMnc09_D44HAdR-U62imrPUaL5JaLcaIW3QrjAPTy_TgpITOAJtC0kzyV2-6AY6AFvSdoL4WKLcFGtBQMfAdDzjEq4CZzwlm0WB56sL6u1yzD-3RqU5w4C3u552jrWf2jN6iNMQo4OS1I1o7eutOG3l3r1WoxN_WUVArP4IW_Rvs3kEgTzsR5SLhxKotzv1Q",
                "p": "_ncdC96G0W7MmUalU3RxFzM_oC6oSVX0J1sNSVUq-4CXiI66wUgA7MIu6KSZR9VAqgCmUOaMMPRcsZkubEUX9ECMrIZPznmp0TtoG8_kQ_jaIj9m33CmyXN_HeYptDAxKwH5n7kmBHDpYq7sSXmWg-LsUYCVy0wNc-gERaSiKX0",
                "q": "yNw5itfwPRQepCtJN2epAScc3bKKTp3vR_UHH-rX1QqqBb-vOZKzajvpF2qAp3_6WvVNuesaOMDoIzy-SyKKnTEUGoIbBvkdbUQbkrH0KFpYNq55QDUPlIHH4_VsyyX08H9aeJd7c1N8QsasB4OkC7uj7BlW_s14soVb_dz-7zk",
                "qi": "LGq21q8aT4YdJHpDaYybm6bxifoM3RqWz_3WOg1izA47VTWos9_yI0Iz9gNALVgJcbsIQpBWX9Fg3uHySW7mLmp0Loy6irFIPg2mo1v1qxIthzacA8s7LyrqMtZQZC8B3218jmPZ1OjLyWXJ6h2XGSxQDjKsN6L-HUNaJ3EZbWo"
            },
            "NOTE This is the workspace/storage/service_parameter_key.pem key\"UhK6Y0danl_SnjjyZB55P-3lZ5PSXoTppBPPwZUQpfk": {
                "crv": "P-256",
                "kid": "UhK6Y0danl_SnjjyZB55P-3lZ5PSXoTppBPPwZUQpfk",
                "kty": "EC",
                "use": "sig",
                "x": "kTLJqocbtW8C4XtgANdC6lSPIeOGk0w9goN6pvChVEA",
                "y": "YD-Ra2axyY_AnwSUtD5BMmVHrqTUbcFIbjz-BN9jdtU"
            }
        }
    },
    "nonce_endpoint": "/nonce",
    "registration_endpoint": "/entries",
    "registration_policy": "/statements/TODO",
    "supported_signature_algorithms": [
        "RS256"
    ]
}
```

- Got LiteLLM sending transparent statement URNs to relying party phase 0 to get workload identity token for tool call
  - litellm 3b6b7427b15c0cadd23a8b5da639e22a2fba5043