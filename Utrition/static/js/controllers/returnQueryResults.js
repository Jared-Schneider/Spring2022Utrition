/*
    Search is attached to the foodType search bar. The event is fired on every keyup (every character pressed).
    It waits for 250 milliseconds after the final character typed, and then begins the ElasticSearch query process by
    calling returnQueryResults().
 */
function search () {
    setTimeout(returnQueryResults, 250);
}

/*
What the code below does is this:
  1) Contact the /es-food-lookup route on the web server, and give it whatever food the user entered
       ie. give it the users "food search string", which is just food field from the front-end
  2) So a POST request is fired at the /es-food-lookup route on our webserver, and inside that request is some JSON
     containing the food search string
  3) Then the back-end contacts our Elasticsearch stuff to find the food that best matches whatever the user entered
  4) And finally, the best-matching-food is returned to us here on the front-end (in some JSON)
  5) So then we update the food results div with the top 5 results

  ** Only queries backend when the search string is greater than 3 characters
*/
function returnQueryResults() {
    const foodEntered = document.querySelector("#foodType").value;
    // const noresults = document.getElementById("noresults")
    // const loading = document.getElementById("loading")

    // if we actually have something to search with...
    if (foodEntered !== "" && foodEntered.length > 3) {
        // noresults.style.display = "none";
        // loading.style.display = "block";

        const dataToSend = {"search_str": foodEntered};

        const xhr = new XMLHttpRequest();  // use the XHR API to fire off an HTTP Request (specifically a POST here) to the server
        xhr.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                // we will enter here when the response comes back from the web server
                const response = JSON.parse(this.responseText);

                // if back-end returned us an empty JSON object, no food was found that matched our search string
                let matchWasFound = (this.responseText.trim() !== "{}");

                if (matchWasFound) {
                    // loading.style.display = "block";

                    const results = response["foods"];
                    // With the units received from the server, go ahead and update the page :)

                    const foodResultsDiv = document.getElementById("foodResultsDiv");
                    foodResultsDiv.innerHTML = '';
                    for (let result of results) {
                        foodResultsDiv.innerHTML += `<div class="results"><button class="results" id="${result["id"]}" onclick="autocompleteUnits(this.id)">${result["food_desc"]}</button></div>`;
                    }

                } else {
                    // noresults.style.display = "block";
                }
                // loading.style.display = "none";
            }
        }
        xhr.open("POST", "/es-food-lookup", true);  // true => make the call asynchronously, which is a best practice
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify(dataToSend));

    } else if (foodEntered === "") {
        const foodResultsDiv = document.getElementById("foodResultsDiv");
        foodResultsDiv.innerHTML = "";

    }
}

/*
    Three things happening here (in order):
    1) Set the foodType input form value to match (exactly) the selected food
    2) Clear the results that were displayed in the foodResultsDiv because a selection has been made
    3) Update the Units Selection with the options for the selected food (retrieved from ElasticSearch based on
       foodID)
 */
function autocompleteUnits(id) {
    // Get the div containing the food results
    const foodResultsDiv = document.getElementById("foodResultsDiv");

    // Get the exact name of the selected food
    const selectedFood = document.getElementById(id).innerText;

    // Set the foodType input to match the selected food
    document.getElementById("foodType").value = selectedFood;

    // Clear the div containing the food results
    foodResultsDiv.innerHTML = '';
    document.getElementById("DB_food_id").value = id

    const dataToSend = {"search_str": id};

    const xhr = new XMLHttpRequest();  // use the XHR API to fire off an HTTP Request (specifically a POST here) to the server
    xhr.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            // we will enter here when the response comes back from the web server
            const response = JSON.parse(this.responseText);

            // if back-end returned us an empty JSON object, no food was found that matched our search string
            let matchWasFound = (this.responseText.trim() !== "{}");

            if (matchWasFound) {
                // loading.style.visibility = "visible";
                // Retrieve the returned units for the selected food
                const units = response["units"];

                // Present the units options to the user
                const unitsSelect = document.getElementById("unitSelect");
                unitsSelect.innerHTML = "";
                for (let unit of units){
                    unitsSelect.innerHTML += `<option>${unit["food_unit_desc"]}</option>`;
                }
            }
        }
    }
    xhr.open("POST", "/es-units-lookup", true);  // true => make the call asynchronously, which is a best practice
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(dataToSend));
}
