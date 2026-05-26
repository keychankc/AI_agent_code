from chain.research_chain import web_research_chain


def generate_complete_research_report():
    question = {
        "user_question": "杭州有哪些值得一去的地方？"
    }
    report = web_research_chain.invoke(question)
    print(report)



if __name__ == '__main__':
    generate_complete_research_report()
