let SERVICE = "https://jukeboxxy.com/search";
let INTERNAL_POST_REGEX = /https?:\/\/((www|np)\.)?reddit\.com\/r\//;
let MAX_ROWS = 5;
let FONT_COLOUR = "rgb(0, 204, 102)";
var GUID = "temp";

var fetchedPosts = {};
var isRequestInFlight = false;
var showingAll = true;

let loadSettings = function(resolve) {
    chrome.storage.sync.get(["guid", "showingAll"], (items) => {
        console.log(items);

        let showingAll = items.showingAll === undefined ? true : items.showingAll;

        if (items.guid !== undefined) {
            resolve({guid: items.guid, showingAll: showingAll});
        }    

        let random = function() {
            return Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);
        }

        let newGuid = random();
        chrome.storage.sync.set({guid: newGuid}, () => {
            resolve({guid: newGuid, showingAll: showingAll});
        });
    });
};

let settingsPromise = new Promise((resolve, reject) => loadSettings(resolve))
                            .then((settings) => {
                                showingAll = settings.showingAll;
                                GUID = settings.guid;
                                init();
                            });