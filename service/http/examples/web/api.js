"use strict";
/*
 * From the examples/web directory run
 *
 * $ python3.7 -m http.server 9090
 * $ dffml service http -insecure -cors '*' -port 8080 -upload-dir .
 *
 * Or for a temp directory to upload to run:
 *
 * $ cd $(mktemp -d) && dffml service http server -insecure -cors '*' -log debug -upload-dir .
 *
 * Go to http://localhost:9090/
 * Open the console and call the runit() function (type runit() and press enter)
 */

class DFFMLHTTPAPIObjectContext {
  constructor(api, parent, label) {
    this.api = api;
    this.parent = parent;
    this.label = label;
  }
}

class DFFMLHTTPAPISourceContext extends DFFMLHTTPAPIObjectContext {
  async repos(chunk_size) {
    // TODO https://www.codementor.io/tiagolopesferreira/asynchronous-iterators-in-javascript-jl1yg8la1
    var response = await this.api.request("/source/" + this.label + "/repos/" + chunk_size);

    response = await response.json();

    return response.repos;
  }

  async update(repo) {
    // https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
    var response = await this.api.request("/source/" + this.label + "/update/" + repo.src_url, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      mode: 'cors', // no-cors, cors, *same-origin
      cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      credentials: 'omit', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'follow', // manual, *follow, error
      referrer: 'no-referrer', // no-referrer, *client
      body: JSON.stringify(repo), // body data type must match "Content-Type" header
    });

    await response.json();
  }
}

class DFFMLHTTPAPIModelContext extends DFFMLHTTPAPIObjectContext {
  async train(sources) {
    var source_context_names = [];
    for (var sctx of sources) {
      source_context_names.push(sctx.label);
    }

    var response = await this.api.request("/model/" + this.label + "/train", {
      method: 'POST',
      mode: 'cors',
      cache: 'no-cache',
      credentials: 'omit',
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'follow',
      referrer: 'no-referrer',
      body: JSON.stringify(source_context_names),
    });

    response = await response.json();

    return response.repos;
  }

  async accuracy(sources) {
    var source_context_names = [];
    for (var sctx of sources) {
      source_context_names.push(sctx.label);
    }

    var response = await this.api.request("/model/" + this.label + "/accuracy", {
      method: 'POST',
      mode: 'cors',
      cache: 'no-cache',
      credentials: 'omit',
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'follow',
      referrer: 'no-referrer',
      body: JSON.stringify(source_context_names),
    });

    response = await response.json();

    return response.repos;
  }

  async predict(repos) {
    var response = await this.api.request("/model/" + this.label + "/predict/0", {
      method: 'POST',
      mode: 'cors',
      cache: 'no-cache',
      credentials: 'omit',
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'follow',
      referrer: 'no-referrer',
      body: JSON.stringify(repos),
    });

    response = await response.json();

    return response.repos;
  }
}

class DFFMLHTTPAPIObject {
  constructor(plugin_type, context_cls, api) {
    this.plugin_type = plugin_type;
    this.context_cls = context_cls;
    this.api = api;
    this.plugin = null;
    this.label = null;
    this.config = {};
  }

  async configure(plugin, label, config) {
    var response = await this.api.request("/configure/" + this.plugin_type + "/" + plugin + "/" + label, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      mode: 'cors', // no-cors, cors, *same-origin
      cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      credentials: 'omit', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'follow', // manual, *follow, error
      referrer: 'no-referrer', // no-referrer, *client
      body: JSON.stringify(config), // body data type must match "Content-Type" header
    });

    response = await response.json();

    this.plugin = plugin;
    this.label = label;
    this.config = config;

    return response;
  }

  async context(ctx_label) {
    var response = await this.api.request("/context/" + this.plugin_type + "/" + this.label + "/" + ctx_label);

    await response.json();

    return new this.context_cls(this.api, this, ctx_label);
  }
}

class DFFMLHTTPAPISource extends DFFMLHTTPAPIObject {
  constructor(api) {
    super("source", DFFMLHTTPAPISourceContext, api);
  }
}

class DFFMLHTTPAPIModel extends DFFMLHTTPAPIObject {
  constructor(api) {
    super("model", DFFMLHTTPAPIModelContext, api);
  }

  async context(ctx_label, features) {
    var response = await this.api.request("/context/" + this.plugin_type + "/" + this.label + "/" + ctx_label, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      mode: 'cors', // no-cors, cors, *same-origin
      cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      credentials: 'omit', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'follow', // manual, *follow, error
      referrer: 'no-referrer', // no-referrer, *client
      body: JSON.stringify(features), // body data type must match "Content-Type" header
    });

    await response.json();

    return new this.context_cls(this.api, this, ctx_label);
  }
}

class DFFMLHTTPAPI {
  constructor(endpoint) {
    this.endpoint = endpoint;
  }

  async request(path, options) {
    const url = this.endpoint + path;
    const response = await fetch(url, options);
    if (response.status < 400) {
      return response;
    }

    const message = await response.json();
    if (message.hasOwnProperty("error") &&
      typeof message.error === "string") {
      throw new Error(message.error);
    }

    throw new Error("Unknown error occured");
  }

  /* upload
   * path: Path to place uploaded file at
   * file: String of file contents or input_element.files[0]
   */
  async upload(path, file) {
    const formData = new FormData();

    if (typeof file === "string") {
      file = new Blob([file], {
        type: "application/octet-stream"
      });
    }

    formData.append('file', file);

    const response = await this.request("/service/upload/" + path, {
      method: 'POST',
      body: formData
    });

    return await response.json();
  }

  source() {
    return new DFFMLHTTPAPISource(this);
  }

  model() {
    return new DFFMLHTTPAPIModel(this);
  }
}

var runit = async function() {
  /*
   * This is an example of how to use the HTTP api from JavaScript
   *
   * The following line creates a new API object where we've substitued port
   * 9090 for port 8080 (which is where the API is listening).
   */
  var api = new DFFMLHTTPAPI(window.location.origin.replace(window.location.port, '8080'));

  console.log("Created api", api);

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
      "arg": null,
      "config": {
        "filename": {
          "arg": [
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
      "arg": null,
      "config": {
        "filename": {
          "arg": [
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

  // Create an array of all the repos for fun
  var repos = await training_sctx.repos(100);
  console.log("Training repos", repos);

  var repos_array = [];
  for (var key of Object.keys(repos)) {
    repos_array.push(repos[key]);
  }
  console.log("Array of training repos", repos_array);

  // Create a model
  var model = api.model();
  console.log("Created model", model);

  await model.configure("scikitlr", "mymodel", {
    "model": {
      "arg": null,
      "config": {
        "predict": {
          "arg": [
            "Salary"
          ],
          "config": {}
        }
      }
    }
  });

  console.log("Configured model", model);

  var mctx = await model.context("mymodel_context", {
    "Years": {
      // "name": "Years",
      "dtype": "int",
      "length": 1
    },
    "Expertise": {
      "name": "Expertise",
      "dtype": "int",
      "length": 1
    },
    "Trust": {
      "name": "Trust",
      "dtype": "float",
      "length": 1
    }
  });
  console.log("Created model context", mctx);

  await mctx.train([training_sctx]);
  console.log("Trained model context", mctx);

  var accuracy = await mctx.accuracy([test_sctx]);
  console.log("Model context accuracy", accuracy);

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

  if (prediction.mish_the_smish.prediction.value !== 70) {
    console.error(prediction)
    throw new Error("prediction.mish_the_smish.prediction.value was not 70!");
  }

  console.log("Success!");
}

runit();
