import folium
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Sample list of addresses
addresses_raw = [
    "Mayfield, Cnr Maitland Rd & Valencia St, Mayfield, NSW 2304",
    "Mt Hutton, 46 Wilson Rd, Mt Hutton, NSW 2290",
    "Charlestown Square, 30 Pearson St, Charlestown, NSW 2290",
    "Cardiff, Cnr Macquarie & Main Rds, Cardiff, NSW 2285",
    "Glendale, 387 Lake Rd, Glendale, NSW 2285",
    "Cameron Park, Cameron Park Plaza, Cnr Portland Dr & Northridge Dr, Cameron Park, NSW 2285",
    "Kotara, 89 Park Ave, Kotara, NSW 2289",
    "Newcastle West, 23 Steel St, Newcastle West, NSW 2302",
    "Jesmond, 24–26 Blue Gum Rd, Jesmond, NSW 2299",
    "Maryland, 144 Maryland Dr, Maryland, NSW 2287",
    "Warabrook, 3 Angophora Dr, Warabrook, NSW 2304",
    "Beresfield, Cnr Lawson & Newton St, Beresfield, NSW 2322",
    "Green Hills, Stockland Centre, 1 Molly Morgan Dr, East Maitland, NSW 2323",
    "Raymond Terrace, 39–41 Glenelg St, Raymond Terrace, NSW 2324",
    "Rutherford, Cnr Alexandra Ave & Hillview St, Rutherford, NSW 2320",
    "Salamander Bay, 2 Town Centre Cct, Salamander Bay, NSW 2317",
    "Nelson Bay, Cnr Stockton St & Donald St, Nelson Bay, NSW 2315",
    "Medowie, 39–47 Ferodale Rd, Medowie, NSW 2318",
    "Forster, Cnr The Lakes Way & Breese Pde, Forster, NSW 2428",
    "Tuncurry, Cnr Peel & Kent St, Tuncurry, NSW 2428",
    "Taree, 60 Manning St, Taree, NSW 2430",
    "Belmont, Cnr Macquarie & Singleton St, Belmont, NSW 2280",
    "Lakewood, 10 Botanic Dr, Lakewood, NSW 2443",
    "Lake Cathie, Lot 2 Ocean Dr, Lake Cathie, NSW 2445",
    "Port Macquarie, Cnr Bay & Park Sts, Port Macquarie, NSW 2444",
    "Caddens, 68 O'Connell St, Caddens, NSW 2747",
    "Cranebrook, 80 - 98 Borrowdale Way, Cranebrook, NSW 2749",
    "Emu Plains, Lennox Shop. Ctr, Cnr Great Western Hwy & Lawson St, Emu Plains, NSW 2750",
    "Glenmore Park, Cnr Town Tce & Glenmore Parkway, Glenmore Park, NSW 2745",
    "Jordan Springs, Cnr Lakeside Pde & Jordan Springs Bvd, Jordan Springs, NSW 2747",
    "Penrith, 569 - 589 High St, Penrith, NSW 2750",
    "Richmond, Cnr Lennox & Paget St, NSW 2753",
    "South Penrith, Southlands Shop. Ctr, 2 Birmingham Rd, South Penrith, NSW 2750",
    "Windsor, Windsor Town Shop. Ctr, Kable St, Windsor, NSW 2756",
    "Blacktown, Westpoint Shop. Ctr, 17 Patrick St, Blacktown, NSW 2148",
    "Eastern Creek, 159 Rooty Hill Road South, NSW 2766",
    "Emerton, 40 Jersey Rd, Emerton, NSW 2770",
    "Greenway Village, Shop M1 799 Richmond Rd, Colebee, NSW 2761",
    "Kings Langley, Cnr James Cook Dr & Ravenhill St, Kings Langley, NSW 2147",
    "Marayong, Quakers Ct, Cnr Falmouth & Quaker Rds, Marayong, NSW 2148",
    "Mt Druitt, Westfields, 49 Luxford Rd, Mt Druitt, NSW 2770",
    "Plumpton, Plumpton Market Pl, Cnr Jersey & Hyatts Rds, Plumpton, NSW 2761",
    "Prospect, Cnr Flushcombe Rd & Myrtle St, Prospect, NSW 2148",
    "Seven Hills, 224 Prospect Hwy, Seven Hills, NSW 2147",
    "St Clair, St Clair Shop. Ctr, Cnr Bennett Rd & Endeavour St, St Clair, NSW 2759",
    "St Mary's, St Marys Village Shop. Ctr, Shop 302, Charles Hackett Dr, NSW 2760",
    "Bonnyrigg, Bonnyrigg Ave, Bonnyrigg, NSW 2177",
    "Cabramatta, 180 Railway Pde, Cabramatta, NSW 2166",
    "Cecil Hills, Cnr Sandringham Dr & Fedore Rd, Cecil Hills, NSW 2171",
    "Fairfield, Neeta City Shop. Ctr, 1 - 29 Court St, Fairfield, NSW 2165",
    "Fairfield Heights, 186 The Bvd, Fairfield Heights, NSW 2165",
    "Green Valley, The Valley Plaza, 187 Wilson Rd, Hinchinbrook, NSW 2168",
    "Greystanes, 655 Merrylands Rd, Greystanes, NSW 2145",
    "Pemulwuy, Cnr Greystanes Rd & Butu Wargun Dr, Pemulwuy, NSW 2145",
    "Toongabbie, 17 - 19 Aurelia St, Pemulwuy, NSW 2145",
    "Wentworthville, 326 - 336 Great Western Hwy, Wentworthville, NSW 2145",
    "Wetherill Park, Cnr Restwell Rd & Prairie Vale Rd, Wetherill Park, NSW 2164",
    "Baulkham Hills, 375 - 383 Windsor Rd, Baulkham Hills, NSW 2153",
    "Dural, Round Crn 494 - 500 Old Northern Rd, Round Corner, NSW 2158",
    "Glenorie, 936 - 938 Old Northern Rd, Glenorie, NSW 2157",
    "Glenwood, 60 Glenwood Park Dr, Glenwood, NSW 2768",
    "Kellyyville North, Cnr Withers & Hezlett Rds, Kellyville North, NSW 2155",
    "Kellyville North, 2 Hector Court, Kellyville, NSW 2155",
    "Schofields, Railway Tce and Pelican Rds, Schofields, NSW 2762",
    "Rouse HIll, 10 - 14 Market Lane, Rouse Hill, NSW 2155",
    "Camden, 35 Oxley St, Camden, NSW 2570",
    "Campbelltown Macarthur Sq, Shop. Ctr, Cnr Gilchrist Dr & Kellicar Rd, Campbelltown, NSW 2560",
    "Campbelltown Mall, 271 Queen St, Campbelltown, NSW 2560",
    "Campbelltown Market Fair, Cnr Tindall St And Kellicar & Narellan Rds, Campbelltown, NSW 2560",
    "Gregory Hills, Cnr of Village Circuit & Gregory Hills Dr, Gregory Hills, NSW 2557",
    "Mt Annan, 11 - 13 Main St, Mt Annan, NSW 2567",
    "Narellan, Narellan Town Centre, 326 Camden Vally Way, Narellan, NSW 2567",
    "Oran Park, Oran Park Dr & Peter Brock Dr, Oran Park, NSW 2570",
    "Rosemeadow, Cnr Copperfield & Thomas Rose Drs, Rosemeadow, NSW 2560",
    "Spring Farm, 254 Richardson Rd, Spring Farm, NSW 2570",
    "Carnes Hill, Cnr Cowpasture & Kurajong Rds, Carnes Hill, NSW 2171",
    "Casula, 607 Hume Hwy, Casula, NSW 2170",
    "Liverpool, Westfield Shop. Ctr, Cnr Campbell & Northumberland St, Liverpool, NSW 2170",
    "Miller, Miller Community Shopping Cente, Cartwright Ave, Miller, NSW 2168",
    "Moorebank, Moorebank Shop. Vge, 136 Stockton Ave, Moorebank, NSW 2170",
    "Prestons, 1975 - 1985 Camden Valley Way, Prestons, NSW 2170",
    "Auburn, Cnr Queen & Park Rd, Auburn, NSW 2144",
    "Bass Hill, 753 Hume Hwy, Bass Hill, NSW 2197",
    "Berala, 15 - 16 Woodburn Rd, Berala, NSW 2141",
    "Chester Hill, Chester Sq Shop. Ctr, 1 - 13 Leicester St, Chester Hill, NSW 2162",
    "Chullora, 355 Waterloo Rd, Chullora, NSW 2190",
    "Granville, Cnr Louis & Blaxcell St, Granville, NSW 2142",
    "Lidcombe, 92 Parramatta Rd, Lidcombe, NSW 2144",
    "Merrylands, 209 Pitt St, Merrylands, NSW 2160",
    "Newington, 1 Ave Of Americas, Newington, NSW 2127",
    "North Parramatta, 1-9 North Rocks Road, North Parramatta, NSW 2151",
    "Parramatta, Westfield Shop. Ctr, 159 - 175 Church St, Parramatta, NSW 2150",
    "Ashfield, 260A Liverpool Rd, Ashfield, NSW 2131",
    "Ashfield North, 202-242 Parramatta Road, Ashfield, NSW 2131",
    "Bankstown, Centro Shop. Ctr, Lady Cutler Ave, Bankstown, NSW 2200",
    "Burwood, Shop 6, Level 3, Westfield Shop. Ctr, 100 Burwood Rd, Burwood, NSW 2134",
    "Burwood Plaza, Burwood Plaza Shop. Ctr, 42 - 50 Railway Pde, Burwood, NSW 2134",
    "Campsie, 68 - 72 Evaline St, Campsie, NSW 2194",
    "Canterbury, 2A Charles St, Canterbury, NSW 2193",
    "Lakemba, 2 - 26 Haldon St, Lakemba, NSW 2195",
    "Punchbowl, 1 - 9 the Bvd, Punchbowl, NSW 2196",
    "Strathfield, Shop 19, Strathfield Plaza, 11 The Bvd, Strathfield, NSW 2135",
    "Revesby, 60 Marco Ave, Revesby, NSW 2212",
    "Katoomba, Cnr Parke & Waratah St, Katoomba, NSW 2780",
    "Balmain, 276 Darling St, Balmain, NSW 2041",
    "Granville, Cnr Louis & Blaxcell St, Granville, NSW 2142",
    "Parramatta, Westfield Shop. Ctr, 159 - 175 Church St, Parramatta, NSW 2150",
    "Ashfield, 260A Liverpool Rd, Ashfield, NSW 2131",
    "Kings Langley, Cnr James Cook Dr & Ravenhill St, Kings Langley, NSW 2147",
    "Glenwood, 60 Glenwood Park Dr, Glenwood, NSW 2768",
    "Kellyville, 48 Wrights Rd, Kellyville, NSW 2155",
    "Kellyville Grove, 2 Hector Court, Kellyville, NSW 2155",
    "Cecil Hills, Cnr Sandringham Dr & Fedore Rd, Cecil Hills, NSW 2171",
    "Lidcombe, 92 Parramatta Rd, Lidcombe, NSW 2144",
    "Baulkham Hills, 375 - 383 Windsor Rd, Baulkham Hills, NSW 2153",
    "Camden, 35 Oxley St, Camden, NSW 2570",
    "Revesby, 60 Marco Ave, Revesby, NSW 2212",
    "Toongabbie, 17 - 19 Aurelia St Toongabbie, NSW 2146",
    "Bonnyrigg, Bonnyrigg Ave, Bonnyrigg, NSW 2177",
    "North Parramatta, 1-9 North Rocks Road, North Parramatta, NSW 2151",
]

addresses = []

for address in addresses_raw:
    suburb, split_address = address.split(", ", maxsplit=1)

    if split_address[0].isdigit():
        addresses.append(split_address)

    else:
        addresses.append(f"Woolworths {suburb}")
addresses = [address.split(", ", maxsplit=1)[1] for address in addresses_raw]


# Initialize geocoder
geolocator = Nominatim(user_agent="address_mapper")


# Function to get latitude and longitude
def get_lat_lon(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except GeocoderTimedOut:
        return None, None


# Create a DataFrame
data = {"Address": addresses}
df = pd.DataFrame(data)

# Get coordinates
df["Latitude"], df["Longitude"] = zip(*df["Address"].apply(get_lat_lon))

# Initialize a map centered around the first valid location
valid_locations = df.dropna(subset=["Latitude", "Longitude"])
if not valid_locations.empty:
    first_location = valid_locations.iloc[0]
    my_map = folium.Map(
        location=[first_location["Latitude"], first_location["Longitude"]], zoom_start=5
    )
else:
    print("No valid locations found.")
    exit()

# Add markers to the map
for _, row in valid_locations.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=row["Address"],
        icon=folium.Icon(color="blue"),
    ).add_to(my_map)

# Save map to an HTML file
my_map.save("map.html")
print("Map has been saved as map.html. Open it in your browser.")
