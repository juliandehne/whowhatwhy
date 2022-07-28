
Select * from delab_moderationcandidate2 dm
    where dm.tweet_id in
        (select id from delab_tweet dt where simple_request_id = 932)
            and dm.id not in
        (select mod_candidate_id from delab_moderationrating);


select from delab_moderationcandidate2 dm
    where dm.tweet_id in
        (select id from delab_tweet dt where dt.text like '%whataboutism%')
            and dm.id not in
        (select mod_candidate_id from delab_moderationrating);


select * from delab_moderationrating dr where dr.mod_candidate_id in
(select dm.id from delab_moderationcandidate2 dm
    join delab_tweet tw
        on dm.tweet_id = tw.id
            where tw.platform = 'reddit');


select from delab_twintolerancerating dr where dr.candidate_id in
(select dm.id from delab_twcandidateintolerance dm
    join delab_tweet tw
        on dm.tweet_id = tw.id
            where tw.platform = 'reddit');

select from delab_twcandidateintolerance where id in
(select dm.id from delab_twcandidateintolerance dm
    join delab_tweet tw
        on dm.tweet_id = tw.id
            where tw.platform = 'reddit');

