self.addEventListener("install", () => {
  console.log("install");
});
self.addEventListener("activate", () => {
  console.log("activate");
});
self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (
    request.method !== "GET" ||
    self.location.origin !== new URL(request.url).origin
  ) {
    return;
  }
  const key = request.mode === "navigate" ? "/" : request;
  event.respondWith(networkFirst(request, key));
});

async function networkFirst(request, key) {
  const cache = await caches.open("rigi-v1");
  try {
    const response = await fetch(request);
    await cache.put(key, response.clone());
    return response;
  } catch {
    const cached = await caches.match(key);
    return cached ?? Response.error();
  }
}
