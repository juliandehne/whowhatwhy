update delab_tweet set conversation_id = twitter_id
    where platform='reddit' and conversation_id != twitter_id and tn_parent_id is NULL