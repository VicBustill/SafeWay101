import streamlit.components.v1 as components

def render_map(api_key: str, start_address: str, destination_address: str):
    # Escape double quotes to avoid breaking the JS string literals
    start_js = (start_address or "").replace('"', '\\"')
    dest_js = (destination_address or "").replace('"', '\\"')

    html = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          #map {{
            height: 800px;
            width: 100%;
          }}
        </style>
      </head>
      <body>
        <div id="map"></div>

        <script>
          let map;

          function isLatLng(s) {{
            // very simple check: "number,number"
            return /^\\s*-?\\d+(\\.\\d+)?\\s*,\\s*-?\\d+(\\.\\d+)?\\s*$/.test(s);
          }}

          function parseLatLng(s) {{
            const parts = s.split(",").map(x => parseFloat(x.trim()));
            return {{ lat: parts[0], lng: parts[1] }};
          }}

          function initMap() {{
            const start = "{start_js}";
            const dest = "{dest_js}";

            const geocoder = new google.maps.Geocoder();
            const directionsService = new google.maps.DirectionsService();
            const directionsRenderer = new google.maps.DirectionsRenderer();

            map = new google.maps.Map(document.getElementById("map"), {{
              zoom: 13,
              center: {{ lat: 34.0522, lng: -118.2437 }} // fallback
            }});

            directionsRenderer.setMap(map);

            function showStartMarkerAndMaybeRoute(originForDirections) {{
              // If we have a destination, draw a route
              if (dest && dest.trim().length > 0) {{
                directionsService.route(
                  {{
                    origin: originForDirections,
                    destination: dest,
                    travelMode: google.maps.TravelMode.DRIVING
                  }},
                  (response, status) => {{
                    if (status === "OK") {{
                      directionsRenderer.setDirections(response);
                    }} else {{
                      console.log("Directions failed:", status);
                    }}
                  }}
                );
              }}
            }}

            // If start is "lat,lng", center immediately
            if (start && isLatLng(start)) {{
              const startLatLng = parseLatLng(start);
              map.setCenter(startLatLng);
              new google.maps.Marker({{
                map,
                position: startLatLng,
                title: "Start"
              }});
              showStartMarkerAndMaybeRoute(startLatLng);
              return;
            }}

            // Otherwise, geocode the start address
            if (start && start.trim().length > 0) {{
              geocoder.geocode({{ address: start }}, (results, status) => {{
                if (status === "OK" && results && results[0]) {{
                  const loc = results[0].geometry.location;
                  map.setCenter(loc);
                  new google.maps.Marker({{
                    map,
                    position: loc,
                    title: "Start"
                  }});
                  showStartMarkerAndMaybeRoute(start);
                }} else {{
                  console.log("Geocode failed:", status);
                }}
              }});
            }}
          }}
        </script>

        <script async
          src="https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap">
        </script>
      </body>
    </html>
    """

    components.html(html, height=820)