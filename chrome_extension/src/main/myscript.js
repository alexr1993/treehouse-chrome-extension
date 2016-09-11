let fetchSubreddits = function() {
  // Users with RES will have some invisible posts, only those with srTagged class are visible
  var posts = document.querySelectorAll("a.title.srTagged");
  if (posts.length === 0) {
    posts = document.querySelectorAll("a.title");
  }
  var unfetchedPosts = [];
  var unfetchedUrls = [];

  posts.forEach(function (p) {
    let url = p.href;
    if (fetchedPosts[url] === undefined && INTERNAL_POST_REGEX.exec(url) === null) {
      unfetchedPosts.push(p);
      unfetchedUrls.push(p.href);
    }
  });

  if (unfetchedPosts.length === 0) {
    isRequestInFlight = false;
    return;
  }

  console.log("unfetchedPosts" + unfetchedUrls.length);

  $.ajax({
    type: "POST",
    url: SERVICE,
    contentType: "application/json",
    data: JSON.stringify({urls: unfetchedUrls}),
    dataType: "json",
    success: function( submissionData ) {
      unfetchedPosts.forEach(function(p) {
        let subData = submissionData.submissions[p.href];
        if (subData === undefined) {
          return; // Data is not available yet
        }

        fetchedPosts[p] = true;

        if (subData.length < 2) {
          subData = [];
        }
        presentSubmissionData(p.parentElement.parentElement, subData, Math.max(0, subData.length - 1) + " other submissions");
      });
      isRequestInFlight = false;
    },
    error: function(xhr, error) {
      isRequestInFlight = false;
    }
  });
};

var pageUrlFetched = null;
var fetchingPageUrl = false;

let fetchPageUrl = function() {
  let url = window.location.href;

  $.ajax({
    type: "POST",
    url: service,
    contentType: "application/json",
    data: JSON.stringify({urls: [url]}),
    dataType: "json",
    success: function( submissionData ) {
      let subData = submissionData.submissions[url];
      if (subData === undefined) {
        fetchingPageUrl = false;
        return; // Data is not available yet
      }

      presentSubmissionData(document.getElementById("watch-headline-title"), subData, subData.length + " submissions on Reddit");
      pageUrlFetched = window.location.href;
      fetchingPageUrl = false;
    },
    error: function(xhr, error) {
      fetchingPageUrl = false;
    }
  });
}

// Never stop checking because never-ending reddit might be on
let runRequest = function() {
  // TODO check we are on Reddit
  if (!isRequestInFlight) {
    isRequestInFlight = true;
    fetchSubreddits();
  }
  setTimeout(runRequest, 1000);
};

runRequest();

// Never stop checking because youtube doesn't load new pages when you follow a link to another video
let runPageUrlRequest = function() {
  // TODO check we are on a youtube video page
  if (fetchingPageUrl) {
    setTimeout(runPageUrlRequest, 1000);
    return;
  }
  
  if (pageUrlFetched === window.location.href) {
    setTimeout(runPageUrlRequest, 1000);
    return;
  }

  fetchingPageUrl = true;
  fetchPageUrl();      

  setTimeout(runPageUrlRequest, 1000);
};
