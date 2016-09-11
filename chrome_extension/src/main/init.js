console.log("Subreddit finder running");

(function() {
  var toggle = function() {
    showingAll = !showingAll;
    pageToggle.textContent = showingAll ? "Hide Post Lists" : "Show Post Lists";

    let tables = document.querySelectorAll(".greentable");
    for (var i = 0; i < tables.length; i++) {
      tables[i].style.display = showingAll ? "block" : "none";
    }
  }

  let pageToggle = document.createElement("a");
  pageToggle.style.cursor = "pointer";
  let li = document.createElement("li");
  li.appendChild(pageToggle);
  pageToggle.onclick = toggle;
  pageToggle.textContent = showingAll ? "Hide Post Lists" : "Show Post Lists";
  let pageTabs = document.querySelector(".tabmenu");
  if (pageTabs == null) {
    return;
  }
  pageTabs.appendChild(li);
}());