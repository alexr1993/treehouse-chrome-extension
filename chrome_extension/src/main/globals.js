let SERVICE = "http://localhost:8080/search"; //"
let INTERNAL_POST_REGEX = /https?:\/\/((www|np)\.)?reddit\.com\/r\//;
let MAX_ROWS = 5;
let FONT_COLOUR = "rgb(0, 204, 102)";
var GUID = "temp";

var fetchedPosts = {};
var isRequestInFlight = false;
var showingAll = true;
let lazyLoadGuid = function() {
    chrome.storage.sync.get("guid", (items) => {
        console.log(items);
        if (items.guid !== undefined) {
            GUID = items.guid;
            init();
            return;
        }    

        let random = function() {
            return Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);
        }

        let newGuid = random();
        chrome.storage.sync.set({guid: newGuid}, () => {
            GUID = newGuid;
            init();
            return;
        });
    });
};

lazyLoadGuid();