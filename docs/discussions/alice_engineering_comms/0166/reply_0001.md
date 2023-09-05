## 2023-02-02 Exporting Groovy Functions

- 1:1 Pankaj/John
- Update 2023-02-15: This became https://github.com/intel/dffml/commit/15c9c245add1fae5a0b1767ed77973d9dbdd4899
- https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst#writing-an-overlay
- https://docs.groovy-lang.org/latest/html/api/org/apache/groovy/parser/antlr4/package-summary.html
  - https://docs.groovy-lang.org/latest/html/api/org/apache/groovy/parser/antlr4/GroovyLangParser.html
  - https://www.graalvm.org/
  - https://www.graalvm.org/latest/reference-manual/native-image/
- First we create another operation which takes groovy files
  - Define `NewType("GroovyFunction", str)` as output
  - Remove `output=Stage.OUTPUT`

https://github.com/intel/dffml/blob/d77e2f697d806f71ab7dcf64a74cadfe5eb79598/entities/alice/alice/shouldi/contribute/cicd.py#L26-L33

- Then we do the Groovy equivalent of returning a list of functions (seen here in python AST example)

https://github.com/intel/dffml/blob/d77e2f697d806f71ab7dcf64a74cadfe5eb79598/examples/operations/python.py#L61-L66

```patch
diff --git a/entities/alice/alice/shouldi/contribute/cicd.py b/entities/alice/alice/shouldi/contribute/cicd.py
index 3237a1990..e682e3aeb 100644
--- a/entities/alice/alice/shouldi/contribute/cicd.py
+++ b/entities/alice/alice/shouldi/contribute/cicd.py
@@ -33,6 +33,32 @@ def cicd_jenkins_library(
     return bool(groovy_file_paths)
 
 
+GroovyFunction = NewType("GroovyFunction", str)
+
+@dffml.op
+def groovy_functions(
+    groovy_file_paths: dffml_operations_innersource.operations.GroovyFileWorkflowUnixStylePath,
+) -> List[GroovyFunction]:
+    # TODO Probably need to require namspacing of functions somehow
+    # Might need to update the stdlib qualifications spec
+    """
+
+
+    groovy_file_url = "https://github.com/apache/groovy/raw/74baecf4b3990f84003929c0c31ec150d5d305cf/src/test/groovy/transform/stc/DelegatesToSTCTest.groovy"
+    $ wget https://github.com/apache/groovy/raw/74baecf4b3990f84003929c0c31ec150d5d305cf/src/test/groovy/transform/stc/DelegatesToSTCTest.groovy
+    $ GROOVY_FILE=DelegatesToSTCTest.groovy python -um doctest path/to/this/file.py
+
+    >>> import os
+    >>> groovy_functions(os.environ["GROOVY_FILE"])
+    ["testShouldChooseMethodFromOwner", "testShouldChooseMethodFromDelegate", ""]
+    TODO List rest of funtion names or choose samller file
+    """
+    # Example:
+    # void testShouldChooseMethodFromOwner() {
+    # yield line if line.strip().endswith(") {") and not "=" in line.
+    return []
+
+
 @dffml.op(
     stage=dffml.Stage.OUTPUT,
 )
```