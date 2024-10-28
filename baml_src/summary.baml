class Summary {
    title string @description("论文的英文标题")
    chinese_title string @description("论文的中文标题")
    repo string?  @description("文章的代码仓库地址")
    // core_ideas_summary string  @description("文章解析，根据论文摘要部分，概括论文核心内容 归纳主要观点 字数控制在150-200字左右 保证精炼而全面")
    core_ideas_summary string  @description("文章解析，根据论文摘要部分，翻译文章摘要，归纳主要观点, 保证精炼而全面")
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
            Liquid-Graph Time-Constant Network
for Multi-Agent Systems Control
Antonio Marino1
, Claudio Pacchierotti2
, Paolo Robuffo Giordano2
Abstract— In this paper, we propose the Liquid-Graph Timeconstant (LGTC) network, a continuous graph neural network
(GNN) model for control of multi-agent systems based on the
recent Liquid Time Constant (LTC) network. We analyse its
stability leveraging contraction analysis and propose a closedform model that preserves the model contraction rate and does
not require solving an ODE at each iteration. Compared to
discrete models like Graph Gated Neural Networks (GGNNs),
the higher expressivity of the proposed model guarantees
remarkable performance while reducing the large amount
of communicated variables normally required by GNNs. We
evaluate our model on a distributed multi-agent control case
study (flocking) taking into account variable communication
range and scalability under non-instantaneous communication.
Index Terms— Distributed Control, Graph Neural Network,
Stability Analysis
I. INTRODUCTION
Communication is a crucial element in achieving distributed solutions for multi-agent systems (MAS) from control to planning [2]. Like many distributed control algorithms, also learning-based control can benefit from interagent communication to partition the prediction process
across multiple machines contributing to task scalability and
prediction accuracy [6].
Leveraging communication, recent trends in data-driven
distributed control involve employing Graph Neural Networks (GNNs) to encode distributed control and planning
solutions. In this respect, Gama et al. [7] extend GNNs
to flocking control for large teams. Additional examples
of the use of GNNs for distributed control are found in
space coverage [8], multi-robot path planning [9], and motion
planning [10], including obstacle-rich environments [11].
GNNs also enhance multi-agent perception [12] and enable
distributed active information acquisition [13], translating
multi-robot information gathering into graph representation
and formulating GNN-based decision-making.
In the recent literature, one of the objectives is to make the
learning-based method robust and stable [14]. In this context,
many works applied contraction analysis to demonstrate
recurrent neural network stability [15], or directly closedloop stability in continuous learning [16] and adaptive control [17]. Recently, the stability analyses presented in [18],
[19] showcased the concepts of ISS (Input-to-State Stability)
1 A. Marino is with Univ Rennes, CNRS, Inria, IRISA – Rennes, France.
E-mail: antonio.marino@irisa.fr.
2 C. Pacchierotti and P. Robuffo Giordano are with CNRS, Univ Rennes,
Inria, IRISA – Rennes, France. E-mail: {claudio.pacchierotti,prg}@irisa.fr.
This work was supported by the ANR-20-CHIA-0017 project “MULTISHARED”.
and incremental ISS (δISS) [20], [21] in the context of
LSTMs and GRUs, which are two of the most popular
recurrent neural network models. Inspired by these last
results, we proposed [22] the conditions for δISS of the
recurrent version of GNN, i.e. Gated Graph Neural Networks
(GGNN) [23].
In this study, we introduce a continuous graph ordinary
differential equation (ODE) network called Liquid-Graph
Time-Constant (LGTC) network, inspired by its single-agent
counterpart, the Liquid Time Constant (LTC) network [24].
The LTC network demonstrates a strong representation learning capability, empowering agents to extrapolate and make
inferences even in unfamiliar scenarios. Additionally, its
closed-form version [25] eliminates the need to solve the
initial value problem of the ODE, a requirement in other
ODE networks [26]–[28]. In the existing literature, there are
few attempts to make graph ODEs for modelling dynamic
network systems [29], predicting traffic flow [30], or for
sequential recommendations [31]. These models typically
employ an auto-regressive network over a vector field modelled by a Graph Neural Network (GNN), initializing the
internal state with the previous layer’s output. In contrast, the
proposed LGTC aims to introduce a novel model that learns
a dynamic (or “liquid”) time constant, influenced by both
input data and the internal state communicated over the agent
graph. This dynamic time constant enables each element of
the state to capture specific dynamics, thereby enhancing the
model’s predictive capabilities. The specialized dynamics can
be used to reduce the number of the network’s internal state
(memory) and consequently the number of information each
agent needs to communicate. The final aim of this study is to
approach model-based algorithms’ communication efficiency
while increasing prediction accuracy, which in control translates into a higher distributed control efficiency.
In addition, our contribution includes proposing an approximated closed-form for the LGTC system, enhancing the
computational efficiency and reducing the communication
load. We proceed to evaluate the proposed models alongside
GGNN and GraphODE in a flocking control example.
II. PRELIMINARIES
Let G = (V, E) be an undirected graph where V =
{v1, . . . , vN } is the vertex set (representing the N agents
in the group) and E ⊆ V × V is the edge set. Each edge
ek = (i, j) ∈ E is associated with a weight wij ≥ 0 such
that wij > 0 if the agent i and j can interact and wij = 0
otherwise. As usual, we denote with Ni = {j ∈ V| wij > 0}
the set of neighbors of agent i. We also let A ∈ R
N×N
arXiv:2404.13982v2 [cs.MA] 4 Sep 2024
be the adjacency matrix with entries given by the weights
w
P
ij . Defining the degree matrix D = diag(di) with di =
j∈Ni
wij , the Laplacian matrix of the graph is L = D−A.
The graph signal x ∈ R
N , whose i-component xi
is
assigned to agent i, can be processed over the network by
the following linear combination rule applied by each agent
six =
X
j∈Ni
sji(xi − xj ), (1)
where si
is the i-th row of S. The signal manipulation can
be operated by means of any graph shift operator S ⊆
S, e.g., Laplacian, adjacency matrix, weighted Laplacian ,
which respects the sparsity pattern of the graph. Later, in
Sect. V, we will use the Laplacian as support matrix, as it is
commonly used in distributed control. However, the proposed
techniques do not assume the use of a specific support matrix.
Performing k repeated applications of S on the same signal
represents the aggregation of the k-hop neighbourhood information. In analogy with traditional signal processing, this
property can be used to define a linear graph filtering [32]
that processes the multi features signal x ∈ R
N×G with G
features:
HS(x) = XK
k=0
S
kxHk (2)
where the weights Hk ∈ R
G×F define the output of the
filter. Note that S
k = S(S
k−1
), so that it can be computed locally with repeated 1-hop communications between
a node and its neighbors. Hence, the computation of HS is
distributed on each node.
A. Graph Neural Network
Although HS is simple to evaluate, it can only represent
a linear mapping between input and output filters. GNNs
increase the expressiveness of the linear graph filters by
means of pointwise nonlinearities ρ : R
N×Fl−1 → R
N×Fl−1
following a filter bank. Letting HSl be a bank of Fl−1 × Fl
filters at layer l, the GNN layer is defined as
xl = ρ(HSl(xl−1)), xl−1 ∈ R
N×Fl−1
. (3)
Starting by l = 0 with F0, the signal tensor xln ∈ R
N×Fln
is the output of a cascade of ln GNN layers. This specific
type of GNN is commonly referred to as a convolution
graph network because each layer utilizes a graph signal
convolution (2). By the use of imitation learning or similar
techniques, the GNN can learn a distributed policy by finding
the optimal filter weights Hk to propagate information
among the agents and generate the desired output. Notably,
each agent employs an identical version of the network and
exchanges intermediate quantities with the other agents in the
network through the application of S, resulting in an overall
distributed neural network. GNNs inherit some interesting
properties from graph filters, such as permutational equivariance [33] and their local and distributed nature, showing
superior ability to process graph signals [9], [13], [34].
B. Gated Graph Neural Network
Recurrent models of GNNs can solve time-dependent
problems. These models, similarly to recurrent neural networks (RNNs), are known as graph recurrent neural networks
(GRNNs). GRNNs utilize memory to learn patterns in data
sequences, where the data is spatially encoded within graphs,
regardless of the team size of the agents [35]. However,
traditional GRNNs encounter challenges such as vanishing
gradients, which are also found in RNNs. Additionally, they
face difficulties in handling long sequences in space, where
certain nodes or paths within the graph might be assigned
more importance than others in long-range exchanges, causing imbalances in the graph’s informational encoding.
Forgetting factors can be applied to mitigate this problem,
reducing the influence of past or new signal on the state. A
Gated Graph Neural Network (GGNN) [23] is a recurrent
Graph Neural Network that uses a gating mechanism to
control how the past information influences the update of the
GNN states. We can add a state and an input gates, qˆ, q˜ ∈
Q ⊆ [0, 1]N×F , that are multiplied via the Hadamard product ◦ by the state and the inputs of the network, respectively.
These two gates regulate how much the past information
and the input are used to update the network’s internal state.
GGNNs admit the following state-space representation [36],



q˜ = σ(A˜S(x) + B˜S(u) + ˆb)
qˆ = σ(AˆS(x) + BˆS(u) + ˜b)
x
+ = σc(qˆ◦ AS(x) + q˜◦ BS(u) + b)
(4)
with σ(x) = 1
1+e−x being the logistic function, and σc(x) =
e
x−e
−x
e
x+e−x being the hyperbolic tangent. Aˆ
S, Bˆ
S are graph
filters of the forgetting gate, A˜
S, B˜
S are graph filters (2) of
the input gate, and AS and BS are the state graph filters (2).
ˆb,˜b, b ∈ R
N×F are respectively the biases of the gates and
the state built as 1N ⊗b with the same bias for every agents.
We consider the system under the following assumption
Assumption 1. The input u is unity-bounded: u ∈ U ⊆
[−1, 1]N×G , i.e. ||u||∞ ≤ 1.
We identify the induced ∞-norm as || · ||∞. We used the
following notation for the filters in the system (4):
SI,K ≜ [I, S, . . . , SK]
A0,K ≜ [A0, . . . , AK]
T B0,K ≜ [B0, . . . , BK]
T
A˜0,K ≜ [A˜0, . . . , A˜K]
T Aˆ0,K ≜ [Aˆ0, . . . , AˆK]
T
B˜0,K ≜ [B˜0, . . . , B˜K]
T Bˆ0,K ≜ [Bˆ0, . . . , BˆK]
T
(5)
where K is the filters length. Then, in light of assumption 1
and knowing that ||x||∞ ≤ 1, each gate feature qi satisfies:
|qˆi| ≤ σ(||SI,K||∞(||Aˆ0,K||∞ + ||Bˆ0,K||∞) + ||bˆ||∞) ≜ σqˆ.
(6)
Assumption 2. Given any two support matrices ||S1(t)||∞
and ||S2(t)||∞, ∀t ∈ R
+ associated with two different
graphs, they are bounded by the same ||S¯||∞; moreover, they
are lower bounded by ||S˜||∞.
In our previous work [22], we derived the following stability
condition

        "#
    }
}