function predict(URL) {
  return fetch('cgi-bin/api-ml.py?action=predict' +
    '&maintained=' + Number(maintained) +
    '&URL=' + URL)
  .then(function(response) {
    return response.json()
  }.bind(this));
}

window.addEventListener('DOMContentLoaded', function(event) {
  var tableDOM = document.getElementById('table');
  var URLDOM = document.getElementById('URL');
  var predictDOM = document.getElementById('predict');

  predictDOM.addEventListener('click', function(event) {
    predict(URLDOM.value)
    .then(function() {
      refreshTable(tableDOM);
    });
  });
});
