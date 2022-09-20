

update delab_tweet b set conversation_id = tn_parent_id where b.tn_parent_id in (select conversation_id from
    (select distinct (a.conversation_id), count(a.text) as c from delab_tweet a
        group by a.conversation_id having count(a.text) < 10000) as tobefiltered);

update delab_tweet c
set conversation_id = p.conversation_id
from delab_tweet p
    where c.tn_parent_id = p.twitter_id and c.conversation_id != p.conversation_id