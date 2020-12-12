# l3aflet
Welcome to l3aflet, a flight information progressive web application using Django, JavaScript and Docker

## App functionality
The app is used to provide users the location of their nearest airport. Using their device coordinates, the application requests 
the Lufthansa API, which returns the nearest airport. The Leaflet/OpenStreetMap functionality flies to this airport. Along with location,
all arrivals and departures (mostly of Lufthansa operation) are displayed (Flight number, Destination, Departure Time (local) and status).

Along with flight information, the application also utilises the OpenCage API which reverse geocodes the users coordinates into a
readable address. This address is in the format of road, locale, city, county and country.

## How to access
The application can be found on https://www.l3aflet.xyz

Users can signup, providing an email, username and password. Upon then logging in, the app automatically determines the users location, 
nearest airport and relevant flight information.

The user can also go to their profile, where they will be shown their details, such as location address, nearest airport details, 
username and email address. Users also have the option to change their password if wanted.

### Deployment
The application is deployed using Docker, Nginx and AWS. The separate packages of software are containerised into the database, database
management panel, nginx and the actual Django/JS project itself. This network of containers are located on an Amazon EC2 instance running
on Amazon Linux AMI.

#### To note
The codebase includes some REST API setup code. I initially attempted to separate the application and presentation layers into a React
and Django tier architecture. Unfortunately CORS issues took center stage and the time to implement and fix proved too large for the deadline. 
You can find the attempts to utilise and build a RESTful API in the codebase.
