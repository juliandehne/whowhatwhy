
Select * from delab_moderationcandidate2 dm
    where dm.tweet_id in
        (select id from delab_tweet dt where simple_request_id = 932)
            and dm.id not in
        (select mod_candidate_id from delab_moderationrating);


select * from delab_moderationcandidate2 dm
    where dm.tweet_id in
        (select id from delab_tweet dt where dt.text like '%whataboutism%')
            and dm.id not in
        (select mod_candidate_id from delab_moderationrating)
