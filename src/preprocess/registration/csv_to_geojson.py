import pandas as pd
import geojson

# Load CSV data into a DataFrame
csv_file = '/gpfs/data/proteomics/data/Endometrial_mIF/qptiff_HE/Image/544800/Binary/0413-3D                  _1018924.svs [0]-544800-rois.csv'
df = pd.read_csv(csv_file)

# Function to convert the string of coordinates to a list of tuples
def parse_points(point_str):
    point_pairs = point_str.split(' ')
    coordinates = []
    for pair in point_pairs:
        lon, lat = map(float, pair.split(','))
        coordinates.append((lon, lat))
    return coordinates

# Create GeoJSON features
features = []
for _, row in df.iterrows():
    polygon_points = parse_points(row['all_points'])  # Parse the polygon coordinates
    polygon = geojson.Polygon([polygon_points])       # Create a Polygon geometry
    properties = {
        "Id": row['Id'],
        "Name": row['Text'],
        "Shape": row['type']
    }
    feature = geojson.Feature(geometry=polygon, properties=properties)
    features.append(feature)

# Create a FeatureCollection
feature_collection = geojson.FeatureCollection(features)

# Save to a GeoJSON file
geojson_file = '/gpfs/data/proteomics/data/Endometrial_mIF/qptiff_HE/Image/544800/Binary/0413-3D                  _1018924.svs [0]-544800-rois.geojson'
with open(geojson_file, 'w') as f:
    geojson.dump(feature_collection, f)

print(f"GeoJSON saved to {geojson_file}")

