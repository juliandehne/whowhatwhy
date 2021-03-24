from blog.models import Post
from searchtweets import ResultStream,load_credentials, gen_rule_payload, collect_results


def run():
    print(Post.objects.first().title)
    credentials: dict = load_credentials(filename="C:\\Users\\julia\\PycharmProjects\\djangoProject\\twitter\\secret\\keys.yaml",
                     yaml_key="search_tweets_api",
                     env_overwrite=False)
    rule = gen_rule_payload("beyonce", results_per_call=2)  # testing with a sandbox account
    print(rule)
    tweets = collect_results(rule, max_results=2, result_stream_args=credentials)
    print(tweets)

