# %%
import pathlib
import pandas as pd
import folium
from branca.element import Template, MacroElement
import matplotlib.pyplot as plt
import io
import numpy as np
from typing import Dict, List, Tuple

# Configuration for file paths

data = pathlib.Path("/mnt/c/Users/marco/polling places/data")
CONFIG: Dict[str, str] = {
    "expected_polling_places_file": data / "prdelms.gaz.statics.250405.09.00.02.csv",
    "last_polling_places_file": data / "GeneralPollingPlacesDownload-27966.csv",
    "votes_file": data / "HouseStateFirstPrefsByPollingPlaceDownload-27966-NSW.csv",
}


# %%
def load_expected_polling_places(file_path: str, division: str) -> pd.DataFrame:
    """Load the expected polling places file and filter by division."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(
            f"Error: The file '{file_path}' was not found. Please check the file path."
        )
        exit()
    df = df[df["DivName"].str.contains(division) & (df["Status"] != "Abolition")]
    df["PremisesName"] = df["PremisesName"].str.strip()
    df["PremisesName"].replace(
        {"TAFE NSW (Ultimo Campus)": "TAFE NSW Ultimo Campus"}, inplace=True
    )
    return df


def load_last_polling_places(
    file_path: str,
    df_expected: pd.DataFrame,
    division: str,
    neighbouring_division: Dict[str, List[str]],
    not_prepoll: bool,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load the last polling places file and filter by division and premises."""
    df_last_polling_places = pd.read_csv(file_path, skiprows=1)
    df_last_polling_places["PremisesNm"] = df_last_polling_places["PremisesNm"].replace(
        {"3A Joynton Avenue Creative Centre": "Joynton Avenue Creative Centre"}
    )
    df_subset = df_last_polling_places[
        df_last_polling_places["PremisesNm"].isin(df_expected["PremisesName"])
        & df_last_polling_places["DivisionNm"].isin(neighbouring_division[division])
    ]
    if not_prepoll:
        df_subset = df_subset[~df_subset["PollingPlaceNm"].str.contains("PP")]
    return df_last_polling_places, df_subset


def load_votes(
    file_path: str, df_last_polling_places_subset: pd.DataFrame
) -> pd.DataFrame:
    """Load the votes file and filter by polling places."""
    df_votes = pd.read_csv(file_path, skiprows=1)
    df_votes_subset = df_votes[
        df_votes["PollingPlaceID"].isin(df_last_polling_places_subset["PollingPlaceID"])
    ].merge(
        df_last_polling_places_subset[["PremisesNm", "PollingPlaceID"]],
        on="PollingPlaceID",
    )
    return df_votes_subset


def generate_party_mapping(parties: List[str]) -> Dict[str, str]:
    """Generate a mapping of party names to categories."""
    party_mapping = {}
    for party in parties:
        if "Labor" in party:
            party_mapping["Labor"] = party
        elif "Greens" in party:
            party_mapping["Greens"] = party
        elif "Liberal" in party and "Democrats" not in party:
            party_mapping["Liberal"] = party
        elif "Independent" in party:
            party_mapping["Independent"] = party
        elif "One Nation" in party:
            party_mapping["One Nation"] = party
        elif "United Australia" in party:
            party_mapping["United Australia"] = party
    return party_mapping


def pivot_table(df: pd.DataFrame, Party_to_colour: Dict[str, str]) -> pd.Series:
    """Create a pivot table summarizing votes by party."""
    votes = {
        party: df.loc[df["PartyNm"] == party, "OrdinaryVotes"].sum()
        for party in Party_to_colour
        if party != "Other"
    }
    votes.update(
        {
            "Other": df.loc[
                ~df["PartyNm"].isin(Party_to_colour.keys()), "OrdinaryVotes"
            ].sum()
        }
    )
    return pd.Series(votes)


def create_map_with_markers(df: pd.DataFrame, division: str) -> None:
    """Create a map with circle markers for expected polling places."""
    if df.empty:
        print("No valid locations found.")
        exit()

    my_map = folium.Map(
        location=[df["Lat"].median(), df["Long"].median()], zoom_start=13.5
    )

    for _, row in df.iterrows():
        total_votes = row["OrdVoteEst"] + row["DecVoteEst"]
        radius = total_votes / 100
        wheelchair = row["WheelchairAccess"]
        color = (
            "blue"
            if wheelchair == "Full"
            else "grey"
            if wheelchair == "Assisted"
            else "red"
        )
        popup_html = f"""
            <div style="font-family: Arial; font-size: 14px;">
                <b style="font-size: 16px; color: darkblue;">{row["PremisesName"]}</b><br>
                <b>Estimated Ordinary Votes:</b> {row["OrdVoteEst"]}<br>
                <b>Estimated Declaration Votes:</b> {row["DecVoteEst"]}<br>
                <b>Wheelchair Access:</b> {row["WheelchairAccess"]}
            </div>
        """
        folium.CircleMarker(
            location=[row["Lat"], row["Long"]],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            fill=True,
            fill_color=color,
            color=color,
            fill_opacity=0.6,
        ).add_to(my_map)

    # Legend HTML (for both color & size)

    legend_html = """
    <div style="position: fixed; 
                bottom: 40px; left: 40px; width: 250px; height: 240px; 
                background-color: white; z-index:9999; 
                font-size:14px; padding: 10px; 
                border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <b>Polling Booth Legend</b><br>
        <b>Circle Color:</b><br>
        <div style="display: flex; align-items: center;">
            <div style="background:blue; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></div> 
            Full Wheelchair Access
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background:grey; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></div> 
            Assisted Wheelchair Access
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background:red; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></div> 
            No Wheelchair Access/No information
        </div>
        <b>Circle Size (Voter Estimate):</b><br>
        <div style="display: flex; align-items: center;">
            <div style="background:gray; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px;"></div> 
            ~500 votes
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background:gray; width: 20px; height: 20px; border-radius: 50%; margin-right: 5px;"></div> 
            ~1,000 votes
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background:gray; width: 40px; height: 40px; border-radius: 50%; margin-right: 5px;"></div> 
            ~2,000 votes
        </div>
    </div>
    """

    # Add legend to the map
    legend = MacroElement()
    legend._template = Template(f"""
        {{% macro html(this, kwargs) %}}
        {legend_html}
        {{% endmacro %}}
    """)

    my_map.get_root().add_child(legend)

    my_map.save(f"Division_of_{division}_expected_polling_day_locations.html")
    print("Map with markers has been saved.")


def create_map_with_pie_charts(
    df: pd.DataFrame, Party_to_colour: Dict[str, str], name: str
) -> None:
    """Create a map with pie chart markers for primary votes."""
    if df.empty:
        print("No valid locations found.")
        exit()

    my_map = folium.Map(
        location=[df["Lat"].median(), df["Long"].median()], zoom_start=13.5
    )

    def create_pie_chart(row: pd.Series, radius: float) -> str:
        """Generate a pie chart as an SVG string."""
        diameter = radius * 2
        scale_factor = 2
        px = 1 / plt.rcParams["figure.dpi"]
        fig, ax = plt.subplots(
            figsize=(diameter * px * scale_factor, diameter * px * scale_factor)
        )
        values = [
            row.get(party, 0) if not np.isnan(row.get(party, 0)) else 0
            for party in Party_to_colour.keys()
        ]
        colors = list(Party_to_colour.values())

        ax.pie(values, labels=None, colors=colors, startangle=90)
        ax.set_xticks([])
        ax.set_yticks([])

        buff = io.StringIO()
        plt.savefig(buff, format="svg", bbox_inches="tight", transparent=True)
        buff.seek(0)
        svg = buff.getvalue()
        plt.close(fig)
        return svg

    for _, row in df.iterrows():
        popup_html = f"""
        <div style="font-family: Arial; font-size: 14px;">
        <b style="font-size: 16px; color: darkblue;">{row["PremisesName"]}</b><br>
        """
        if "OrdVoteEst" in row:
            total_votes = row["OrdVoteEst"] + row["DecVoteEst"]

            popup_html += f"""
                <b>Estimated Ordinary Votes:</b> {row["OrdVoteEst"]}<br>
                <b>Estimated Declaration Votes:</b> {row["DecVoteEst"]}<br>
                <b>Wheelchair Access:</b> {row["WheelchairAccess"]}<br>
                """
        else:
            total_votes = np.sum(
                [row.get(party, 0) for party in Party_to_colour.keys()]
            )
            popup_html += f"""
                <b>Total votes:</b> {total_votes}<br>
                """

        radius = total_votes / 100

        votes = [
            f"<b>Last election {party} primary:</b> {row[party]}<br>"
            for party in Party_to_colour.keys()
        ]
        popup_html += f"""
                {"".join(votes)}
            </div>
        """

        if np.isnan(row[next(iter(Party_to_colour))]) or all(
            row[party] == 0 for party in Party_to_colour.keys()
        ):
            color = "grey"
            folium.CircleMarker(
                location=[row["Lat"], row["Long"]],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300),
                fill=True,
                fill_color=color,
                color="black",
                fill_opacity=0.6,
            ).add_to(my_map)
        else:
            pie_chart_svg = create_pie_chart(row, radius)
            icon_html = f"<div>{pie_chart_svg}</div>"
            folium.Marker(
                location=[row["Lat"], row["Long"]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.DivIcon(html=icon_html, icon_size=(radius * 2, radius * 2)),
            ).add_to(my_map)

    party_html = ""
    for party, colour in Party_to_colour.items():
        party_html += f"""
        <div style="display: flex; align-items: center;">
            <div style="background:{colour}; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></div> {party}
        </div>
        """

    # Legend HTML
    legend_html = f"""
    <div style="position: fixed; 
                bottom: 40px; left: 40px; width: 280px; height: auto; 
                background-color: white; z-index:9999; 
                font-size:14px; padding: 10px; 
                border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <b>Polling Booth Legend</b><br>
        <b>Circle Size (Voter Estimate):</b><br>
        <div style="display: flex; align-items: center;">
            <div style="background:gray; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px;"></div> 
            ~500 votes
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background:gray; width: 20px; height: 20px; border-radius: 50%; margin-right: 5px;"></div> 
            ~1,000 votes
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background:gray; width: 40px; height: 40px; border-radius: 50%; margin-right: 5px;"></div> 
            ~2,000 votes
        </div>
        <b>Party primary votes at last election:</b><br>
        {party_html}
        <div style="display: flex; align-items: center;">
            <div style="background:grey; border: 2px solid black; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></div> 
            New booth/No primary votes recorded
        </div>
    </div>
"""

    # Add legend to the map
    legend = MacroElement()
    legend._template = Template(f"""
        {{% macro html(this, kwargs) %}}
        {legend_html}
        {{% endmacro %}}
    """)

    my_map.get_root().add_child(legend)

    my_map.save(name)
    print("Map with pie charts has been saved.")


def main(division: str) -> None:
    neighbouring_division: Dict[str, List[str]] = {
        "Sydney": ["Sydney", "Grayndler"],
        "Wentworth": ["Sydney", "Wentworth", "Kingsford Smith"],
        "Bennelong": ["Bennelong", "North Sydney"],
        "Ryan": ["Ryan"],
        "Moreton": ["Moreton"],
    }

    # Load data
    df_expected = load_expected_polling_places(
        CONFIG["expected_polling_places_file"], division
    )
    df_last_polling_places, df_last_polling_places_subset = load_last_polling_places(
        CONFIG["last_polling_places_file"],
        df_expected,
        division,
        neighbouring_division,
        not_prepoll=True,
    )
    df_votes_subset = load_votes(CONFIG["votes_file"], df_last_polling_places_subset)

    df_last_prepolling_places_subset = df_last_polling_places.loc[
        (df_last_polling_places["DivisionNm"] == division)
        & (df_last_polling_places["PollingPlaceNm"].str.contains("PP"))
    ]

    df_votes_prepolling = load_votes(
        CONFIG["votes_file"], df_last_prepolling_places_subset
    )

    # Generate party mapping
    parties = df_votes_subset["PartyNm"].unique()
    party_mapping = generate_party_mapping(parties)
    Party_to_colour = {
        party_mapping["Labor"]: "red",
        party_mapping["Liberal"]: "blue",
        party_mapping["Greens"]: "green",
    }
    if "Independent" in party_mapping:
        Party_to_colour.update(
            {
                party_mapping["Independent"]: "lightseagreen",
            }
        )
    if "One Nation" in party_mapping:
        Party_to_colour.update(
            {
                party_mapping["One Nation"]: "orange",
            }
        )
    if "United Australia" in party_mapping:
        Party_to_colour.update(
            {
                party_mapping["United Australia"]: "yellow",
            }
        )
    Party_to_colour.update(
        {
            "Other": "grey",
        }
    )

    # Process votes by party
    df_votes_by_party = (
        df_votes_subset.groupby("PremisesNm", group_keys=False)
        .apply(lambda x: pivot_table(x, Party_to_colour), include_groups=False)
        .reset_index()
        .rename(columns={"PremisesNm": "PremisesName"})
    )
    df_primary_votes = df_expected.merge(
        df_votes_by_party, on="PremisesName", how="left"
    )

    df_pre_poll_votes_by_party = (
        df_votes_prepolling.groupby("PremisesNm", group_keys=False)
        .apply(lambda x: pivot_table(x, Party_to_colour), include_groups=False)
        .reset_index()
        # .rename(columns={"PremisesNm": "PremisesName"})
    )
    df_primary_votes_prepolling = df_last_prepolling_places_subset.merge(
        df_pre_poll_votes_by_party, on="PremisesNm", how="left"
    ).rename(
        columns={"Latitude": "Lat", "Longitude": "Long", "PremisesNm": "PremisesName"}
    )

    # Create maps
    create_map_with_markers(df_expected, division)
    create_map_with_pie_charts(
        df_primary_votes,
        Party_to_colour,
        name=f"Division_of_{division}_expected_polling_day_locations_primary_vote_last_election.html",
    )
    create_map_with_pie_charts(
        df_primary_votes_prepolling,
        Party_to_colour,
        name=f"Division_of_{division}_pre_polling_primary_vote_last_election.html",
    )


if __name__ == "__main__":
    main("Sydney")
    main("Wentworth")
    main("Bennelong")
    CONFIG.update(
        {
            "votes_file": data
            / "HouseStateFirstPrefsByPollingPlaceDownload-27966-QLD.csv",
        }
    )
    main("Moreton")
    main("Ryan")
