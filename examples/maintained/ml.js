function predict (URL) {
  return fetch('cgi-bin/api.py?action=predict&URL=' + URL)
    .then(function(response) {
      return response.json()
    });
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