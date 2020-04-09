dffml service http server -insecure -cors '*' -addr 0.0.0.0 -port 8080 \
  -models mymodel=scikitlr \
  -model-features Years:int:1 Expertise:int:1 Trust:float:1 \
  -model-predict Salary:float:1
