# coding=utf-8

from pepper.brain.fame_aware import FameAwareMemory

if __name__ == "__main__":

    # Create brain connection
    brain = FameAwareMemory(address="http://localhost:7200/repositories/famous")

    people = ["Máxima of the Netherlands", "Brexit"]

    for elem in people:
        x = brain.lookup_person_wikidata(elem)
