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
  async records (chunk_size) {
    // TODO https://www.codementor.io/tiagolopesferreira/asynchronous-iterators-in-javascript-jl1yg8la1
    var response = await this.api.request("/source/" + this.label + "/records/" + chunk_size);

    response = await response.json();

    return response.records;
  }

  async update (record) {
    // https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
    var response = await this.api.request("/source/" + this.label + "/update/" + record.key, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      mode: 'cors', // no-cors, cors, *same-origin
      cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      credentials: 'omit', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'follow', // manual, *follow, error
      referrer: 'no-referrer', // no-referrer, *client
      body: JSON.stringify(record), // body data type must match "Content-Type" header
    });

    await response.json();
  }
}

class DFFMLHTTPAPIModelContext extends DFFMLHTTPAPIObjectContext {
  async train (sources) {
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

    return response.records;
  }

  async accuracy (sources) {
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

    return response.records;
  }

  async predict (records) {
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
      body: JSON.stringify(records),
    });

    response = await response.json();

    return response.records;
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

  async configure (plugin, label, config) {
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

  async context (ctx_label) {
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
}

class DFFMLHTTPAPI {
  constructor(endpoint) {
    this.endpoint = endpoint;
  }

  async request (path, options) {
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
  async upload (path, file) {
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