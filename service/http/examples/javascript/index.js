var runit = async function() {
  // Create an instance of the API class, use the same URL we are on as the
  // endpoint
  var api = new DFFMLHTTPAPI(window.location.origin);

  console.log("Created api", window.location.origin, api);

  // Training data and source
  var training_source = api.source();
  console.log("Created training_source", training_source);

  var training_csv_contents = "Years,Expertise,Trust,Salary\n";
  training_csv_contents += "0,1,0.2,10\n";
  training_csv_contents += "1,3,0.4,20\n";
  training_csv_contents += "2,5,0.6,30\n";
  training_csv_contents += "3,7,0.8,40\n";

  await api.upload("my_training_dataset.csv", training_csv_contents);
  console.log("Uploaded my_training_dataset.csv");

  await training_source.configure("csv", "my_training_dataset", {
    "source": {
      "plugin": null,
      "config": {
        "filename": {
          "plugin": [
            "my_training_dataset.csv"
          ],
          "config": {}
        }
      }
    }
  });
  console.log("Configured training_source", training_source);

  var training_sctx = await training_source.context("my_training_dataset_context");
  console.log("Created training_sctx", training_sctx);

  // Test data and source

  var test_source = api.source();
  console.log("Created test_source", test_source);

  var test_csv_contents = "Years,Expertise,Trust,Salary\n";
  test_csv_contents += "4,9,1.0,50\n";
  test_csv_contents += "5,11,1.2,60\n";

  await api.upload("my_test_dataset.csv", test_csv_contents);
  console.log("Uploaded my_test_dataset.csv");

  await test_source.configure("csv", "my_test_dataset", {
    "source": {
      "plugin": null,
      "config": {
        "filename": {
          "plugin": [
            "my_test_dataset.csv"
          ],
          "config": {}
        }
      }
    }
  });
  console.log("Configured test_source", test_source);

  var test_sctx = await test_source.context("my_test_dataset_context");
  console.log("Created test_sctx", test_sctx);

  // Create an array of all the records for fun
  var records = await training_sctx.records(100);
  console.log("Training records", records);

  var records_array = [];
  for (var key of Object.keys(records)) {
    records_array.push(records[key]);
  }
  console.log("Array of training records", records_array);

  // Create a model
  var model = api.model();
  console.log("Created model", model);

  await model.configure("scikitlr", "mymodel", {
    "model": {
      "plugin": null,
      "config": {
        "predict": {
          "plugin": [{
            "name": "Salary",
            "dtype": "int",
            "length": 1
          }, ],
          "config": {}
        },
        "features": {
          "plugin": [{
            "name": "Years",
            "dtype": "int",
            "length": 1
          }, {
            "name": "Expertise",
            "dtype": "int",
            "length": 1
          }, {
            "name": "Trust",
            "dtype": "float",
            "length": 1
          }],
          "config": {}
        }
      }
    }
  });

  console.log("Configured model", model);

  var mctx = await model.context("mymodel_context");
  console.log("Created model context", mctx);

  await mctx.train([training_sctx]);
  console.log("Trained model context", mctx);

  // Create a scorer
  var scorer = api.scorer();
  console.log("Created scorer", scorer);

  await scorer.configure("mse", "mymse", {});
  console.log("Configured scorer", scorer);

  var actx = await scorer.context("mymse_context");
  console.log("Created scorer context", actx);

  var accuracy = await actx.score([test_sctx]);
  console.log("Scorer accuracy", accuracy);

  var prediction = await mctx.predict({
    "mish_the_smish": {
      "features": {
        "Years": 6,
        "Expertise": 13,
        "Trust": 1.4
      }
    }
  });
  console.log("Model context predict", prediction);

  if (prediction.mish_the_smish.prediction.Salary.value !== 70) {
    console.error(prediction)
    throw new Error("prediction.mish_the_smish.prediction.value was not 70!");
  }

  console.log("Success!");
}

runit();