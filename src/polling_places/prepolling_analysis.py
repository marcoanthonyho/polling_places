from IPython.display import display
import pandas as pd
from polling_places.polling_places import (
    CONFIG,
    load_votes,
    generate_party_mapping,
    load_last_polling_places,
    load_expected_polling_places,
)

division = "Sydney"
neighbouring_division: dict[str, list[str]] = {
    "Sydney": ["Sydney", "Grayndler"],
    "Wentworth": ["Sydney", "Wentworth", "Kingsford Smith"],
    "Bennelong": ["Bennelong", "North Sydney"],
    "Ryan": ["Ryan"],
    "Moreton": ["Moreton"],
}
df_expected = load_expected_polling_places(
    CONFIG["expected_polling_places_file"], division
)

df_last_polling_places, _ = load_last_polling_places(
    CONFIG["last_polling_places_file"], df_expected, division, neighbouring_division
)

df_cbd = df_last_polling_places[
    df_last_polling_places["PremisesNm"].isin(
        ["Sydney Masonic Centre", "York Events", "TAFE NSW Ultimo Campus"]
    )
]


def pivot_table(df: pd.DataFrame, Party_to_colour: dict[str, str]) -> pd.Series:
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
            ].sum(),
            "PremisesNm": df["PremisesNm"].values[0],
            "DivisionNm": df["DivisionNm"].values[0],
        }
    )
    return pd.Series(votes)


df_votes_cbd = load_votes(CONFIG["votes_file"], df_cbd)

parties = df_votes_cbd["PartyNm"].unique()
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

display("Absentee votes")
for premises in [
    "Sydney Masonic Centre",
    "York Events",
    "TAFE NSW Ultimo Campus",
]:
    df_prepolling = (
        df_votes_cbd.groupby("PollingPlace", group_keys=False)
        .apply(lambda x: pivot_table(x, Party_to_colour), include_groups=False)
        .reset_index()
    ).query("PremisesNm == @premises")

    # display(df_prepolling.query("DivisionNm == 'Sydney'"))
    # display(df_prepolling[(df_prepolling["DivisionNm"] != 'Sydney') & df_prepolling["PollingPlace"].str.contains("PP")])
    display(premises)
    display(
        df_prepolling[
            (df_prepolling["DivisionNm"] != "Sydney")
            & df_prepolling["PollingPlace"].str.contains("PP")
        ].sum(numeric_only=True)
    )
    print(
        "Total absentee prepoll votes:",
        df_prepolling[
            (df_prepolling["DivisionNm"] != "Sydney")
            & df_prepolling["PollingPlace"].str.contains("PP")
        ]
        .sum(numeric_only=True)
        .sum(),
    )
    print(
        "Total division of Sydney prepoll votes:",
        df_prepolling[
            (df_prepolling["DivisionNm"] == "Sydney")
            & df_prepolling["PollingPlace"].str.contains("PP")
        ]
        .sum(numeric_only=True)
        .sum(),
    )
    # display(df_prepolling.query("DivisionNm != 'Sydney' & PollingPlace contains PP").sum(numeric_only=True))
