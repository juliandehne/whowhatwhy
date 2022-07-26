
delete from delab_tweet b where b.conversation_id in (select conversation_id from
    (select distinct (a.conversation_id), count(a.text) as c from delab_tweet a
        group by a.conversation_id having count(a.text) < 10) as pairs);


