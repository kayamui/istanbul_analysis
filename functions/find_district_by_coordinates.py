# ANOTHER WAY TO FIND BY LAT AND LON
import json

import geopandas as gpd
from shapely.geometry import Point

def print_lonLat_columns(df):
    """Prints columns containing the substring 'enlem' (case-insensitive)."""

    for col in df.columns:
        if ('enlem' in col.lower()) | ('boylam' in col.lower()) | (col.lower() == 'lat') | (col.lower() == 'lon'):
            print(col)


def get_district_neighbourhood(df):
  # Load districts
  with open("C:/Users/mkaya/Onedrive/Masaüstü/istanbul112_hidden/data/locations/istanbul-districts.json", "r", encoding="utf-8") as f:
      districts_data = json.load(f)
      districts_gdf = gpd.GeoDataFrame.from_features(districts_data["features"])
  print_lonLat_columns(df)
  lat = str(input('latitude column: '))
  lon = str(input('longitude column: '))

  columns= [col for col in df.columns] + ['Neighbourhood', 'District']
  # Load neighborhoods
  neighbourhoods_gdf = gpd.read_file("C:/Users/mkaya/Onedrive/Masaüstü/istanbul112_hidden/data/locations/istanbul_neighbourhoods.geojson")

  # Convert Vakanın Enlemi and Vakanın Boylamı to geometry points
  df["geometry"] = df.apply(lambda row: Point(row[lon], row[lat]), axis=1)
  points_gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

  # Spatial join to find districts
  points_gdf = gpd.sjoin(points_gdf, districts_gdf, how="left", predicate="within")
  points_gdf.rename(columns={"name": "District"}, inplace=True)

  # Drop 'index_right' before the second spatial join
  if 'index_right' in points_gdf.columns:
      points_gdf = points_gdf.drop(columns=['index_right'])

  # Spatial join to find neighborhoods
  points_gdf = gpd.sjoin(points_gdf, neighbourhoods_gdf, how="left", predicate="within")
  points_gdf.rename(columns={"name": "Neighbourhood"}, inplace=True)

  # Select relevant columns and save
  return points_gdf[columns]
