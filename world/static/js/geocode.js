const geoCodeUrl = 'https://api.opencagedata.com/geocode/v1/json?q=';
let profileLocale = document.getElementById('profileLocale');
let profileCity = document.getElementById('profileCity');
let profileCountry = document.getElementById('profileCountry')

getLocation();

function getLocation() {
    navigator.geolocation.getCurrentPosition(
        function(pos){
            pingOpenCage(pos);
        },
        function(err){
        },
        {
            enableHighAccuracy: true,
            timeout: 30000
        }
    )
}

function pingOpenCage(pos) {
    let locString = pos.coords.latitude + ',' + pos.coords.longitude;
    let key = '&key=a772e63f0d244c28a26fec647612e5fb';
    let url = geoCodeUrl + locString + key;
    fetch(url, {
        method: 'GET',
        headers: {},
    }).then(response => {
        if (!response.ok) {
            throw Error(response.statusText);
        } else {
            return response.json();
        }
    }).then(json => {
        profileLocale.innerHTML = JSON.stringify(json.results[0].components.locality).slice(1, -1);
        profileCity.innerHTML = JSON.stringify(json.results[0].components.city).slice(1, -1);
        profileCountry.innerHTML = JSON.stringify(json.results[0].components.country).slice(1, -1);
    }).catch(error => {
        alert(error);
    })
}

function getCookie(cookieType) {
    let cookieRetrieved = null;

    //if there is no cookie return null
    if(document.cookie === null || document.cookie === ''){
        return null;
    } else {
        //split document.cookie into an array of individual cookies and loop through
        var cookieArray = document.cookie.split(';');
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


