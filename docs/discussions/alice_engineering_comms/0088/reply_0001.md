## 2022-11-16 Portland Linux Kernel November meetup

- https://www.meetup.com/portland-linux-kernel-meetup/events/289592627/
- Talked to Andy most of the time (x86, kvm nested)
  - Asked him what he's excited about
    - He's stoked on profiling and perf counters, good stuff to be stoked on.
      - Mentioned ptrace, instruction count per cycle I think, can't quite remember.
      - Told him will circle back once we are to retriggering for regressions.
- Semantic grep
- https://www.kernel.org/doc/html/v6.0/dev-tools/coccinelle.html
  - Idea is to infer what the input to coccinelle is (figure out appropriate semantic patch)
- Gave example of three developers working on different branches in different repos.
  Yes we aren't supposed to have long lived feature branches, but if you have three
  short lived dev branches you're still here.
  - Alice works in the background constantly trying to find the "state of the art"
    for the combination of those branches.
  - Alice is always trying to ensure you're working off the context local dynamic
    state of the art, LIVE at HEAD for decentralized development.
    - Git allows your source control to be decentralized but this allows yo
      to take full advantage of that, grep A/B testing rebase cherry-pick all
      permutations (how dataflows already call operations, grep for food / recipe
      example).