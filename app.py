import streamlit as st
from chatbot import chatbot, rereieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

# utility function

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []
    add_thread(st.session_state['thread_id'])

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):

    state = chatbot.get_state(
        config = {'configurable' : {'thread_id' : thread_id}}
    )

    return state.values.get('messages', [])

#st.session is basically a dictoinory that saves previously run data

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
#    st.session_state['chat_threads'] = []
# now it check if there is a thread in database then it will consider it
# and print that, so our history is basically stored
    st.session_state['chat_threads'] = rereieve_all_threads()

add_thread(st.session_state['thread_id'])

#*****Side bar UI****

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_threads'][::]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        #we are doing this because the message loading require 'message_history'
        #and that is in a different format 
        # so we manually define the correct format
         
        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role' : role, 'content' : msg.content})
        
        st.session_state['message_history'] = temp_messages

#loding the entire conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')



if user_input:

    #firstly add the message to message_history
    st.session_state['message_history'].append({'role' : 'user', 'content' : user_input})
    with st.chat_message('user'):
        st.text(user_input)

    #now we fetch it from the llm
#    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
#
#    ai_message = response['messages'][-1].content
#
#    #first add the ai_message into message_history
#    st.session_state['message_history'].append({'role' : 'assistant', 'content' : ai_message})
#    with st.chat_message('assistant'):
#        st.text(ai_message)

    #we will now use streaming in python to smothen out our chatbot

    #we are using persistence so here we define our thread
    #    CONFIG = {'configurable' : {'thread_id' : 'thread_1'}}
#   now dynamically
    CONFIG = {'configurable' : {'thread_id' : st.session_state['thread_id']}}


    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            #so when we get stream object in return, it contains 2 components 1 is message_chunk and another is metadata,
            #and now we are iterating over these components to stream our output
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages' : [HumanMessage(content=user_input)]},
                #     config={'configurable' : {'thread_id' : 'thread-1'}},
                #dynamically 
                config = CONFIG,
                stream_mode= 'messages'
            )
        )


    st.session_state['message_history'].append({'role' : 'assistant', 'content' : ai_message})