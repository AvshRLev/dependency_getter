document.addEventListener("DOMContentLoaded", () => {
  document.querySelector("#form").addEventListener("submit", (event) => {
    event.preventDefault();
    packageName = document.querySelector("#name").value;
    packageVersion = document.querySelector("#version").value;
    const title = document.createElement("div");
    title.innerHTML = `${packageName}: ${packageVersion}`;
    let queryPackage = `${packageName}/${packageVersion}`;
    document.querySelector("#main").append(title);
    const firstList = document.querySelector("#list");
    createChildDependeciesListItems(queryPackage, "list");
  });
});

function createChildDependeciesListItems(queryPackage, parentID) {
  let parent = document.getElementById(parentID);
  if (parent.children.length > 0) {
    return;
  }
  fetch("http://127.0.0.1:5000/" + queryPackage)
    .then((response) => response.json())
    .then((dependencies) => {
      const depList = document.createElement("ul");
      Object.entries(dependencies["deps"]).forEach((dep) => {
        const li = document.createElement("li");
        console.log(dep);
        li.innerHTML = `${dep[0]}: ${dep[1]}`;
        let package = `${dep[0]}/${dep[1]}`;
        let id = Math.random();
        li.setAttribute("id", `${id}`);
        li.addEventListener("click", function () {
          document.removeEventListener(
            "click",
            createChildDependeciesListItems
          );
          createChildDependeciesListItems(package, id);
        });
        depList.appendChild(li);
      });

      parent.append(depList);
    });
}

// ul = document.getElementById("my-list");
// createChildDependeciesListItems("lala", ul);
