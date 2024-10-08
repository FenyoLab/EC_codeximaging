import pandas as pd
import geojson

def geojson_to_csv(geojson_file, csv_file):
    """
    Convert a GeoJSON file to a CSV file.

    Args:
        geojson_file (str): Path to the input GeoJSON file.
        csv_file (str): Path to save the output CSV file.
    """
    # Load the GeoJSON file
    with open(geojson_file, 'r') as f:
        data = geojson.load(f)

    # Extract features from the GeoJSON
    features = data['features']

    # Prepare lists to store data for the DataFrame
    roi_id = []
    name = []
    shape = []
    coords = []

    # Function to convert list of tuples into string format
    def format_points(coordinates):
        return ' '.join([f"{lon},{lat}" for lon, lat in coordinates])

    # Loop through features and extract properties and geometry
    for feature in features:
        properties = feature['properties']
        geometry = feature['geometry']
        
        # Extract data
        roi_id.append(properties['Id'])
        name.append(properties['Name'])
        shape.append(properties['Shape'])
        
        # Extract and format coordinates (assuming Polygon)
        coordinates = geometry['coordinates'][0]  # First ring of the polygon
        point_str = format_points(coordinates)
        coords.append(point_str)

    # Create DataFrame from extracted data
    df = pd.DataFrame({
        'Id': roi_id,
        'Text': name,
        'type': shape,
        'all_points': coords
    })

    # Save DataFrame to CSV
    df.to_csv(csv_file, index=False)

    print(f"CSV saved to {csv_file}")

# Path to the GeoJSON file
#geojson_file = '/media/ssd02/as18894/registration/data/annotations/20231012-9784-6H_Scan1/6H_qptiff_rois.geojson'
#csv_file = '/media/ssd02/as18894/registration/data/annotations/20231012-9784-6H_Scan1/6H_qptiff_rois.csv'
#geojson_to_csv(geojson_file, csv_file)
