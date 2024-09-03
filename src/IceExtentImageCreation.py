# This file will download a grib2 file, 
# convert it so it can be used to generate 
# a polar stereographic image and then 
# generate that image before passing it back 
# to the application

import requests
import shutil
import pytz
import time
import zipfile
import os
import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime
from pyproj import CRS
from io import BytesIO
from PIL import Image, ImageTk


from IceExtentGUI import Application

class AppImageCreation(Application):
    def __init__(self):
        Application.__init__(self)

    def download_store_image(self, year, yday):
        # Download the zip file with the shape files, 
        # unzip and store the shape files,
        # return shapefile path

        # We need the year/yday to generate the date string for the images
        dt = datetime.strptime(f"{year} {yday}", "%Y %j").replace(tzinfo=pytz.utc)
        dtstring = dt.strftime("%m%d%Y")

        url = f"https://usicecenter.gov/File/DownloadArchive?prd=2{dtstring}"
        response = requests.get(url, stream=True)

        # Path to the zip file
        zip_file_path = f"nic_autoc{year}{yday}n_pl_a.zip"
        extracted_folder_path = './nic_miz_extracted/'

        # Save stream to zip file
        with open(zip_file_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        # Create a directory to extract files to
        os.makedirs(extracted_folder_path, exist_ok=True)

        # Extract the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_folder_path)

        return os.path.join(extracted_folder_path, zip_file_path.replace('.zip','.shp'))

    def create_image(self, shapefile_path):
        # Create the image from the shapefile,
        # Convert it into a BytesIO object, 
        # Then convert into a tkinter.Canvas image

        if shapefile_path:
            # Load the shapefile using GeoPandas
            gdf = gpd.read_file(shapefile_path)

            # Define the Polar Stereographic projection
            crs_polar = CRS.from_proj4("+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")

            # Reproject the GeoDataFrame to the polar stereographic projection
            gdf = gdf.to_crs(crs_polar)

            # Plot the data into a BytesIO object
            fig, ax = plt.subplots(figsize=(10, 10))
            gdf.plot(ax=ax, edgecolor='black', facecolor='lightblue')
            ax.set_title('Polar Stereographic Projection')

            # Save the plot to a BytesIO object
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close(fig)  # Close the figure to avoid displaying it

            # Use PIL to open the image from the BytesIO object
            buf.seek(0)
            img = Image.open(buf)

            # Convert the image to a format Tkinter can use
            img_tk = ImageTk.PhotoImage(img)

            return img_tk


    def get_image(self, year=time.gmtime().tm_year, yday=time.gmtime().tm_yday-1):
        # overrides Application.get_image

        # Download the zip file with the shape files
        shapefile_path = self.download_store_image(year, yday)

        # Create a tkinter.Canvas image that can be used in the app
        pyimg = self.create_image(shapefile_path=shapefile_path)

        # Return the canvas image
        return pyimg





if __name__ == "__main__":
    app = AppImageCreation()
