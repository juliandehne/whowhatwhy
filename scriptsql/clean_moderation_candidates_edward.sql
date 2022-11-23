select * from delab_moderationcandidate2 where tweet_id in (
Select id from delab_tweet where text like '%@EdwardOfIran @PahlaviReza @nedprice @JakeSullivan46 @POTUS We reject foreign made%')
and id not in (Select mod_candidate_id from delab_moderationrating);

select * from delab_moderationrating where mod_candidate_id in(
select id from delab_moderationcandidate2 where tweet_id in (
Select id from delab_tweet where text like '%@EdwardOfIran @PahlaviReza @nedprice @JakeSullivan46 @POTUS We reject foreign made%'));
