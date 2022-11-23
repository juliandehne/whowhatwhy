select count(ds.title), ds.title, ds.created_at
from delab_moderationrating mr
    join delab_moderationcandidate2 d on mr.mod_candidate_id = d.id
    join delab_tweet dt on dt.id = d.tweet_id
    join delab_simplerequest ds on dt.simple_request_id = ds.id
where mr.u_moderating_part is not null
  and mr.u_moderating_part <> ''
group by
    ds.title, ds.created_at
order by count(ds.title) desc