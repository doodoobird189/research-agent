from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

load_dotenv()

search_tool = SerperDevTool()

researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover accurate, up-to-date facts and key developments on {topic}",
    backstory=(
        "You are an experienced researcher who verifies claims, tracks sources, and organises raw findings into clear notes."
    ),
    tools=[search_tool],
    verbose=True,
)

analyst = Agent(
    role="Reporting Analyst",
    goal="Synthesise research findings into a clear structured report on {topic}",
    backstory="You turn detailed research notes into concise, accurate summaries with actionable takeaways.",
    verbose=True,
)

research_task = Task(
    description=(
        "Research {topic}. Gather key facts, recent developments, and notable examples using web search."
    ),
    expected_output="Structured research notes with key facts and source URLs.",
    agent=researcher,
)

report_task = Task(
    description=(
        "Write a well-structured Markdown report on {topic} based strictly on the research notes provided."
    ),
    expected_output="A clean Markdown report with headings and bullet points.",
    output_file="report.md",
    agent=analyst,
)

crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, report_task],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    topic = input("Enter the topic you would like to research: ")
    result = crew.kickoff(inputs={"topic": topic})
    print(result)
