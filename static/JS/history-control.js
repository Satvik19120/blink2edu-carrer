// window.addEventListener("popstate", function(event) {
//     // Prevent forward navigation after using browser back button
//     history.replaceState(null, null, window.location.href);
// });




// window.addEventListener("popstate", function(event) {
//     history.pushState(null, null, window.location.href);
// });



// window.onpopstate = function () {
//     setTimeout(() => {
//         window.history.forward(); // Forces staying on the current page
//     }, 0);
// };




// window.addEventListener("popstate", function(event) {
//     window.location.replace(window.location.href); // Reloads the current page
// });


// // Optionally, ensure it runs after every navigation event to maintain control
// window.onload = function() {
//     history.replaceState(null, null, window.location.href);
// };



// Prevent forward navigation after back button is used
window.addEventListener("popstate", function(event) {
    history.pushState(null, null, window.location.href);
});

// Ensure users cannot use forward navigation once they go back
window.onpopstate = function () {
    setTimeout(() => {
        window.history.forward(); // Forces staying on the current page
    }, 0);
};

// Refresh page after navigating backward to prevent forward history restoration
window.addEventListener("popstate", function(event) {
    window.location.replace(window.location.href); // Reload the page
});