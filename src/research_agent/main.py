from dotenv import load_dotenv

load_dotenv()

from crewai.crews.crew_output import CrewOutput

from research_agent.crews.research_crew import ResearchCrew


def main() -> None:
    topic = (
        "Research the current state of humanoid robotics, identify the leading "
        "companies, analyse the technologies they're developing, and produce a "
        "report on future opportunities."
    )

    test_topic = "What is Retrieval Augmented Generation and who are the main vendors"

    result = ResearchCrew().crew().kickoff(inputs={"topic": test_topic})

    if not isinstance(result, CrewOutput):
        raise TypeError("Expected CrewOutput; is streaming enabled on the crew?")

    print(result.raw)


if __name__ == "__main__":
    main()
