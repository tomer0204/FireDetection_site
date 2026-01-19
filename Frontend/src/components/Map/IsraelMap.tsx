import { MapContainer, TileLayer, GeoJSON } from "react-leaflet"
import israelGeoJson from "../../assets/israel.geo.json"

const WORLD_POLYGON: GeoJSON.Polygon = {
  type: "Polygon",
  coordinates: [
    [
      [-180, -90],
      [180, -90],
      [180, 90],
      [-180, 90],
      [-180, -90]
    ]
  ]
}

function buildMaskedGeoJSON(israel: any) {
  const holes = israel.features.map((f: any) => f.geometry.coordinates[0])

  return {
    type: "Feature",
    geometry: {
      type: "Polygon",
      coordinates: [
        WORLD_POLYGON.coordinates[0],
        ...holes
      ]
    }
  }
}

export default function IsraelMap() {
  const masked = buildMaskedGeoJSON(israelGeoJson)


    return (
      <MapContainer
  center={[31.0461, 34.8516]}
  zoom={7}
  minZoom={6}
  maxZoom={13}
  zoomSnap={0.5}
  zoomDelta={0.5}
  wheelPxPerZoomLevel={120}
  style={{ height: "100vh", width: "100%" }}
  maxBounds={[
    [29.3, 34.0],
    [33.5, 36.0]
  ]}
  maxBoundsViscosity={1.0}
  zoomAnimation={true}
  zoomAnimationThreshold={4}
  fadeAnimation={true}
  inertia={true}
  inertiaDeceleration={3000}
>

      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <GeoJSON
          // @ts-ignore
        data={masked}
        style={{
           fillColor: "black",
          fillOpacity: 0.6,
          stroke: false
        }}
      />

      <GeoJSON
          // @ts-ignore
        data={israelGeoJson}
        style={{
        fillOpacity: 0,
        color: "#ffffff",
        weight: 1.5,
        dashArray: "4 4"
        }}
      />
    </MapContainer>
  )
}
