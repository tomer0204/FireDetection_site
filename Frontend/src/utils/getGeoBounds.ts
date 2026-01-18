import L from "leaflet"

export function getGeoBounds(geo: any) {
  const layer = L.geoJSON(geo)
  return layer.getBounds()
}
