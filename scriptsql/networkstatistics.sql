
select count(dt1.id) as followerdownloaded
from delab_tweetauthor dt1
where dt1.follower_downloaded is TRUE;

select count(dt1.id) as followingdownloaded
from delab_tweetauthor dt1
where dt1.following_downloaded is TRUE;

select count(dt1.id) as authornumber
from delab_tweetauthor dt1;

select count(*) from delab_followernetwork