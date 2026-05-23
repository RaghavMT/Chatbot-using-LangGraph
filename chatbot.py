from langgraph.graph import StateGraph, START, END
from langchain_pollinations import ChatPollinations
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage
from dotenv import load_dotenv
import os
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    #here we use add_message instead of operator.add as a reducer because add_message is more optimized specially for base messages
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatPollinations(
    model = "nova-fast",
    temperature = 0,
    api_key = os.getenv("POLLINATIONS_API_KEY")
)


def chat_node(state: ChatState):

    #we take the query from the user
    messages = state['messages']

    #send it to llm
    response = llm.invoke(messages)

    #store the response
    #we pass it in a list because we have defined messages as a list in our chatstate
    #and we defined messages as list becuase we want to keep adding new messages in it
    return {'messages' : [response]}

#this is something that will help our chatbot to remember past things in RAM
#checkpointer = InMemorySaver()

#now we do it in sqlite
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)


#this is our main graph
graph = StateGraph(ChatState)

#adding nodes
graph.add_node('chat_node', chat_node)

#adding edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)


#thread is something while tells the chatbot which person's context are we talking about
#so thread is basically a person 
#and there can be multiple person so each thread id represents a person

# thread_id = '1' 


#the part after this wont be needed when we are using frontend on streamlit,
#this is for the terminal part only

#    while True:
 #       
  #      user_message = input('Type Here: ')
#
 #       if user_message.lower() in ['quit', 'exit', 'end', 'bye']:
  #          break
#
 #       config = {'configurable': {'thread_id' : thread_id}}
#
 #       
    #    response = chatbot.invoke({'messages': [HumanMessage(content= user_message)]}, config=config)

    #    print('AI:' , response['messages'][-1].content)
        
        #trying to implement it using streaming
  #      full_response = ""
#
 #       for message_chunk, metadata in chatbot.stream(
  #          {'messages':[HumanMessage(content=user_message)]},
   #         config={'configurable' : {'thread_id' : 'thread_1'}},
    #        stream_mode='messages'
     #   ):
#
 #           chunk = message_chunk.content
#
 #           if chunk:
  #              print(chunk, end=" ", flush = True)
   #             full_response += chunk
    #    
     #   print("\n")


#now we are trying using sqlite
