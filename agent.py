class GAIAAgent:
    
    def __init__(self):
        from graph import graph
        self.agent = graph

    def __call__(self, question: str) -> str:
        print(f"Agent received question (first 50 chars): {question[:50]}...")
        messages = [ ("user" , question) ]
        response = self.agent.invoke( {"messages": messages} )
        answer = response["messages"][-1].content
        print(f"Agent returning fixed answer: {answer}")
        return answer