Notes from work in progress tutorial:

We need to come up with serveral metrics to track and plot throughout.
We also need to plot in relation to other metrics for tradeoff analysis.

We could also make this like a choose your own adventure style tutorial,
if you want to do it with threads, here's your output metrics. We can
later show that we're getting these metrics by putting all the steps
into a dataflow and getting the metrics out by running them. We could then
show how we can ask the orchestrator to optimize for speed, memory, etc.
Then add in how you can have the orchestrator take those optimization
constriants from dynamic conditions such as how much memory is on the
machine you are running on, or do you have access to a k8s cluster. Also
talked about power consumption vs. speed trade off for server vs. desktop.
Could add in edge constraints like network latency.

Will need to add in metrics API and use in various places in
orchestrators and expose to operations to report out. This will be the
same APIs we'll use for stub operations to estimate time to completion,
etc.

- Make sure to measure speed and memory useage with ProcessPoolExecutor
  ThreadPoolExecutor. Make sure we take into accout memory from all
  processes.

- Start to finish speed

  - Plot with number of requests made

- Memory consumed

  - Plot with number of requests made

This could be done as an IPython notebook.

- Show basic downloader code

  - Observe speed bottleneck due to download in series

- Parallelize download code

  - Observe increase in speed

  - Observe error handling issues

- Add in need to call out via subprocess

  - Observe subprocess issues

- Move to event loop

  - Observe increase in speed (? Not sure on this yet)

  - Observe successful error handling

  - Observe need to track fine grained details

- Move to event based implemention with director (orchestrator, this file
  minus prev pointers in Base Event)

  - Observe visablity into each event state of each request

  - Observe lack of visablity into chain of events

- Add prev pointers

  - Open Liniage

- Move to data flow based implemention

- Demo full DFFML data flow using execution on k8s

  - Use k8s playground as target environment