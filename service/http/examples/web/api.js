"use strict";

class DFFMLHTTPAPISource {
  constructor(api, label) {
    this.api = api;
    this.label = label;
  }

  async repos(chunk_size) {
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
      credentials: 'same-origin', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'follow', // manual, *follow, error
      referrer: 'no-referrer', // no-referrer, *client
      body: JSON.stringify(repo), // body data type must match "Content-Type" header
    });

    response = await response.json();

    return response.repos;
  }
}

class DFFMLHTTPAPI {
  constructor(endpoint) {
    this.endpoint = endpoint;
  }

  async request(path, options) {
    var url = this.endpoint + path;
    return await fetch(url, options);
  }

  source(label) {
    return new DFFMLHTTPAPISource(this, label);
  }
}

var runit = async function() {
  var api = new DFFMLHTTPAPI(window.location.origin.replace(window.location.port, '8080'));

  console.log(api);

  var source = api.source("mydataset");

  console.log(source);

  var repos = await source.repos(100);

  console.log(repos);

  var repos_array = [];

  for (var key of Object.keys(repos)) {
    repos_array.push(repos[key]);
  }

  console.log(repos_array);
}

runit();
