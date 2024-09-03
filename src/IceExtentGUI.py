import requests
import tkinter as tk
import time
import pytz

from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime, timedelta


class Application():
    def __init__(self):
        self.years = list(reversed(range(1999, time.gmtime().tm_year+1)))

        self.root = tk.Tk()
        self.build_window()

    def build_window(self):
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.nav_frame.grid_rowconfigure(0, weight=1)
        self.nav_frame.grid_columnconfigure(0, weight=1)
        self.nav_frame.grid_columnconfigure(4, weight=1)

        # We need to keep track of the year-day to keep the images in sync
        self.select_day = tk.StringVar(self.root) # Variable to hold day of year for buttons below
        self.select_day.set((datetime.today() - timedelta(days=1)).strftime("%j")) # We are backward looking, starting with the previous day's analysis

        # We need to keep track of the left image year and the right image year internally
        self.left_year = tk.StringVar(self.root)
        self.left_year.set(self.years[0]) # set the left side year to current year

        # Drop down option menu to select the image year we want to view
        self.left_year_menu = tk.OptionMenu(self.nav_frame, self.left_year, *self.years, command=lambda x: self.update_images('left'))
        self.left_year_menu.grid(row=0, column=0)

        # Buttons to increment and decrement the yday, and a text area to display it
        self.decrement_btn = tk.Button(self.nav_frame, text="<", command=lambda: self.decrement())
        self.decrement_btn.grid(row=0, column=1)
        self.yday_lbl = tk.Label(self.nav_frame, text=self.select_day.get(), borderwidth=2, relief='ridge')
        self.yday_lbl.grid(row=0, column=2)
        self.increment_btn = tk.Button(self.nav_frame, text=">", command=lambda: self.increment())
        self.increment_btn.grid(row=0, column=3)

        # We need to keep track of the left image year and the right image year internally
        self.right_year = tk.StringVar(self.root)
        self.right_year.set(self.years[1]) # set the left side year to current year

        # Drop down option menu to select the image year we want to view
        self.right_year_menu = tk.OptionMenu(self.nav_frame, self.right_year, *self.years, command=lambda x: self.update_images('right'))
        self.right_year_menu.grid(row=0, column=4)

        # We want a frame to hold the images themselves
        self.img_frame = tk.Frame(self.root)
        self.img_frame.grid(row=1, column=0)

        # We build the left and right canvases, as well as the maps which hold the actual images
        self.canvas_left = tk.Canvas(self.img_frame, width=900, height=700, bg='white')
        self.canvas_left.grid(row=0, column=0)
        self.map_left = self.canvas_left.create_image(0, 0, image=None, anchor='nw')

        self.canvas_right = tk.Canvas(self.img_frame, width=900, height=700, bg='white')
        self.canvas_right.grid(row=0, column=1)
        self.map_right = self.canvas_right.create_image(0, 0, image=None, anchor='nw')

        # This initializes the images based on current yday and this year (left) and last year (right)
        self.update_images('left') # We need this to run ahead of the mainloop call
        self.update_images('right') # We need this to run ahead of the mainloop call

        self.root.mainloop() # This has to be here for the map images to show up

    def update_images(self, side):
        # I'm sure there's a more elegant solution to this but I wanted to get it done
        if side == 'left':
            # update the left side image based on selected year and yday
            self.image_left = self.get_image(year=self.left_year.get(), yday=self.select_day.get())
            self.canvas_left.itemconfig(self.map_left, image=self.image_left)
        elif side == 'right':
            # update the right side image based on selected year and yday
            self.image_right = self.get_image(year=self.right_year.get(), yday=self.select_day.get())
            self.canvas_right.itemconfig(self.map_right, image=self.image_right)
        else:
            print(f"Couldn't update {side}") # This would go to a log usually


    def get_image(self, year=time.gmtime().tm_year, yday=time.gmtime().tm_yday-1):
        # We need the year/yday to generate the date string for the images
        dt = datetime.strptime(f"{year} {yday}", "%Y %j").replace(tzinfo=pytz.utc)
        dtstring = dt.strftime("%Y%m%d")

        # Download the image
        req = requests.get(f"https://usicecenter.gov/products/daily/arctic/{year}/miz_graphics/miz_arc_{dtstring}.png")

        try:
            # Convert the png into an image that can be displayed by tkinter
            img = Image.open(BytesIO(req.content)).resize((890, 690))
            pyimg = ImageTk.PhotoImage(img)
            return pyimg
        except Exception as e:
            # Just in case something goes wrong (would go to a logger if I implemented logging)
            print("Could not convert image: ")
            print(f"{e}")
            return None
    
    def decrement(self):
        # Subtract one day from the yday and update variable and display accordingly
        yday = int(self.select_day.get())-1
        self.select_day.set(yday)
        self.yday_lbl.config(text=self.select_day.get())
        self.update_images('left')
        self.update_images('right')

    def increment(self):
        # Add one day from the yday and update variable and display accordingly
        yday = int(self.select_day.get())+1
        self.select_day.set(yday)
        self.yday_lbl.config(text=self.select_day.get())
        self.update_images('left')
        self.update_images('right')



if __name__ == "__main__":
    app = Application()
