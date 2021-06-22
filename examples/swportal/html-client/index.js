class API {
  _getOnlyContext(results) {
    return results[Object.keys(results)[0]];
  }

  async getProject(projectUUID) {
    return this._getOnlyContext(await (await fetch('/projects/' + projectUUID)).json());
  }

  async getProjects() {
    return this._getOnlyContext(this._getOnlyContext(await (await fetch('/projects')).json()));
  }
}


class App {
  constructor(api) {
    this.api = api;
    this.elements = {};
  }

  getElements(root) {
    var elements = {};

    // Create an object to hold references to all elements, keys are element ids.
    for (var element of document.querySelectorAll("[id]")) {
      elements[element.id] = element;
    }

    return elements;
  }

  refreshElements(root) {
    this.elements = this.getElements(root);
  }

  populateDisplayProject(project) {
    // Hide the displaed project if there is no data to display
    if (typeof project === "undefined" || project === null) {
      this.elements.displayProjectContainer.style.display = "none";
      return;
    }

    this.elements.displayProjectContainer.style.display = "block";
    this.elements.displayProjectName.innerText = project.name;
    this.elements.displayProjectStaticAnalysis.innerText = project.staticAnalysis;
    this.elements.displayProjectLegal.innerText = project.legal;
  }

  async refreshDisplayProject(projectUUID) {
    if (typeof projectUUID === "undefined" ||
      projectUUID === null ||
      projectUUID === "")
      this.populateDisplayProject();
    else
      this.populateDisplayProject(await this.api.getProject(projectUUID));
  }

  populateProjectsList(projects) {
    // Clear the list
    this.elements.projectsList.innerHTML = "";
    // Create a list element for each project
    Object.entries(projects).forEach(([uuid, project]) => {
      var listItem = document.createElement("li");
      var listItemLink = document.createElement("a");

      this.elements.projectsList.appendChild(listItem);
      listItem.appendChild(listItemLink);

      listItemLink.innerText = project.name;
      listItemLink.href = "#" + uuid;
      listItemLink.onclick = (() => {
        this.refreshDisplayProject(uuid);
      });
    });
  }

  async refreshProjectsList() {
    this.populateProjectsList(await this.api.getProjects());
  }
}

var app = new App(new API());

window.addEventListener('DOMContentLoaded', async function(event) {
  // DOM loaded, grab all DOM elements we'll be working with
  app.refreshElements(document);

  // Get the list of projects
  app.refreshProjectsList();

  // If there is a project hash, display it
  app.refreshDisplayProject(window.location.hash.replace("#", ""));
});
