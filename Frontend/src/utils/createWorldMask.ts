export function createWorldMask(israelCoords: number[][][]) {
  const world: number[][] = [
    [-180, -90],
    [-180, 90],
    [180, 90],
    [180, -90]
  ]

  return {
    type: "Feature",
    geometry: {
      type: "Polygon",
      coordinates: [
        world,
        israelCoords[0]
      ]
    }
  }
}
