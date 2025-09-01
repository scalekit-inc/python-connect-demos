from langchain_core.prompts import SystemMessagePromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate,PromptTemplate, ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template="You are a helpful assistant. Use tools if needed.")),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=["input"], template="{input}")),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])
