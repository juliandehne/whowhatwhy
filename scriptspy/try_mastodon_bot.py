from mastodon import Mastodon
import yaml

def create():
    """
    You have to register your application in the mastodon web app first,
    (home/preferences/Development/new application)
    then save the necessary information in the file that is called
    """

    with open("../twitter/secret/secret_mstd.yaml", 'r') as f:
        access = yaml.safe_load(f)

    mastodon = Mastodon(client_id=access["client_id"],
                        client_secret=access["client_secret"],
                        access_token=access["access_token"],
                        api_base_url="https://mastodon.social/"
                        )
    return mastodon


mastodon = create()
status = "Super, es scheint zu funktionieren!"
mastodon.status_post(status=status, in_reply_to_id=110808535893104049)