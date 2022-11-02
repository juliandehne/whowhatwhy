def run():
    example_conversation_id = 1508854754050457608
    # %%
    from delab.network.conversation_network import get_nx_conversation_graph

    # simple case 1 merge
    merged, todelete, tochance  = get_nx_conversation_graph(example_conversation_id, merge_subsequent=True)
    not_merged = get_nx_conversation_graph(example_conversation_id)
    assert len(not_merged.nodes) > len(merged.nodes)

    # simple case 2 no merge
    example_conversation_id = 1526082959505244162
    merged, todelete, tochance = get_nx_conversation_graph(example_conversation_id, merge_subsequent=True)
    not_merged = get_nx_conversation_graph(example_conversation_id)
    assert len(not_merged.nodes) > len(merged.nodes)


