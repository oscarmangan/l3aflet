/*  Author: Oscar Mangan                    */
/*  Description: L3aflet Service Worker     */
/*  Creation Date: 23/11/2020               */

//import Google Workbox library
//importScripts('https://storage.googleapis.com/workbox-cdn/releases/5.1.2/workbox-sw.js');

let staticCacheName = "django-pwa-v" + new Date().getTime();
let filesToCache = [
    '/offline/',
    '/accounts/login',
    '/static/css/style.css',
    '/static/images/globe_icon.png',
];

// Cache on install
self.addEventListener("install", event => {
    this.skipWaiting();
    console.log('hello');
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                return cache.addAll(filesToCache);
            })
    )
});

// Clear cache on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => (cacheName.startsWith("django-pwa-")))
                    .filter(cacheName => (cacheName !== staticCacheName))
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});

// Serve from Cache
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
            .catch(() => {
                return caches.match('/offline/');
            })
    )
});
