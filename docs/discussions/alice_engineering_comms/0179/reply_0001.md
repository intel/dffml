## 2023-02-15 Groovy Functions

- 1:1 Pankaj/John
- The antlr4 definition of a Groovy parser is https://github.com/apache/groovy/blob/master/src/antlr/GroovyParser.g4
- We will use https://docs.groovy-lang.org/latest/html/api/org/apache/groovy/parser/antlr4/GroovyLangParser.html to leverage that parser and output a JSON for the AST, which we'll wrap with Gravel native, and `_ensure` the helper binary exists.
- https://github.com/ietf-scitt/use-cases/blob/fd2828090482fe63a30a7ddd9e91bdb78892a01e/openssf_metrics.md#activitypub-extensions-for-securitytxt

```diff
diff --git a/entities/alice/alice/please/log/todos/todos.py b/entities/alice/alice/please/log/todos/todos.py                                                                                                     index c7e77f110..1f35b203a 100644
--- a/entities/alice/alice/please/log/todos/todos.py
+++ b/entities/alice/alice/please/log/todos/todos.py
@@ -332,3 +332,45 @@ class AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues:                                                                                                                                  logger=self.logger,
             )
         }
+
+    async def db_add_created_issue_security(
+        # db: MongoConnection,
+        issue_url: SecurityIssueURL,
+    ):
+        import code; code.interact(local=locals())
+        record.features.tags.append({
+            "issue_url": issue_url,
+        })
+        # Update DB
+        await db.update(...)
+
+
+"""
+    # Closing issue is not a priority
+
+    async def gh_issue_close_readme_if_fixed(
+        file_present: dffml_operations_innersource.operations.FileReadmePresent,                                                                                                                                +    ) -> ReadmeIssueURLClosed:
+        # Bail if it exists now
+        if not file_present:
+            return
+        # Check if the issue is still open
+        # issue_url = $ gh issue list | grep "Recommended Community Standard: README"                                                                                                                           +        # NOTE Should also check that we were the ones that opened this. Not a                                                                                                                                  +        # priority though.
+        if not issue_url:
+            return
+        # Close the issue if it exists
+        # $ gh issue close issue_url
+        return closed_issue_url
+
+    async def db_remove_closed_issue(
+        db: MongoConnection,
+        closed_issue_url: ReadmeIssueURLClosed,
+    ):
+        # Loop through features.tags
+        if item["issue_url"] == closed_issue_url:
+            del features.tags[index_of_item]
+        # Update DB
+        await db.update(...)
+"""
```