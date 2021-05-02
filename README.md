## Purpose
This project has been implemented for two reasons:
1. to create a tool for effective study of classic CS algorithms via
  'spaced repetition' and 'active recall' techniques
1. to implement a project following Martin Robert's guidelines in his
  book 'Clean Architecture'.
  
Why a spaced repetition tool to study algorithms? There is lot's of literature
describing the theory behind algorithms and lots of sources that allow
solving algorithmic problems. However, it is easy to get carried away, solving
problems at random and forgetting learned information over time.
This program should:
* allow to define relevant algorithmic topics with arbitrary granularity, open to modification
* allow to define problems whose optimal solution represents an application of one
  of the relevant algorithmic topics
* quantify the knowledge status per algorithmic topic
* help to reach the desired knowledge status per topic with maximum efficiency
  (through spaced repetition and active recall techniques)

This is an experimental project and implements a minimalist
solution -> you are welcome to use it with care :-).

## Setup
* clone the repository
* create a virtual environment, e.g.: `python3 -m venv <your_env_name>`
* activate the environment: `source <path_to_venv>/bin/activate`
* install: `pip install -e <path_to_cloned_repo>`

Run the CLI with the '-h' flag to see possible actions:
`srep -h`

## Usage
When studying algorithmic problems, the goal is not to
commit solutions to individual problems to memory. Instead, we want to
learn and remember key algorithms and their applications, to eventually
be able to solve any problem. This is a key difference to existing apps
that implement spaced repetition algorithms (such as
[anki](https://www.ankiapp.com/) or
[supermemo](https://www.supermemo.com/de/apps)).

Therefore, the intended purpose of this program is **to track and help
us refresh the knowledge of key algorithms**. This means: the program
tracks how well we know an algorithmic topic by tracking how well we
solve problems related to that topic, where each problem should represent a
relevant application case of the related algorithm. The program then calculates
when we should re-solve the same problem to get to and maintain the desired
algorithmic knowledge level.

To use this program, the user can either start by adding relevant algorithmic
topics to the database (see below), or by starting solving problems related to
the algorithms of interest. When encountering a problem that is
somewhat representative of an application for a relevant algorithm,
this problem should be added to the 'spaced-repetition' database
via `srep add-problem`.

The corresponding dialogue will ask to link the problem to at least one
'tag', representative of an algorithmic topic, e.g. 'depth-first-search'.
A problem should
be linked to exactly those algorithms that solve this problem optimally in
some way. There can be several optimal algorithms, that may each have some
trade-offs (e.g. optimal time or space complexity). Non-optimal algorithms
should not be linked, otherwise the program will schedule repetitions of the
non-optimal solution.<br>
Tags need to exist in the database before a problem can
be linked to them. Create a tag via:
`srep add-tag`.

Every attempt at solving a tracked problem should be logged by creating a
ProblemLog:
`srep add-log`.  
The corresponding dialogue asks to grade how well the problem
was solved on a provided scale, and via which algorithm(s) /
tag(s) the problem has been solved. Only algorithms linked to the problem
(i.e. optimal ones) may be selected. However, each ProblemLog also has an optional
'comment' field, in which the user could describe non-optimal solutions.
From these execution logs, the underlying algorithm calculates:

* a 'knowledge score' per problem-tag combination (representing an application
  case of the linked algorithm). List all knowledge scores via:<br>
  `srep list-full`
* an overview of the aggregated knowledge level per problem:<br>
  `srep list-problems`
* an overview of the aggregated knowledge level per tag (i.e. algorithm):<br>
  `srep list-tags`
  
Any of these overviews can be used to find the topic, problem or problem-topic
combination with the
highest priority to study (= lowest knowledge).


## How it works
This section sketches spaced-repetition's underlying priorization algorithm.

### Tags (= algorithmic topics)
Tags represent algorithmic topics, the knowledge per tag is rated on a scale
from 0 (high need to catch up) to 5 (topic mastered). The knowledge status
is calculated from the last solution attempts (= ProblemLogs) of every linked
problem.

```tag_knowledge = weighted_avg_score * experience```

#### Weighted avg. score
Problems are rated in three categories: easy, medium, hard.
It is reasoned that:
- easy problems signify the introduction of a topic
- medium problems are more representative of actual
  topic knowledge as well as interview questions
- hard problems are rather edge-cases or advanced interview
  questions --> having strong results here shows that one fully masters
  a topic.

Therefore, the score per algorithm is determined from the
knowledge scores achieved when last solving it's linked problems via this
algorithm (= logged problem-tag-combinations), averaged per difficulty:
```weighted_knowledge_score = max(0.5 * avg_easy_score,  0.75 * avg_med_score, avg_hard_score)```

#### Experience
Algorithms can be applied in a variety of ways and, in some cases, for
very different problem types. To track the knowledge of different
algorithmic topics correctly, it does make sense to choose topics in
a rather fine-grained manner.
Per such fine-grained topic, a minimum of 5 problems is deemed necessary
to cover it, i.e. to reach full 'experience'. Hence:  
```experience = max(1, num_problems_linked_to_tag/ 5)```


### Knowledge Scores
Problems may be solved optimally via different algorithms.
E.g.: assume a problem can be solved optimally by either of two algorithms A and
B; we want to study both.
We last solved the problem by applying algorithm A 3 weeks ago with a score of 4,
and solved it via algorithm B 2 weeks ago with a score of 2. Which one should
we rehearse more urgently? We got a better result with algorithm A, but we may
have forgotten more of it since it has been longer.

To determine which algorithm application case rehearsal more urgently, we rank
problem-tag-combinations via a **knowledge score KS** between 0 and 5, where:
* 0  --> no knowledge
* 5 --> perfect knowledge

**KS** is computed as the product of the **Correctness Score C** achieved
when last solving the problem with the linked algorithm, and the
**Retention Factor RF**:  
```KS = C * RF```

#### Correctness Score C
There are 6 possible values for the correctness score: `C in [0..5]`
These are mapped to the following possible outcomes of solving a problem
with specific algorithm(s):

| Attempt result | Correctness Score |
|---|---|
| KNEW_BY_HEART                       | 5 |
| SOLVED_OPTIMALLY_IN_UNDER_25 (mins) | 4 |
| SOLVED_OPTIMALLY_SLOWER             | 3 |
| SOLVED_OPTIMALLY_WITH_HINT          | 2 |
| SOLVED_SUBOPTIMALLY                 | 1 |
| NO_IDEA                             | 0 |

#### Retention Factor RF
According to literature, humans forget learned content in some
exponential form. Study and repetition algorithms have been developed to
counter forgetting.
For memorizing smaller bits of information (e.g. Flash card style studying),
[SuperMemo_2](https://en.wikipedia.org/wiki/SuperMemo) (SM2) is one of
the most popular ones. This algorithm is used to schedule repetitions
of active recall sessions such that knowledge is committed to long-term memory
with the least amount of actual study time.

Here however, I am not only interested in scheduling repetition times.
I also want to estimate my knowledge of all relevant topics, to study
the most urgent one when I have time.

To get the best of both worlds, spaced-repetition calculates the optimal
rehearsal dates. Once past that date, the algorithm estimates how much of
the once acquired knowledge has been forgotten.

Therefore, upon revision of a problem at time t_0, the next intended
repetition time t_1 is calculated via a modified version of SM2 (see differences
to SM2 below).<br>
Concretely: t_1 = t_0 + T, where T is the spacing interval calculated via SM2.<br>
When reaching a time t_2 > t_1 (i.e. past the scheduled repetition time), it is
assumed that the user starts to forget in an exponential manner.<br>
Specifically, it is assumed that once another
spacing interval T has passed after the scheduled repetition time t_1,
the user remembers only the fraction '**a**' of the original knowledge
present at time t_0.
Hence the **Retention Factor RF** is introduced, which calculates
exactly that:

![retention_factor](./docs/RF.svg),

where:
* **a** is the fraction of remembered knowledge, **T** days after the
scheduled repetition
* **delta_t** is the time that has gone by since the scheduled
repetition (= max(0, t - t_1))

'a' is currently set to 0.5 -> T after the next scheduled repetition time t_1,
the user is assumed to have forgotten half of their knowledge.

In summary: The retention factor RF diminishes the KnowledgeScore KS when the
user does not repeat a problem as scheduled. This, in some way, represents
how much the user remembers of each topic and allows to rank problems by
'urgency of repetition'.


### Differences to SM2
See the description of SM2 as reference on
[Wikipedia](https://en.wikipedia.org/wiki/SuperMemo).

##### Learning phase
In typical spaced repetition programs, one first has to complete a
'learning phase' before entering the 'spaced repetition' phase.
This does not seem applicable to studying algorithmic topics, as the tools
to solve the individual problems overlap largely between problems. Hence
the 'learning phase' is skipped.

##### Spacing interval T
In SM2, each question starts out with a spacing interval of 1 day,
which is then grown via the 'ease', which in turn is influenced by
the scores achieved when recalling knowledge. Knowledge acquired when deriving
solutions to problems however seems to fade slower than knowledge acquired
through pure memorization. This is especially true when we can reuse knowledge
acquired in other problems. Hence, the minimum spacing interval T depends on the
score achieved during the last review of the problem:

| Attempt result | Score |
|---|---|
| KNEW_BY_HEART                  | 30 |
| SOLVED_OPTIMALLY_IN_UNDER_25   | 14 |
| SOLVED_OPTIMALLY_SLOWER        | 7 |
| any worse result               | 3 |


## Architecture
The architecture has been designed according to the guidelins of
Robert Martin's book 'Clean Architecture', an excerpt of which can be
found on his blog: [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).  
Having worked in fast growing organizations where time for
development was short and future develpoments uncertain, I have always
looked for ways of efficiently developing a new product whilst keeping
it as flexible as possible for future changes. Quickly growing
requirements, framework changes or scaling a product can lead to major
issues if the product's architecture has not been considered early
enough.
'The Clean Architecture' offers basic guidelines that can be applied
to most projects in varying degrees of detail, depending on project
scope and status.

In this project, I chose a medium-strict approach where:
* Key Logic and the required data structures live in the 'use_cases' and
'domain' directories and are independent of external implementation
details, such as:
  * how the user interacts with them (e.g. via CLI or a potential web
  interface)
  * how their outputs are visualized
  * 'detail' implementations, such as the database or ORM
* The database is organized via Django ORM because I know it best and
wanted to spend as little time as possible here. Core logic accesses
the db via a 'db_gateway_interface' and is completely independent from
the actual implementation. It could be swapped for any other
db or ORM (e.g. SqlAlchemy).
* The directory 'Presenters' contains the tools to display computation
results to the user. These can be exchanged freely as long as they
implement the PresenterInterface. Currently, only a basic 'CLI'
Presenter has been implemented.
  
### Overview
The following diagram sketches the described structure:
![architecture](./docs/architecture_overview.svg),
