class Summary {
    title string @description("论文的英文标题")
    repo string?  @description("文章的代码仓库地址")
    core_ideas_summary string  @description("文章解析，概括论文核心内容 归纳主要观点 字数控制在100字左右 保证精炼而全面")
    innovations string[] @description("创新点，每条一句话")
    methodology string[] @description("研究方法，每条一句话")
    conclusions string[] @description("研究结论，每条一句话")
}

function SummaryPaper(paperContent: string) -> Summary {
    client AFallbackClient
    prompt #"
        基于这里提供的论文内容，输出内容，使用中文:
        {{paperContent}}

        {{ ctx.output_format }}
    "#
}

test AQuantumPaper {
    functions [SummaryPaper]
    args {
        paperContent #"
            The Rise of Quantum Internet Computing
Seng W. Loke, Member, IEEE
Abstract—This article highlights quantum Internet computing as referring to distributed quantum computing over the quantum Internet, analogous to (classical) Internet computing involving (classical) distributed computing over the (classical) Internet. Relevant to quantum Internet computing would be areas of study such as quantum protocols for distributed nodes using quantum information for computations, quantum cloud computing, delegated verifiable blind or private computing, non-local gates, and distributed quantum applications, over Internet-scale distances.
Index Terms—quantum Internet computing, quantum Internet, distributed quantum computing, Internet computing, distributed systems, Internet
”This work has been submitted to the IEEE for possible publication. Copyright may be transferred without notice, after which this version may no longer be accessible.”
1 INTRODUCTION
THERE have been tremendous developments in quantum computing, quantum cryptography, quantum commu- nications and the quantum Internet, and we have seen increased investments and intensive research in quantum computing in recent years [1], [2]. The quantum Internet will not necessarily replace the (classical) Internet we know and use today, at least not in the near future, but can complement the current Internet. The quantum Internet aims to enable robust quantum teleportation (or transmission) of qubits,1 and entanglement among qubits,2 over long Internet-scale distances, which are key to many of the quantum protocols including quantum key distribution, quantum voting, and others, as well as for non-local control of quantum gates.
There have been efforts to build quantum computers, and it remains to see if any one paradigm becomes the dominant or best way of building such quantum comput- ers. At the same time, even as researchers develop more powerful quantum computers (supporting more qubits for operations, and at lower error rates), there is an opportunity for connecting multiple quantum computers from differ- ent sites to achieve much more complex quantum com- putations, i.e., inter-linking multiple quantum computers on different sites to perform distributed computing with a distributed system of quantum computers (or quantum processing units (QPUs) at different nodes), arriving at the notion of distributed quantum computing, e.g., [3].
While distributed quantum computing can involve mul- tiple QPUs next to each other or at the same site, with the quantum Internet, one can envision distributed quantum
• Seng W. Loke is with the School of Information Technology, Deakin University, Melbourne, Australia.
E-mail: see https://www.deakin.edu.au/about-deakin/people/seng-loke.
Manuscript received X XX, 20XX; revised X XX, 20XX.
1. A qubit is the basic unit of quantum information, and can be thought of as a two-state, or two-levelled, quantum-mechanical system, such as an electron’s spin, where the two levels are spin up and spin down, or a photon’s polarization, where the two states are the vertical polarization and the horizontal polarization.
2. Multiple qubits at different sites can share an entangled state, a superpositon of “specially correlated” states, to be used in distributed algorithms.
computing over nodes geographically far apart. As noted in [4], the idea is the quantum Internet as the “underly- ing infrastructure of the Distributed Quantum Computing ecosystem.”
This article highlights the emerging area of distributed quantum computing over the quantum Internet, which we refer to as quantum Internet computing, i.e., the idea of com- puting using quantumly connected distributed quantum computers over Internet-scale distances. Hence, quantum Internet computing is not a new concept in itself but a proposed “umbrella term” used here for the collection of topics (listed below), from an analogy to (classical) Internet computing.
Internet computing, where one does distributed comput- ing but over Internet-scale distances and distributed sys- tems involve nodes connected via the Internet, is at the inter- section of work in (classical) distributed computing and the (classical) Internet. Analogous to Internet computing, one could ask the question of what would be at the intersection of work in distributed quantum computing and work on the quantum Internet, which brings us to the notion of quantum Internet computing.
Also, while the quantum Internet and distributed quan- tum computing are still nascent research areas, there are at least three key topics which can be considered as relevant to quantum Internet computing:
• distributed quantum computing, including quantum protocols from theoretical perspectives involving communication complexity studies, and distributed quantum computing via non-local or distributed quantum gates,
• quantum cloud computing with a focus on delegat- ing quantum computations, blind quantum comput- ing, and verifying delegated quantum computations, and
• computations and algorithms for the quantum Inter- net including key ideas such as quantum entangle- ment distillation, entanglement swapping, quantum
✦
  arXiv:2208.00733v1 [cs.ET] 1 Aug 2022
 
IEEE IOT MAGAZINE, VOL. XX, NO. X, X 2022
2
repeaters, and quantum Internet standards.3
We briefly discuss the above topics in the following sections.

        "#
    }
}