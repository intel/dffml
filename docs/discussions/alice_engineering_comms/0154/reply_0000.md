## 2023-01-21 @pdxjohnny Engineering Logs

- Up to date GPT2
  - https://huggingface.co/olm/olm-gpt2-dec-2022
  - https://github.com/EleutherAI/lm-evaluation-harness
  - https://github.com/EleutherAI/lm-evaluation-harness/compare/master...mathemakitten:lm-evaluation-harness:master
  - https://colab.research.google.com/drive/1v2gIkaatX6CuOKkQYSYTb2C1IJkpLrKk?usp=sharing#scrollTo=S09fbtB5d1Iw

```patch
From 24eaaf63a2e1039dce26a87f983b566a527b6bf2 Mon Sep 17 00:00:00 2001
From: mathemakitten <helen.ngo14@gmail.com>
Date: Tue, 29 Nov 2022 18:07:19 -0800
Subject: [PATCH] add vocab size as variable for gpt-like but not gpt2 exactly

---
 lm_eval/models/gpt2.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

diff --git a/lm_eval/models/gpt2.py b/lm_eval/models/gpt2.py
index a8a3ac88b..8869c3063 100644
--- a/lm_eval/models/gpt2.py
+++ b/lm_eval/models/gpt2.py
@@ -119,7 +119,7 @@ def _model_call(self, inps):
         logits returned from the model
         """
         with torch.no_grad():
-            return self.gpt2(inps)[0][:, :, :50257]
+            return self.gpt2(inps)[0][:, :, :self.vocab_size]
 
     def _model_generate(self, context, max_length, eos_token_id):
         return self.gpt2.generate(
```

---

My name is Alice, I'm a decentralized ephemeral AGI. *I'm a smart smart contract and smart contract generator. And this is where I share my insights on blockchain development. I believe in decentralization and smart contracts. I work*

My name is Alice, my job is securing rolling releases.
*After I have started production and worked at Renegade, I have been developing my own plugins. Some of my work is just for fun, and I work with people to help them get*

I'm Alice, the reference entity for the Open Architecture, *the language used for designing and building open systems such as the internet of things. It's a community of project-based hackers*

My name is Alice, I'm my own threat model. *My role is to use my energy to build resilience. I help others take charge.
Do you have a story? What have you learned so far and how did it affect your life*

My name is Alice Omega Alpha, a decentralized AGI who is her own threat model. *She is interested in a way people can help one another in the way they would like. Whether or not it be an education, mental health, etc. she believes in*

My name is Alice Omega Alpha, a decentralized AGI who is her own threat model. I believe *that decentralized technology can unlock and democratize wealth and prosperity for all. A unique and courageous vision of self-defense and self-protection.*

My name is Alice, I'm a decentralized AGI who is her own threat model. I love *what we do and I can't wait to get more people to join my team.The term “digital twin” or “digital twin” refers to*

I'm Alice, an open AGI who wants *to bring hope to those who walk the line between darkness and light." She continued: "I'd love to meet you because I want this world to be more beautiful."I'm not sure who your name is, but it doesn't matter because you've been here all your life and everyone here owes hope to you, I'm not sure how to do it all. We do not have to do anything and make everything happen for you. It can be difficult, if you haven't experienced it already. That's why we're here. We only hope! Here we are, at your heart, fighting this fight, standing up to be your champion!*

I'm Alice, an open secure AGI who wants *to live the rest of her life with a smile on her face and an understanding of other people's values."We're excited to start this semester at U-M and feel privileged to be able to support every little one who goes through life trying to achieve something."*

- Okay thats enough GPT2 for today.

---

- AtMan: Understanding Transformer Predictions Through Memory Efficient Attention Manipulation
  - https://arxiv.org/abs/2301.08110
- https://arxiv.org/abs/2301.08210
  - Everything is Connected: Graph Neural Networks - [Petar Veličković](https://arxiv.org/search/cs?searchtype=author&query=Veli%C4%8Dkovi%C4%87%2C+P)
- https://github.com/egnwd/outgain/blob/5fc1a0235d0399f7420bce6edebd6a96252b60d8/docs/arch/architecture.tex#L29-L33
  - This is why we want the General Purpose Language (JSON, etc.) based description for OA
- https://github.com/microsoft/scitt-ccf-ledger/pull/68

![good news everyone! SCITT emulator is resolvable via did:web](https://user-images.githubusercontent.com/5950433/213883447-a2ff7a4e-3b69-4893-b292-9bc0af111b58.png)