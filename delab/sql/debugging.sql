select count( distinct dt.conversation_id) from delab_tweet dt inner join delab_moderationcandidate2 m on m.tweet_id = dt.id
select count(*) from delab_moderationcandidate2;
select count(*) from delab_tweet;

select * from delab_moderationcandidate2 where tweet_id in
                                             (select dt.id from delab_tweet dt where dt.platform = 'twitter' and dt.simple_request_id == )
                                         and id in
                                             (select mod_candidate_id from delab_moderationrating);

