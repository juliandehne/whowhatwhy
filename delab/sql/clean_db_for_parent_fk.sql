delete
from delab_twcandidate cand
where cand.tweet_id in
      (SELECT distinct dt.id
       from delab_tweet dt
       where dt.tn_parent is not null
         and (dt.tn_parent not in
              (SELECT distinct twitter_id from delab_tweet)));

delete
from delab_tweet dt
where dt.tn_parent not in
      (SELECT distinct twitter_id from delab_tweet)
  and dt.tn_parent is not null

