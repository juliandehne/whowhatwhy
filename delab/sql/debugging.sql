delete from delab_tweet b where b.topic_id = 8;

select count(distinct author_id) from delab_tweet d where d.topic_id = 8;

select * from delab_tweetauthor a join delab_tweet dt on a.id = dt.tw_author_id where dt.topic_id = 8