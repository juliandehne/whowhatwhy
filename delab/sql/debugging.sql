select count( distinct dt.conversation_id) from delab_tweet dt inner join delab_moderationcandidate2 m on m.tweet_id = dt.id

select count(*) from delab_moderationcandidate2;
select count(*) from delab_moderationrating;