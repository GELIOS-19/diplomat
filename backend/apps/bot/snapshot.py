from pathlib import Path

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

transport = AIOHTTPTransport(url="https://hub.snapshot.org/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)


def query_snapshot_proposal(proposal_id: str):
    """
    Fetches data for a specific proposal from Snapshot.

    Parameters:
    -----------
    proposal_id : str
        The unique identifier for the proposal.

    Returns:
    --------
    dict:
        The data of the proposal as a dictionary.
    """

    with open(
        Path(__file__).parent / "text_templates" / "queries" / "proposal.txt",
        "r",
    ) as query_file:
        query = query_file.read().format(proposal_id=proposal_id)
        return client.execute(gql(query))


def query_snapshot_space(space_id: str):
    """
    Fetches data for a specific space from Snapshot.

    Parameters:
    -----------
    space_id : str
        The unique identifier for the space.

    Returns:
    --------
    dict:
        The data of the space as a dictionary.
    """
    with open(
        Path(__file__).parent / "text_templates" / "queries" / "space.txt",
        "r",
    ) as query_file:
        query = query_file.read().format(space_id=space_id)
        return client.execute(gql(query))
