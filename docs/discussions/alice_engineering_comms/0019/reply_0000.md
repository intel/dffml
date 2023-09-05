## 2022-09-06 @pdxjohnny Engineering Logs

- User reports need for bypass the validation on insert of each record to mongodb source.
  - https://www.mongodb.com/docs/manual/core/schema-validation/bypass-document-validation/
    - > To bypass the validation rules and insert the invalid document, run the following `insert` command, which sets the `bypassDocumentValidation` option to `true`:
      > ```javascript
      > db.runCommand( {
      >    insert: "students",
      >    documents: [
      >       {
      >          name: "Alice",
      >          year: Int32( 2016 ),
      >          major: "History",
      >          gpa: Double(3.0),
      >          address: {
      >             city: "NYC",
      >             street: "33rd Street"
      >          }
      >       }
      >    ],
      >    bypassDocumentValidation: true
      > } )
      > ```
- References
  - https://duckduckgo.com/?q=validation+level+mongodb&t=canonical&ia=web
  - https://www.mongodb.com/docs/compass/current/validation/
  - https://www.mongodb.com/docs/manual/core/schema-validation/
  - https://www.mongodb.com/docs/manual/core/schema-validation/specify-validation-level/#std-label-schema-specify-validation-level
  - https://www.mongodb.com/docs/manual/core/schema-validation/bypass-document-validation/
- Updating `MongoDBSource`
- References
  - https://duckduckgo.com/?q=motor+mongo+asyncio+bypassDocumentValidation&t=canonical&ia=web
  - https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#inserting-a-document
  - https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_collection.html#motor.motor_asyncio.AsyncIOMotorCollection.insert_one
    - > *bypass_document_validation* requires server version **>= 3.2**
    - *bypass_document_validation*: (optional) If `True`, allows the write to opt-out of document level validation. Default is `False`.
    - https://github.com/intel/dffml/blob/7627341b66f6209b85ea4ae74e3fb4159d125d30/source/mongodb/dffml_source_mongodb/source.py#L32-L39
    - https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_collection.html#motor.motor_asyncio.AsyncIOMotorCollection.replace_one
- TODO
  - [ ] Docs on on open source async first development model in a way which is a quick onramp to the fully connected development model.
  - [ ] Allow for user to bypass the validation on insert of each record to mongodb source.