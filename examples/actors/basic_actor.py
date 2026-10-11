
from satched.core import run, Orchestrator, LeafActor, OrchestratorState, Decision, LeafActorState

class DummyState(OrchestratorState):
    def __init__(self):
            super().__init__(children_state={})

class NewDummyState(OrchestratorState):
    def __init__(self):
            super().__init__(children_state={})

def my_decider(s: DummyState) -> Decision:
   return Decision(name="dummy")


run(
    Orchestrator[DummyState](
        name= "",
        decider= my_decider,
        actors=[
            LeafActor(
                name = "mult",
                activity=lambda dummyleafactorstate : dummyleafactorstate
            ),
            LeafActor(
                name = "sub",
                activity=lambda dummyleafactorstate : dummyleafactorstate
            ),
            LeafActor(
                name = "div",
                activity=lambda dummyleafactorstate : dummyleafactorstate
            ),

        ]
    )

)