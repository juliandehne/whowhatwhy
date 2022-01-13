import logging

logger = logging.getLogger(__name__)


class TreeNode:
    def __init__(self, data, tree_id, parent_id=None):
        """data is a tweet's json object
           tree_id is the logical id of the treenode (either author id when downloading, or twitter id in db)
           parent references the tree_id of the parent
        """
        self.tree_id = tree_id
        self.data = data
        self.children = []
        self.max_path_length = 0
        self.parent_id = parent_id

    def find_parent_of(self, node, recurson_counter=0):
        """append a node to the children of it's reply-to user"""
        if recurson_counter > 1000:
            logger.error("got into a recursion with more then 1000 steps for conversation {}".format(self.data))
            return False
        else:
            if node.parent_id == self.tree_id:
                self.children.append(node)
                return True
            else:
                for child in self.children:
                    result = child.find_parent_of(node, recurson_counter=recurson_counter + 1)
                    if result:
                        return result
        return False

    def print_tree(self, level):
        """level 0 is the root node, then incremented for subsequent generations"""
        print(f'{level * "_"}{level}: {self.data}')
        level += 1
        for child in self.children:
            child.print_tree(level)

    def to_string(self, level=0):
        result = ""
        if level == 0:
            result += "Conversation: " + str(self.data["conversation_id"]) + "\n\n"
        result += (level * "\t") + self.data_to_string(level)
        for child in self.children:
            result += child.to_string(level + 1)
        return result

    def data_to_string(self, level):
        text = self.data["text"].split(".")
        tabbed_text = []
        for sentence in text:
            sentence = sentence.replace('\n', ' ').replace('\r', '')
            tabbed_sentence = ""
            if len(sentence) > 125:
                tabbed_sentence += sentence[0:125]
                tabbed_sentence += "\n" + (level * "\t")
                tabbed_sentence += sentence[125:]
            else:
                tabbed_sentence = sentence
            tabbed_text.append(tabbed_sentence)
        separator = ".\n" + (level * "\t")
        tabbed_text = "\n" + (level * "\t") + separator.join(tabbed_text)
        return str(self.data.get("tw_author__name", "namenotgiven")) + "/" + str(
            self.data.get("tw_author__location", "locationnotgiven")) + "/" + str(
            self.data["author_id"]) + ":" + tabbed_text + "\n\n"

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

    def all_tweet_ids(self):
        result = [self.tree_id]
        for child in self.children:
            result.append(child.tree_id)
        return result
