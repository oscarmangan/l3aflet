let HOST = location.protocol + "//" + location.host;
let locationMarker;
let circle;

//Lufthansa API requires a token to make queries, which we will store
//when the page is loaded
let token = '';
let airport_coords = [2];

//defining variables for HTML elements
const inputField = document.getElementById('searchIata');
const searchBtn = document.getElementById('buttonIata');
const nearestBtn = document.getElementById('closestAirport');
const aName = document.getElementById('airportName');
const aCode = document.getElementById('airportCode');
const aCountry = document.getElementById('airportCountry');
const map = document.getElementById('map');
let arrData = document.getElementById('arrData');
let depData = document.getElementById('depData');

//If no token exists in session storage, get one from the Lufthansa API
//If the token does exist, set the variable 'token' to it, and proceed
//Session storage persists as long as the tab or browser is open
function init_page(map, options) {
    if(!sessionStorage.getItem('token')){
        getToken(map);
    } else {
        token = sessionStorage.getItem('token')
        map_init_basic(map, options)
    }
}

//Callback when map is setup, set the standard view to Dublin.
//Then call updateLocation to update users location and go to nearest airport
//If search button is clicked, go to that airport
function map_init_basic(map, options) {
    map.setView([53.35, -6.3], 10);
    let pos;
    updateLocation(map);

    //Event listener for search button, passing the map, token and search input
    searchBtn.addEventListener('click', function() {
        let searchValue = inputField.value;
        if(searchValue.length !== 3){
            alert('IATA code must be 3 characters');
        } else {
            getAirport(map, token, searchValue)
        }
    });

    //Event listener to return to the users closest/home airport
    nearestBtn.addEventListener('click', function() {
        getAirport(map, token, null)
    });
}

//Get the users current location
function updateLocation(map) {
    navigator.geolocation.getCurrentPosition(
        function(pos) {
            updateUserCoords(pos);
            console.log(pos);
            getAirport(map, token, null);
        },
        function(err){
        },
        {
            enableHighAccuracy: true,
            timeout: 30000
        }
    );
}

//Set the map view to the desired airport
function setMapToAirport(map, airport) {
    console.log("Setting map to airport");
    let airLatLon = L.latLng(airport[0], airport[1]);
    map.flyTo(airLatLon, 14);
    if (locationMarker) {
        map.removeLayer(locationMarker);
    }
    locationMarker = L.marker(airLatLon).addTo(map);
}

//Update the users profile on the database
function updateUserCoords(pos) {
    let locString = pos.coords.latitude + ", " + pos.coords.longitude;
    $.ajax({
        type: "POST",
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        url: HOST + "/updatedb/",
        data: {
            point: locString
        }
    }).done(function (data, status, xhr) {
        console.log("User location updated:" + data["message"]);
    }).fail(function (xhr, status, error) {
        console.log(error);
    }).always(function () {
        console.log("Update DB finished");
    })
}

//Update the users nearest airport on their profile (on DB)
function updateUserNearestAirport(airName, airCode, airCountry) {
    let airCoordsStr = airport_coords[0].toString() + ', ' + airport_coords[1].toString()
    $.ajax({
        type: "POST",
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        url: HOST + "/update-db-airport/",
        data: {
            coords: airCoordsStr,
            airportName: airName,
            airportCode: airCode,
            airportCountry: airCountry
        }
    }).done(function (data, status, xhr){
        console.log("User Profile (nearest airport) updated");
    }).fail(function (xhr, status, error){
        console.log(error);
    }).always(function (){
        console.log("Finished updateUserNearestAirport()");
    })
}

//function to retrieve the cookie from our browser
function getCookie(cookieType) {
    let cookieRetrieved = null;

    //if there is no cookie return null
    if(document.cookie === null || document.cookie === ''){
        return null;
    } else {
        //split document.cookie into an array of individual cookies and loop through
        let cookieArray = document.cookie.split(';');
        for(let i = 0; i < cookieArray.length; i++){
            let thisCookie = jQuery.trim(cookieArray[i]);

            //if thisCookie starts with 'cookieType=' (csrftoken=) then cookieRetrieved
            //is a new string of everything after '=' which is our token, decode and return it
            if(thisCookie.startsWith(cookieType + '=')) {
                cookieRetrieved = decodeURIComponent(thisCookie.substring(10));
                break;
            }
        }
    }
    return cookieRetrieved;
}

//Retrieve the Lufthansa API OAuth token, through views.py
function getToken(map) {
    $.ajax({
        type: "POST",
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        url: HOST + "/luft-auth/",
    }).done(function (data, status, xhr) {
        //set the token in storage, and set the variable, then call map init
        sessionStorage.setItem('token', JSON.stringify(data.access_token));
        token = sessionStorage.getItem('token');
        map_init_basic(map, null);
        console.log(status);
    }).fail(function (xhr, status, error) {
        console.log(error);
    }).always(function () {
        console.log("getToken finished");
    })
}

/*
    This function queries the Lufthansa API. If the airport code is null, no
    specific airport is sought after, so request the nearest airport view.
    If there is a code passed in, search for that airport on the API.
 */
function getAirport(map, token, airportCode) {

    if(airportCode === null) {
        //airportCode is null, therefore get the nearest airport
        $.ajax({
            type: "POST",
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            url: HOST + "/nearby-airport/",
            data: {
                auth: token,
            }
        }).done(function (data, status){

            //set the coordinates to each index in the array
            airport_coords[0] = data["lat"];
            airport_coords[1] = data["lon"];
            airportCode = data["code"];

            //set airportInfo div and get the departures and arrivals
            setInfo(data["name"], data["code"], data["country"]);
            updateUserNearestAirport(data["name"], data["code"], data["country"])
            getDepartures(airportCode);
            getArrivals(airportCode);

            //flyTo() nearby airport on the map
            setMapToAirport(map, airport_coords);
            console.log("Near airport found: " + data["name"]);

        }).fail(function (xhr, status, error) {
            alert(error + ": No nearby airport found");
            console.log(error);
        }).always(function () {
            console.log("Airport search finished");
        })
    } else {
        //airportCode has been passed to function, request that airport
        $.ajax({
            type: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            url: HOST + "/search-airport/",
            data: {
                auth: token,
                iata: airportCode
            }
        }).done(function (data, status){

            //place coordinates into the array
            airport_coords[0] = data["lat"];
            airport_coords[1] = data["lon"];
            airportCode = data["code"];

            //set airportInfo div and get the departures and arrivals
            setInfo(data["name"], data["code"], data["country"]);
            getDepartures(airportCode);
            getArrivals(airportCode);

            //flyTo() the coordinates of the airport on the map
            setMapToAirport(map, airport_coords);

            console.log("Search airport: " + status);
        }).fail(function (xhr, status, error) {
            alert(status + ": No airport was found");
            console.log(error);
        }).always(function () {
            console.log('Airport search finished');
        })
    }
}

/*
    Function to retrieve the departures from the current airport
 */
function getDepartures(iata) {
    refreshTable(depData);
    $.ajax({
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        url: HOST + "/get-departures/",
        data: {
            auth: token,
            iata: iata
        }
    }).done(function (data, status, xhr) {
        setDepartures(data);
    }).fail(function (xhr, status, error) {
        displayNoDataDiv("dep");
        console.log(error);
    }).always(function () {
        console.log('getDepartures finished');
    })
}

/*
    Function to retrieve the arrivals into the current airport
 */
function getArrivals(iata) {
    refreshTable(arrData);
    $.ajax({
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        url: HOST + "/get-arrivals/",
        data: {
            auth: token,
            iata: iata
        }
    }).done(function (data, status, xhr) {
        console.log(data);
        setArrivals(data);
    }).fail(function (xhr, status, error) {
        displayNoDataDiv("arr");
        console.log(error);
    }).always(function () {
        console.log('getArrivals finished');
    })
}

//Set the airport information display on the page
function setInfo(name, code, country) {
    aName.innerHTML = name;
    aCode.innerHTML = code;
    aCountry.innerHTML = country;
}

//Set the table to the new data for departures.
function setDepartures(data) {
    refreshTable(depData);

    //loop through the data retrieved and created a new object
    for (let i in data.Flight) {
        let flightCode = data.Flight[i].OperatingCarrier.AirlineID.concat(data.Flight[i].OperatingCarrier.FlightNumber)
        let newDeparture = {
            flightNum: flightCode,
            origin: data.Flight[i].Arrival.AirportCode,
            time: data.Flight[i].Departure.ScheduledTimeLocal.DateTime.substring(11, ),
            status: data.Flight[i].Departure.TimeStatus.Definition
        }
        //adds a new row to the depData table body with this iteration object
        populateRow(newDeparture, depData);
    }
}

//same functionality as setDepartures
function setArrivals(data) {

    for (let i in data.Flight) {
        let flightCode = data.Flight[i].OperatingCarrier.AirlineID.concat(data.Flight[i].OperatingCarrier.FlightNumber)
        let newArrival = {
            flightNum: flightCode,
            origin: data.Flight[i].Departure.AirportCode,
            time: data.Flight[i].Arrival.ScheduledTimeLocal.DateTime.substring(11, ),
            status: data.Flight[i].Arrival.TimeStatus.Definition
        }
        populateRow(newArrival, arrData);
    }
}

/*
    Function to refresh the table and remove previous entries before rebuilding
 */
function refreshTable(tableBody) {
    tableBody.innerHTML = '';
    document.getElementById('noDepartures').style.display="none";
    document.getElementById('noArrivals').style.display="none";
}

/*
    Function to create a new row in either table with the data of that specific arr/dep
 */
function populateRow(newData, tableBody) {
    let values = [newData.flightNum, newData.origin, newData.time, newData.status];
    let newRow = tableBody.insertRow();
    for(let i = 0; i < 4; i++){
        let newCell = newRow.insertCell(-1);
        newCell.innerHTML = values[i];
    }
}

//if no data has been retrieved (i.e. 404) then display the div to indicate this
function displayNoDataDiv(table) {
    if(table === 'dep'){
        document.getElementById('noDepartures').style.display="block";
    } else if (table === 'arr') {
        document.getElementById('noArrivals').style.display="block";
    }
}

