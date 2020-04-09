curl http://localhost:8080/model/mymodel/predict/0 \
  --header "Content-Type: application/json" \
  --data '{"0": {"features": {"Expertise": 17, "Trust": 0.9, "Years": 8}}}' \
  | python -m json.tool
