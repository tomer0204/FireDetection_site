import israelGeoJson from "../assets/israel.geo.json"
import palestineGeoJson from "../assets/palestine.geo.json"

export function buildCoverageGeoJSON() {
  const polygons: number[][][][] = []

  israelGeoJson.features.forEach((f: any) => {
    if (f.geometry.type === "Polygon") {
      polygons.push(f.geometry.coordinates)
    }
    if (f.geometry.type === "MultiPolygon") {
      polygons.push(...f.geometry.coordinates)
    }
  })

  palestineGeoJson.features.forEach((f: any) => {
    if (f.geometry.type === "Polygon") {
      polygons.push(f.geometry.coordinates)
    }
    if (f.geometry.type === "MultiPolygon") {
      polygons.push(...f.geometry.coordinates)
    }
  })

  return {
    type: "Feature",
    geometry: {
      type: "MultiPolygon",
      coordinates: polygons
    }
  }
}
