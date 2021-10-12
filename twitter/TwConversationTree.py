""" This data structure was copied from: https://towardsdatascience.com/mining-replies-to-tweets-a-walkthrough-9a936602c4d6.
    It encapsulates the replies to a tweet

    Eventually this should be merged with:
    https://github.com/fabiocaccamo/django-treenode
"""


class TreeNode:
    def __init__(self, data):
        """data is a tweet's json object"""
        self.data = data
        self.children = []
        self.max_path_length = 0

    def id(self):
        """a node is identified by its author"""
        return self.data['author_id']

    def tweet_id(self):
        return self.data["id"]

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
        print(f'{level * "_"}{level}: {self.data}')
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

    def compute_max_path_length(self, level=0):
        # print(level)
        if len(self.children) > 0:
            child_max_paths = []
            for child in self.children:
                # print(["child"]*level)
                child_max_paths.append(child.compute_max_path_length(level + 1))
            return max(child_max_paths)
        return level

    def get_max_path_length(self):
        # print("hello julian")
        if self.max_path_length == 0:
            self.max_path_length = self.compute_max_path_length()
        return self.max_path_length

    def crop_orphans(self, max_orphan_count=4):
        favourite_children = []
        if len(self.children) > 0:
            counter = 0
            for child in self.children:
                if len(child.children) > 0 and counter < max_orphan_count:
                    favourite_children.append(child)
                    counter += 1
                    child.crop_orphans(max_orphan_count)
        self.children = favourite_children
