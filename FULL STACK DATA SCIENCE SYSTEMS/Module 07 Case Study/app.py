import os
import openai
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_KEY")

start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: "
# prompt = "Consider yourself an experienced blogger with extensive tourism experience. Generate a blog on Spanish tour. Suggest some eateries and fun places to visit."
#### Davinci-003 - GPT 3 model
def openai_3(prompt):

    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    temperature=0,
    max_tokens=2000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.6,
    stop=[" Human:", " AI:"]
    )

    print(response)

    return response.choices[0].text



# GPT 3.5 model
# def openai_35(prompt):
#     response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant that converses with the user."},
#         {"role": "user", "content": f"{prompt}"}
#     ],
#     temperature=0,
#     max_tokens=500,
#     top_p=1,
#     frequency_penalty=0,
#     presence_penalty=0.6,
#     stop=[" Human:", " AI:"]
#     )

#     print(f"User Query: {prompt}")

#     print(response)

#     return response.choices[0].message['content']


# GPT 4 model
# def openai_4(prompt):
#     response = openai.ChatCompletion.create(
#     model="gpt-4",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant that converses with the user."},
#         {"role": "user", "content": f"{prompt}"}
#     ],
#     temperature=0,
#     max_tokens=500,
#     top_p=1,
#     frequency_penalty=0,
#     presence_penalty=0.6,
#     stop=[" Human:", " AI:"]
#     )

#     print(f"User Query: {prompt}")

#     print(response)

#     return response.choices[0].message['content']

def chatgpt_clone(input, history):
    history = history or []
    s = list(sum(history, ()))
    s.append(input)
    inp = ' '.join(s)
    output = openai_3(inp)
    print(f"Bot: {output}")
    history.append((input, output))
    return history, history

with gr.Blocks() as demo:
    gr.Markdown("""<h1><center>Ask Me Anything (AMA)</center></h1>
    """)
    chatbot = gr.Chatbot()
    message = gr.Textbox(placeholder=prompt)
    state = gr.State()
    submit = gr.Button("SEND")
    submit.click(chatgpt_clone, inputs=[message, state], outputs=[chatbot, state])

# demo.launch(debug=True) # development
demo.launch(server_name="0.0.0.0", share=False) # production