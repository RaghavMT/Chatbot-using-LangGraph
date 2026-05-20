import streamlit as st
from chatbot import chatbot
from langchain_core.messages import HumanMessage

#we are using persistence so here we define our thread
CONFIG = {'configurable' : {'thread_id' : 'thread-1'}}

#st.session is basically a dictoinory that saves previously run data
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

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
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            #so when we get stream object in return, it contains 2 components 1 is message_chunk and another is metadata,
            #and now we are iterating over these components to stream our output
            message.chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages' : [HumanMessage(content=user_input)]},
                config={'configurable' : {'thread_id' : 'thread-1'}},
                stream_mode= 'messages'
            )
        )