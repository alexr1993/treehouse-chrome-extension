let getDateString = function(date) {
  let options = {
      weekday: "long", year: "numeric", month: "short",
      day: "numeric", hour: "2-digit", minute: "2-digit"
  };
  return date.toLocaleTimeString("en-us", options);
};

let createCell = function() {
  let cell = document.createElement("a");
  cell.style.color = FONT_COLOUR;
  return cell;
};

let formatDate = function(date) {
  let now = new Date(Date.now());

  let diffSecs = (now.getTime() - date.getTime()) / 1000;
  if (diffSecs < 60) {
    return Math.floor(diffSecs) + " seconds ago";
  }

  let diffMins = diffSecs/60;
  if (diffMins < 60) {
    return Math.floor(diffMins) + " minutes ago";
  }

  let diffHours = diffMins/60;
  if (diffHours < 24) {
    return Math.floor(diffHours) + " hours ago";
  }

  let diffDays = diffHours/24;
  if (diffDays < 31) {
    return Math.floor(diffDays) + " days ago";
  }

  let diffMonths = diffDays/30;
  if (diffMonths < 12) {
    return Math.floor(diffMonths) + " months ago";
  }

  return getDateString(date);
};

let formatTitle = function(title) {
  if (title === undefined || title === null) {
    return "";
  }

  return title;
}

let compareTo = function(numA, numB) {
  if (numA < numB) return -1;
  if (numB < numA) return 1;
  return 0;
}

let createToggleButton = function(table, tableHeading) {
  let toggleButton = document.createElement("span");
  toggleButton.style.cursor = "pointer";
  table.style.display = showingAll ? "block" : "none";
  table.classList = ["greentable"];

  toggleButton.textContent = tableHeading;
  toggleButton.color = FONT_COLOUR;
  toggleButton.style.paddingTop = "3px";
  toggleButton.style.paddingBottom = "4px";

  toggleButton.onclick = function (e) {
    if (table.style.display === "block") {
      table.style.display = "none";
    } else {
      table.style.display = "block";
    }
  };
  return toggleButton;
};

let createRowToggleButton = function(hideableRows) {
  let button = document.createElement("span");
  let visible = false;

  button.textContent = "(show more)"
  button.style.cursor = "pointer";
  button.style.paddingLeft = "3px";
  button.onclick = function(e) {
    if (visible) {
      hideableRows.forEach(function(r) { r.style.display = "none"});
      visible = false;
      button.textContent = "(show more)"
    } else {
      hideableRows.forEach(function(r) { r.style.display = "table-row"});      
      button.textContent = "(show less)";
      visible = true;
    }
  }

  return button;
};

let presentSubmissionData = function(parentElement, subData, tableHeading) {
  let hiddenRows = {};
  if (subData.length > MAX_ROWS) {
    subData.sort(function(a, b) { return compareTo(a.score, b.score); });
    let defaultHidden = subData.slice(0, subData.length - MAX_ROWS);
    defaultHidden.forEach(function(dH) { hiddenRows[dH.createdUtc] = true; });
  }

  subData.sort(function(a, b) { return compareTo(a.createdUtc, b.createdUtc); }).reverse();
  let table = document.createElement("table");
  table.style.marginTop = "3px";
  let toggleButton = createToggleButton(table, tableHeading);
  let hideableRows = [];

  subData.forEach(function(subDatum) {
    let subreddit = subDatum.subredditName;
    let dateCell = createCell();
    let subredditCell = createCell();
    let scoreCell = createCell();

    let date = new Date(subDatum.createdUtc * 1000);
    dateCell.textContent = formatDate(date);
    dateCell.href = subDatum.permalink;

    subredditCell.textContent = "/r/" + subreddit;
    subredditCell.href = "https://www.reddit.com/r/" + subreddit;

    scoreCell.textContent = subDatum.score;

    let td = function(element) {
      let cell = document.createElement("td");
      cell.appendChild(element);
      cell.style.paddingRight = "10px";
      cell.noWrap = true;
      return cell;
    }

    let row = document.createElement("tr");
    row.appendChild(td(dateCell));
    row.appendChild(td(subredditCell));
    row.appendChild(td(scoreCell));

    if (hiddenRows[subDatum.createdUtc]) {
      hideableRows.push(row);
      row.style.display = "none";
    }
    table.appendChild(row);
  });

  parentElement.appendChild(toggleButton);

  if (subData.length > MAX_ROWS) {
    toggleButton.onclick = undefined;
    toggleButton.style.cursor = "default";
    let rowToggleButton = createRowToggleButton(hideableRows);
    parentElement.appendChild(rowToggleButton);
  }
  parentElement.appendChild(table);
}