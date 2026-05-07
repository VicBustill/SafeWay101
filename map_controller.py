import json
import streamlit.components.v1 as components

#I modded here
def render_map(
    api_key: str,
    start_address: str,
    destination_address: str,
    radius_miles: int,
    use_current_location: bool,
    travel_mode: str,
    crime_markers=None,

):
    # Escape double quotes to avoid breaking the JS string literals
    start_js = (start_address or "").replace('"', '\\"')
    dest_js = (destination_address or "").replace('"', '\\"')
    radius_miles_js = radius_miles
    use_current_location_js = "true" if use_current_location else "false"
    travel_mode_js = (travel_mode or "DRIVING").replace('"', '\\"')

    crime_markers_json = json.dumps(crime_markers or [])
    crime_markers_json = crime_markers_json.replace("</", "<\\/")



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
            const radiusMiles = {radius_miles_js};
            const useCurrentLocation = {use_current_location_js};
            const travelMode = "{travel_mode_js}";
            const crimeMarkers = {crime_markers_json};

            const geocoder = new google.maps.Geocoder();
            const directionsService = new google.maps.DirectionsService();
            const directionsRenderer = new google.maps.DirectionsRenderer();

            map = new google.maps.Map(document.getElementById("map"), {{
              zoom: 13,
              center: {{ lat: 34.0522, lng: -118.2437 }} // fallback
            }});

            directionsRenderer.setMap(map);

            function drawRadiusCircle(centerPoint) {{
              if (radiusMiles > 0) {{
                const radiusMeters = radiusMiles * 1609.34;

                new google.maps.Circle({{
                map,
                center: centerPoint,
                radius: radiusMeters,
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillOpacity: 0.15
                }});
               }}
             }}
            
            const infoWindow = new google.maps.InfoWindow();

            function escapeHtml(value) {{
              if (value === null || value === undefined) {{
                return "";
              }}

              return String(value)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
            }}

            function crimeIconColor(iconCategory) {{
              if (iconCategory === "person-crime") {{
                return "#d93025";
              }}

              if (iconCategory === "property-crime") {{
                return "#f9ab00";
              }}

              if (iconCategory === "society-crime") {{
                return "#1a73e8";
              }}

              if (iconCategory === "high-severity-crime") {{
                return "#7b1fa2";
              }}

              return "#5f6368";
            }}

            function addCrimeMarkers() {{
              crimeMarkers.forEach((crime) => {{
                if (crime.lat === null || crime.lon === null) {{
                  return;
                }}

                const position = {{
                  lat: Number(crime.lat),
                  lng: Number(crime.lon)
                }};

                if (Number.isNaN(position.lat) || Number.isNaN(position.lng)) {{
                  return;
                }}

                const summary = crime.summary || {{}};
                const flags = Array.isArray(summary.flags) && summary.flags.length > 0
                  ? summary.flags.join(", ")
                  : "None listed";

                const content = `
                  <div style="max-width: 280px; font-family: Arial, sans-serif;">
                    <h3 style="margin: 0 0 8px 0;">${{escapeHtml(crime.title)}}</h3>
                    <p><strong>Case:</strong> ${{escapeHtml(crime.case_no)}}</p>
                    <p><strong>Crime Against:</strong> ${{escapeHtml(summary.crime_against)}}</p>
                    <p><strong>Occurred:</strong> ${{escapeHtml(summary.occurred)}}</p>
                    <p><strong>Reported:</strong> ${{escapeHtml(summary.reported)}}</p>
                    <p><strong>Location:</strong> ${{escapeHtml(summary.location)}}</p>
                    <p><strong>Premise:</strong> ${{escapeHtml(summary.premise)}}</p>
                    <p><strong>Status:</strong> ${{escapeHtml(summary.status)}}</p>
                    <p><strong>Flags:</strong> ${{escapeHtml(flags)}}</p>
                    <p><strong>Distance:</strong> ${{escapeHtml(crime.distance_m)}} m</p>
                  </div>
                `;

                const marker = new google.maps.Marker({{
                  map,
                  position,
                  title: crime.title || "Crime record",
                  icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 8,
                    fillColor: crimeIconColor(crime.icon_category),
                    fillOpacity: 0.95,
                    strokeColor: "#ffffff",
                    strokeWeight: 2
                  }}
                }});

                marker.addListener("click", () => {{
                  infoWindow.setContent(content);
                  infoWindow.open(map, marker);
                }});
              }});
            }}

            addCrimeMarkers();


            function showStartMarkerAndMaybeRoute(originForDirections) {{
              // If we have a destination, draw a route
              if (dest && dest.trim().length > 0) {{
                directionsService.route(
                  {{
                    origin: originForDirections,
                    destination: dest,
                    travelMode: google.maps.TravelMode[travelMode]
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

             drawRadiusCircle(startLatLng);

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

               drawRadiusCircle(loc);

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