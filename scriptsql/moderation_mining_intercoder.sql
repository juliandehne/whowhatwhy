
select dt.text, ds.created_at, ds.title, mr.u_moderating_part, mr.u_mod_rating, mr2.u_mod_rating, mr.mod_coder_id, mr2.mod_coder_id
from delab_moderationrating mr
    join delab_moderationcandidate2 d on mr.mod_candidate_id = d.id
    join delab_moderationrating mr2 on mr2.mod_candidate_id = d.id
    join delab_tweet dt on dt.id = d.tweet_id
    join delab_simplerequest ds on dt.simple_request_id = ds.id
where mr.u_moderating_part is not null
  and mr.u_moderating_part <> ''
  and mr.mod_coder_id <> mr2.mod_coder_id
  and mr.u_mod_rating <> mr2.u_mod_rating;

select dt.text, ds.created_at, mr.u_moderating_part, mr.u_mod_rating
from delab_moderationrating mr
    join delab_moderationcandidate2 d on mr.mod_candidate_id = d.id
    join delab_tweet dt on dt.id = d.tweet_id
    join delab_simplerequest ds on dt.simple_request_id = ds.id
where mr.u_moderating_part is not null
  and mr.u_moderating_part <> ''
  and mr.u_mod_rating = 0;

select ds.created_at, ds.title, mr.u_mod_rating, mr.mod_coder_id
from delab_moderationrating mr
    join delab_moderationcandidate2 d on mr.mod_candidate_id = d.id
    join delab_tweet dt on dt.id = d.tweet_id
    join delab_simplerequest ds on dt.simple_request_id = ds.id
where mr.u_moderating_part is not null
  and mr.u_moderating_part <> ''

