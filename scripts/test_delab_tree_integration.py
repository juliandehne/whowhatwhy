from delab_trees.test_data_manager import get_example_conversation_tree


def run():
    tree = get_example_conversation_tree()
    print(tree.to_string())
