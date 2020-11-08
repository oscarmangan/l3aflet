var HOST = location.protocol + "//" + location.host;
var locationMarker;
var circle;

var myIcon = L.icon({
    iconUrl: '../static/leaflet/images/marker-icon.png',
    iconSize: [26, 48],
    iconAnchor: [12, 43],
    popupAnchor: [-3, -50],
    shadowUrl: '../static/leaflet/images/marker-shadow.png',
    shadowSize: [48, 75],
    shadowAnchor: [10, 72]
});

function map_init_basic(map, options) {
    map.setView([53.35, -6.3], 10);
    var pos;
    updateLocation(map);
    map.on('touchstart click dblclick ', function() {
        updateLocation(map);
    });
}

function updateLocation(map) {
    navigator.geolocation.getCurrentPosition(
        function(pos) {
            setMapToCurrentLocation(map, pos);
            update_db(pos);
        },
        function(err){
        },
        {
            enableHighAccuracy: true,
            timeout: 30000
        }
    );
}

function setMapToCurrentLocation(map, pos) {
    console.log("In setMapToCurrentLocation");
    var myLatLon = L.latLng(pos.coords.latitude, pos.coords.longitude);
    map.flyTo(myLatLon, 16);
    if (locationMarker) {
        map.removeLayer(locationMarker);
    }
    locationMarker = L.marker(myLatLon,{icon: myIcon}).addTo(map);
    if (circle) {
        map.removeLayer(circle);
    }
    circle = L.circle(myLatLon, {
        color: 'royalblue',
        fillColor: 'royalblue',
        fillOpacity: 0.2,
        radius: pos.coords.accuracy
    }).addTo(map);
    $(".toast-body").html("Found location<br>Lat: " + myLatLon.lat + " Lon: " +
        myLatLon.lng);
    $(".toast").toast('show');
}

function update_db(pos) {
    var locString = pos.coords.longitude + ", " + pos.coords.latitude;
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
        console.log(data["message"]);
        var originalMsg = $(".toast-body").html();
        $(".toast-body").html(originalMsg + "<br/>Updated database<br/>"
        + data["message"]);
    }).fail(function (xhr, status, error) {
        console.log(error);
        var originalMsg = $(".toast-body").html();
        $(".toast-body").html(originalMsg + "<br/>" + error);
    }).always(function () {
        console.log("find_loc_ed finished");
        $(".toast").toast('show');
    })
}

//function to retrieve the cookie from our browser
function getCookie(cookieType) {
    var cookieRetrieved = null;

    //if there is no cookie return null
    if(document.cookie === null || document.cookie === ''){
        return null;
    } else {
        //split document.cookie into an array of individual cookies and loop through
        var cookieArray = document.cookie.split(';');
        for(var i = 0; i < cookieArray.length; i++){
            var thisCookie = jQuery.trim(cookieArray[i]);

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


