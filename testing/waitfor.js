/**
 * This file from the phantomjs repository's examples dir.
 *
 * Wait until the test condition is true or a timeout occurs. Useful for waiting
 * on a server response or for a ui change (fadeIn, etc.) to occur.
 *
 * @param testFx javascript condition that evaluates to a boolean,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param onReady what to do when testFx condition is fulfilled,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param timeOutMillis the max amount of time to wait. If not specified, 3 sec is used.
 */
function waitFor(testFx, onReady, timeOutMillis, whichplant) {
    var maxtimeOutMillis = timeOutMillis ? timeOutMillis : 60000, //< Default Max Timout is 60s
        start = new Date().getTime(),
        condition = false,
        interval = setInterval(function() {
            if ( (new Date().getTime() - start < maxtimeOutMillis) && !condition ) {
                // If not time-out yet and condition not yet fulfilled
                condition = (typeof(testFx) === "string" ? eval(testFx) : testFx()); //< defensive code
            } else {
                if(!condition) {
                    // If condition still not fulfilled (timeout but condition is 'false')
                    console.log("'waitFor()' timeout");
                    phantom.exit(1);
                } else {
                    // Condition fulfilled (timeout and/or condition is 'true')
                    console.log(whichplant + "done at " + Math.round((new Date()).getTime() / 1000));
                    typeof(onReady) === "string" ? eval(onReady) : onReady(); //< Do what it's supposed to do once the condition is fulfilled
                    clearInterval(interval); //< Stop this interval
                }
            }
        }, 250); //< repeat check every 250ms
};


var page = require('webpage').create();
var system = require('system');
var whichplant = system.args[1];

// Open plant page of random plant, and, onPageLoad, do...
page.open("http://169.229.63.33:8888/?plant="+whichplant, function (status) {
    // Check for page load success
    if (status !== "success") {
        console.log("Unable to access network");
    } else {
        // Wait for 'incoming_data' to load
        waitFor(function() {
            // Check in the page if a specific element is now visible
            return page.evaluate(function() {
                return incoming_data.length > 2;
            });
        }, function() {
           console.log("The data came");
           phantom.exit();
        }, 60000, whichplant);        
    }
});
