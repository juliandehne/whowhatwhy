""" This data structure was copied from: https://towardsdatascience.com/mining-replies-to-tweets-a-walkthrough-9a936602c4d6.
    It encapsulates the replies to a tweet
"""


class TreeNode:
    def __init__(self, data):
        """data is a tweet's json object"""
        self.data = data
        self.children = []

    def id(self):
        """a node is identified by its author"""
        return self.data['author_id']

    def reply_to(self):
        """the reply-to user is the parent of the node"""
        return self.data['in_reply_to_user_id']

    def find_parent_of(self, node):
        """append a node to the children of it's reply-to user"""
        if node.reply_to() == self.id():
            self.children.append(node)
            return True
        for child in self.children:
            if child.find_parent_of(node):
                return True
        return False

    def print_tree(self, level):
        """level 0 is the root node, then incremented for subsequent generations"""
        print(f'{level*"_"}{level}: {self.data}')
        level += 1
        for child in self.children:
            child.print_tree(level)

    def list_l1(self):
        conv_id = []
        child_id = []
        text = []
        # print(self.data['id'])
        for child in self.children:
            conv_id.append(self.data['id'])
            child_id.append(child.data['id'])
            text.append(child.data['text'])
        return conv_id, child_id, text

    def flat_size(self):
        children_size = 0
        for child in self.children:
            children_size += child.flat_size()
        return 1 + children_size

    def save_to_db(self):
        # TODO implement
        pass