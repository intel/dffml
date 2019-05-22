function populate_table(tableDOM, URLs) {
  var row;
  var col;
  // Clear the table
  tableDOM.innerHTML = '';
  // Headers
  row = document.createElement('tr');
  tableDOM.appendChild(row)
  // URL
  col = document.createElement('td');
  col.innerText = 'URL';
  row.appendChild(col)
  // Status
  col = document.createElement('td');
  col.innerText = 'Maintained?';
  row.appendChild(col)
  // Create body
  for (var URL in URLs) {
    // Convert from int to string
    if (URLs[URL]) {
      URLs[URL] = 'Yes';
    } else {
      URLs[URL] = 'No';
    }
    row = document.createElement('tr');
    table.appendChild(row);
    // URL
    col = document.createElement('td');
    col.innerText = URL;
    row.appendChild(col)
    // Status
    col = document.createElement('td');
    col.innerText = URLs[URL];
    row.appendChild(col)
  }
}

function refreshTable(tableDOM) {
  return fetch('cgi-bin/api.py?action=dump')
  .then(function(response) {
    return response.json()
  })
  .then(function(URLs) {
    populate_table(tableDOM, URLs);
  });
}

function setMaintenance(URL, maintained) {
  return fetch('cgi-bin/api.py?action=set' +
    '&maintained=' + Number(maintained) +
    '&URL=' + URL)
  .then(function(response) {
    return response.json()
  }.bind(this));
}

window.addEventListener('DOMContentLoaded', function(event) {
  var tableDOM = document.getElementById('table');
  var URLDOM = document.getElementById('URL');
  var maintainedDOM = document.getElementById('maintained');
  var unmaintainedDOM = document.getElementById('unmaintained');

  maintainedDOM.addEventListener('click', function(event) {
    setMaintenance(URLDOM.value, true)
    .then(function() {
      refreshTable(tableDOM);
    });
  });

  unmaintainedDOM.addEventListener('click', function(event) {
    setMaintenance(URLDOM.value, false)
    .then(function() {
      refreshTable(tableDOM);
    });
  });

  refreshTable(tableDOM);
});
