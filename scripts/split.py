import json
import functions
import os
import sys

TEMP_GEOJSON = "temp.geojson"
TOPLEVEL_KEY = "data"

def normalize_date(date):
  date = date.replace("-", ".")
  if len(date) == len("D.MM.YYYY"):
    # Single day digit
    date = date.zfill(len("DD.MM.YYYY"))
  # Reverse DD.MM.YYYY into YYYY.MM.DD so that alphabetical order is the
  # same as chronological.
  date_parts = date.split(".")
  if len(date_parts[0]) != 4:
    date_parts.reverse()
  return ".".join(date_parts)

def split_by_day(data, out_dir):
  # A dictionary from each date to a list of corresponding features
  daily_splits = {}
  if "features" in data:
    for feature in data["features"]:
      if "properties" in feature and "date" in feature["properties"]:
        date = normalize_date(feature["properties"]["date"])
        if date in daily_splits:
          daily_splits[date].append(feature)
        else:
          daily_splits[date] = [feature]
  else:
    print("I was expecting to find a '" + TOPLEVEL_KEY + "' key in the data")

  for date in daily_splits:
    daily_slice_file_path = os.path.join(out_dir, date + ".json")
    if os.path.exists(daily_slice_file_path):
      print("I will not clobber '" + daily_slice_file_path + "', "
            "please delete it first")
      continue
    with open(os.path.join(out_dir, date + ".json"), "w") as f:
      f.write(json.dumps(daily_splits[date]))
      f.close()

def convert_to_geojson(file_path):
  functions.animation_formating_geo(file_path, TEMP_GEOJSON, 'day')

def split_full_data_to_daily_slices(full_data_file_path, out_dir):
  # TODO: Support passinng data directly instead of writing to and
  # re-reading from disk.
  print("Converting to 'geojson' format...")
  convert_to_geojson(full_data_file_path)
  print("Splitting...")
  with open(TEMP_GEOJSON) as f:
    split_by_day(json.loads(f.read()), out_dir)
    f.close()
  os.remove(TEMP_GEOJSON)

def main():
  if sys.version_info[0] < 3:
    print("Sorry but I need Python 3 to work")
    return
  if len(sys.argv) < 2:
    print("I need the path of the file to parse as an argument")
    return

  split_full_data_to_daily_slices(sys.argv[1], ".")

if __name__ == '__main__':
    main()
