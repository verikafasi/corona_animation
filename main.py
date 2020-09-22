import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import data_collect
import os
import numpy as np

os.environ["CARTOPY_USER_BACKGROUNDS"] = "./background/"


def create_map(date, df, ax):
    if ax is None:
        fig = plt.figure(figsize=(19.2, 10.8))
        ax = plt.axes(projection=ccrs.Mercator(min_latitude=-65,
                                               max_latitude=70))
    ax.background_img(name='BM', resolution='low')
    ax.set_extent([-170, 179, -65, 70], crs=ccrs.PlateCarree())
    ax.scatter(list(df['lng']), list(df['lat']),
               s=list(np.sqrt(df['confirmed'])*10), alpha=0.7,
               transform=ccrs.PlateCarree(),
               color='red')

    fontname = 'Open Sans'
    fontsize = 28  # Positions for the date and grad counter
    date_x = -53
    date_y = -50
    date_spacing = 65  # Positions for the school labels

    # Date text
    ax.text(date_x, date_y,
            f"{date.strftime('%b %d, %Y')}",
            color='white',
            fontname=fontname, fontsize=fontsize * 1.3,
            transform=ccrs.PlateCarree())  # Total grad counts

    ax.text(date_x + date_spacing, date_y,
            "Confirmed:", color='white',
            fontname=fontname, fontsize=fontsize,
            transform=ccrs.PlateCarree())
    n_casualty = int(df.groupby('countryregion')['confirmed'].sum().sum())
    ax.text(date_x + date_spacing * 1.7, date_y,
            f"{n_casualty}",
            color='white', ha='left',
            fontname=fontname, fontsize=fontsize * 1.2,
            transform=ccrs.PlateCarree())

    ax.text(date_x + date_spacing, date_y - 10,
            "Death:", color='white',
            fontname=fontname, fontsize=fontsize,
            transform=ccrs.PlateCarree())
    n_casualty = int(df.groupby('countryregion')['deaths'].sum().sum())

    ax.text(date_x + date_spacing * 1.7, date_y - 10,
            f"{n_casualty}",
            color='white', ha='left',
            fontname=fontname, fontsize=fontsize * 1.3,
            transform=ccrs.PlateCarree())
    ax.text(-170, date_y - 12,
            "verikafasi.org",
            color='white', ha='left',
            fontname=fontname, fontsize=fontsize,
            transform=ccrs.PlateCarree())

    return ax



start_date = dt.date(2020,1,22)
end_date = dt.date(2020,3,14)

fig = plt.figure(figsize=(19.2, 10.8))
ax = plt.axes(projection=ccrs.Mercator(min_latitude=-65,
                                       max_latitude=70))

ts_list, country_df = data_collect.get_time_series(by_country=False)

os.system("rm frames/*")
os.system("rm corona.mp4")
os.system("rm corona_w_music"
          ".mp4")
last = 0
# Generate an image for each day between start_date and end_date
for ii, days in enumerate(range((end_date - start_date).days)):
    date = start_date + dt.timedelta(days)
    df = data_collect.get_date_state(date, country_df, ts_list)
    df = df.dropna()
    ax = create_map(date, df, ax=ax)
    fig.tight_layout(pad=-0.5)
    fig.savefig(f"frames/frame_{ii:04d}.png", dpi=100,
                frameon=False, facecolor='black')
    ax.clear()
    last = ii

for jj in range(1,8):
    ii = last + jj
    df = data_collect.get_date_state(end_date, country_df, ts_list)
    df = df.dropna()
    ax = create_map(end_date, df, ax=ax)
    fig.tight_layout(pad=-0.5)
    fig.savefig(f"frames/frame_{ii:04d}.png", dpi=100,
                frameon=False, facecolor='black')
    ax.clear()

os.system("ffmpeg -framerate 3 -i frames/frame_%4d.png -c:v h264 -r 30 -s 1920x1080 ./corona.mp4")
os.system("ffmpeg -i corona.mp4 -i Loss.mp3 -c copy -shortest corona_w_music.mp4")

