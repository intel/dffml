## 2022-10-27 IETF SCITT Technical 

- https://datatracker.ietf.org/wg/scitt/about/
- https://github.com/ietf-scitt/scitt-web/blob/065ae3bf467e236d18774d954b5784d97c43ec17/_posts/2022-10-25-distributing-artifacts.md
- Zulip and Slack exists for IETF
  - Comply with appropriate legal guidance
  - Have fun creating channels an chatting otherwise
  - Do not assume privacy, this is a hosted service.
  - https://xkcd.com/1810/

![XKCD 1810: Chat Systems](https://user-images.githubusercontent.com/5950433/198354823-60c51c09-9644-4d1f-a434-9a474b2f5095.png)

- Supply chain as a network of information that travels across an ecosystem
  - Decentralization is natural in supply chains
- https://datatracker.ietf.org/meeting/upcoming
  - See below
- Example flow / bare bones model
  - When we need the software artifact it's available, it didn't change
    - Need better tooling to keep copies in sync
      - SCITT will be one of them
  - Archiving
  - Deployment logs
  - Auditing for mitigation and upgrades
- How do we make sure that we never move the cheese on customers and they can roll forward and continue to take advantages of advancements in the future
- https://github.com/ietf-scitt/use-cases/blob/main/scitt-components.md
  - More detailed view
  - We can fill this out
- ACME Rockets
  - Wabbit Networks from example can make internal information public easily
    - They might have one SCITT instance that delivers
  - They might have one SCITT instance that delivers provenance information to customers about released artifacts
- Each endpoint example: roy.azurecr.io
  - Container Registry with signing aligned (azurecr means Azure Container Registry)
  - Network boundries complicate permission models
- We need to iron out / document how to do transparent / clean replication
  - petnames spec
- Orie: How much detail is in the graph is trust...
  - John (unsaid, for the notes only): Trust is for sure not binary, but within a given context that value for the green in the trust graph might become infinitely close to 1.
- Every entity that runs a SCITT instance will have a choice of who they trust
- We want to try to give you a simple solution that

---

DRAFT SCITT Agenda, IETF 115, London, UK
Donnerstag, 10. November 2022
09:30 - 11:30	Thursday Session I
 
1. Welcome, Agenda Bashing (Chairs, 5 min)

2. Architecture (TBD, 20 min)
draft-birkholz-scitt-architecture-02

2. Software Supply Chain Uses Cases for SCITT (TBD, 30 min)
draft-birkholz-scitt-software-use-cases-00

3. Hackathon Report (TBD, 30 min)

4. SCITT Receipt Report from COSE (TBD, 20 min)

5. AOB (Open Mic) & Next Steps (Chairs, 15 min)