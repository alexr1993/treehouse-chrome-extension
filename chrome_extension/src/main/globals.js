let SERVICE = "https://jukeboxxy.com/search"; //"
let INTERNAL_POST_REGEX = /https?:\/\/((www|np)\.)?reddit\.com\/r\//;
let MAX_ROWS = 5;
let FONT_COLOUR = "rgb(0, 204, 102)";

var fetchedPosts = {};
var isRequestInFlight = false;
var showingAll = true;