from dffml.repo import Repo
from dffml.base import config
from dffml.df.types import Definition
from dffml.df.base import op
from dffml.df.types import Dataflow,Input
from dffml.df.memory import MemoryOrchestrator



from typing import Dict,Any

@config
class RunDataflowOnRepoConfig:
    dataflow : Dataflow
    

@op(
    inputs={ 
        ins : Definition(name="flow_ins",primitive="Dict[str,Any]")
         },
    outputs={
        results : Defintion(name="flow_results",primitive="Dict[str,Any]")
        },
    config_cls=RunDataflowOnRepoConfig,
    expand = ["results"]
)

def run_dataflow_on_repo(self: OperationImplementationContext,ins : Dict[str,Any]) -> Dict[str,Any] :
    ins_created={}
    defintions=self.config.dataflow.definitions
    for ctx_str,val_defs in ins.items():
        _tins=[]

        ins_created[ctx_str] = [ 
                        Input(
                        value = val_def["value"],
                        defintion = definitions[ val_def["definition"] ]
                            )
                        for val_def in val_defs   
                        ]

    async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(self.config.dataflow) as octx:
                results = []
                for ctx_str,tins in ins_created.items():
                    _ , result = octx.run(*tins)
                    _results.append( {ctx_str:result} )
    

    return {"results":results}
                
                





