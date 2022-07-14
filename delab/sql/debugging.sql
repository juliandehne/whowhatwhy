select count( distinct dt.conversation_id) from delab_tweet dt inner join delab_moderationcandidate2 m on m.tweet_id = dt.id
select count(*) from delab_moderationcandidate2;
select count(*) from delab_tweet;

delete from delab_moderationcandidate2 where tweet_id in
                                             (select dt.id from delab_tweet dt where dt.platform = 'reddit' and dt.tn_parent_id is null)
                                         and id not in
                                             (select mod_candidate_id from delab_moderationrating);

delete from delab_tweet where platform = 'reddit';