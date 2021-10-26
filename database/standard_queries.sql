SELECT conversation_id, title from delab_tweet tw join delab_twtopic dt on tw.topic_id = dt.id where conversation_id = 1446238908501700616

Update delab_tweet set conversation_flow_id = NULL

DELETE from delab_conversationflow