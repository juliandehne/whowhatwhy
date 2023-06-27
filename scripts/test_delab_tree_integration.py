from delab_trees.test_data_manager import get_example_conversation_tree
from gpt4all import GPT4All

def run():
    # tree = get_example_conversation_tree()
    # print(tree.to_string())

    gptj = GPT4All("ggml-gpt4all-j-v1.3-groovy")

    prompt = "Write a statement, telling someone to control their emotion in a discussion!"
    message_1 = "Happy International Day against Homophobia,Transphobia and Biphobia!"
    message_2 = "wow! the fags are getting really creative with their days!"
    message_3 = "for real"
    message_4 = "if you dont want to celebrate it, thats fine"
    message_5 = "why are dykes always telling everyone they are dykes? i really dont care!"
    message_7 = "when did they say they were a lesbian?:D "
    messages_text = [message_1, message_2, message_3, message_4, message_5, message_7]
    message_prompt = "Answer this conversation!\nb:"
    messages = [{"role": "user", "content": prompt}]
    gptj.chat_completion(messages)

    prompt2 = "Adapt the previous statement to react to the message: " + message_5
    messages = [{"role": "user", "content": prompt2}]
    gptj.chat_completion(messages)
