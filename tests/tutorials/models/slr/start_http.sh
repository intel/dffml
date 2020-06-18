dffml service http server -insecure -cors '*' -addr 0.0.0.0 -port 8080 \
  -models mymodel=myslr:MySLRModel \
  -model-feature Years:int:1 \
  -model-predict Salary:float:1 \
  -model-directory modeldir
