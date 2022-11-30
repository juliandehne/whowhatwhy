select * from delab_moderationrating where mod_candidate_id in(
select id from delab_moderationcandidate2 where tweet_id in (
Select id from delab_tweet where text like '%bot_message%'));

select from delab_moderationcandidate2 where tweet_id in (
Select id from delab_tweet where text like '%bot_message%');

Select tweet.id,d.id
    from delab_tweet tweet join delab_moderationcandidate2 d
    on tweet.id = d.tweet_id
where text like '%Hass und Häme%';