- [ ] Run dataflow, collect usage statistics when running locally or k8s for CPU, memory, etc. Build model to predict how much CPU or memory is needed, check if cluster has enough before warn if orchestrator predicts using built model that number of context executing will exceed resource constraints based on historical estimated usage.
  - Example target of 30,000 execution per day. Set up an
    experiment to make sure that works. Try doubling that number and see how
    the system responds. This is how we make sure that the execution assets at our disposal
    meets our needs on speed of thought (or validation?). 10-25 min per execution.
    Round-estimate to 18 minute average. 30,000 * 18 = 1,080,000 minutes
    divided by 60 minutes to the hour = 18,000 hours / 24 hours in a day =
    750 parallel system context executions active on average throughout the day.
- [ ] How would we write a decorator to cache operations which do API calls which are ratelimited?