import geopandas as gpd 
from numpy import zeros, unique, loadtxt
from matplotlib import pyplot as plt
import geoip2.database as geodb
import geoip2.errors as geoerrors
from os import path
import sys

## DEFINE SET STYLES FOR PLOTTING ##
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Ubuntu'
plt.rcParams['font.monospace'] = 'Ubuntu Mono'
plt.rcParams['font.size'] = 20
plt.rcParams['axes.labelsize'] = 22
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.linewidth'] = 2
plt.rcParams['axes.titlesize'] = 19
plt.rcParams['axes.labelpad'] = 15
plt.rcParams['xtick.labelsize'] = 19
plt.rcParams['ytick.labelsize'] = 19
plt.rcParams['legend.fontsize'] = 25
plt.rcParams['figure.titlesize'] = 19
plt.rcParams['figure.figsize'] = (8,8)
plt.rcParams['lines.linewidth'] = 3
plt.rcParams['errorbar.capsize'] = 3.5

### HANDLE ARGUMENT ##
if len(sys.argv) == 1:
    print('Usage %s <ip>...' % sys.argv)
    sys.exit(1)

### Define the path in the library to the lookup DB
lookup_dir = path.abspath(path.dirname(__file__))
dir_fn = path.join(lookup_dir, '..', 'lookup', 'GeoLite2-City_20200407', 'GeoLite2-City.mmdb')

### FUNCTIONS ##

def load_reader(path_to_reader='../lookup/GeoLite2-City_20200407/GeoLite2-City.mmdb'):
    reader = geodb.Reader(path_to_reader)

    return reader

def city_single_ip(ip_string, reader):
    '''Takes single IP address as a string object and returns the response object 
    for the reader. 
    '''
    response = reader.city(ip_string)
    return response

def extract_multiple_ip_coordinates(list_of_ips, reader):
    '''Takes an iterable (list/array) of IP addresses (strings) and extracts them
    from the reader database. 
    '''
    list_of_ips = unique(list_of_ips) # We only care about the unique IPs 
    latitudes = zeros(len(list_of_ips))
    longitudes = zeros(len(list_of_ips))
    for i,p in enumerate(list_of_ips):
        print("On IP %s out of %s " % (str(i), str(len(list_of_ips))))
        try:
            response = city_single_ip(p, reader)
            latitudes[i] = response.location.latitude
            longitudes[i] = response.location.longitude
        except geoerrors.AddressNotFoundError:
            continue
    return longitudes, latitudes

def extract_multiple_ip_dbhits(list_of_ips, reader):  
    '''Takes an iterable (list/array) of IP addresses (strings) and extracts them
    from the reader database. 
    '''
    list_of_ips = unique(list_of_ips) # We only care about the unique IPs 
    db_hits = []
    for i,p in enumerate(list_of_ips):
        print("On IP %s out of %s " % (str(i), str(len(list_of_ips))))
        try:
            response = city_single_ip(p, reader)
            db_hits.append(response)
            # latitudes[i] = response.location.latitude
            # longitudes[i] = response.location.longitude
        except geoerrors.AddressNotFoundError:
            continue
    return db_hits

def generate_map_w_coords(longitudes, latitudes):
    gdf =  gpd.GeoDataFrame(geometry=gpd.points_from_xy(x=longitudes, y=latitudes))
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Now the actual plotting begins
    fig,ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_facecolor('#A8C5DD')
    world.plot(ax=ax, color='#EDC9AF', edgecolor='black')
    gdf.plot(ax=ax, marker='o', color="#0652ff", alpha=0.3, markersize=1)
    fig.set_size_inches((16,8))
    plt.tight_layout()
    plt.savefig("./map-image.png", dpi=300)
    return fig

def read_ip_files(fn):
    '''Reads filename and returns as iterable array of string
    '''
    ip_list = loadtxt(fn, dtype=str)
    return ip_list

def main():
    ip_fn = sys.argv[1]
    # reader_fn = sys.argv[2]
    db_reader = load_reader(str(dir_fn))
    ip_list = read_ip_files(ip_fn)
    longs, lats = extract_multiple_ip_coordinates(ip_list, db_reader)
    generate_map_w_coords(longs, lats)


if __name__ == "__main__":
    main()


