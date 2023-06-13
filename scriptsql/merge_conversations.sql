SELECT * from delab_tweet dt join delab_tweet dt2 on dt.tn_parent_id = dt2.twitter_id where dt.conversation_id <> dt2.conversation_id;

SELECT tn_parent_id from delab_tweet dt where tn_parent_id not in (select twitter_id from delab_tweet);
