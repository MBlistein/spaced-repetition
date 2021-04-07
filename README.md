## Purpose
This project has been implemented for two reasons:
* to create a tool for effective study of algorithmic problems via
  'spaced repetition' and 'active recall' techniques
* to implement a project following Martin Robert's guidelines in his
  book 'Clean Architecture.

This is an experimental project and implements a minimalist
solution for personal need -> please use with care, feedback is welcome
:-).

## Setup
* clone the repository and cd into it
* create a virtual environment, e.g.: `python3 -m venv <your_env_name>`
* activate the environment: `source <path_to_venv>/bin/activate
* install required packages: `pip install -r requirements.txt`

Run the CLI with the '-h' flag to see possible actions:
`python3 scripts/run_cli.py -h`

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
solve problems related to that topic. It then calculates when we should
re-solve the same problem to get to and maintain the desired knowledge
level.

To use this program, the user should just start solving algorithmic
problems. When encountering a problem that is
somewhat representative of a standard algorithm or a typical application
case, this problem should be added to the 'spaced-repetition' database
via `python3 scripts/run_cli.py add-problem`.

The corresponding dialogue will ask to link the problem to at least one
tag (representative of an algorithmic topic, e.g. 'dfs'). Tags should be
as fine-grained as necessary. They need to exist before a problem can
be linked to them. Create a tag via:
`python3 scripts/run_cli.py add-tag`.

Every attempt at solving a tracked problem should be tracked via the
'spaced-repetition' tool. This is possible via:
`python3 scripts/run_cli.py add-log`.  
The corresponding dialogue asks the user to grade how well she/ he was
able to solve the problem on a provided scale. From this and previous
results, the underlying algorithm calculates a 'knowledge score' as well
as the next repetition date for both this problem and the tags linked
to the problem. For more details, see the section 'Algorithm' below.

## Algorithm
The spaced-repetition toolbox should:
* give an overview of the knowlege level across all topics
* schedule problem repetitions to reach desired knowledge levels with
the least effort possible
* rank the topics and problems inside a topic by urgency (which topic
needs work the most?)

To achieve this, the following ranking algorithm has been devised.

### Problems
Problems are ranked via a **knowledge score K** between 0 and 5, where:
* 0  --> no knowledge, highest priority topic
* 5 --> perfect knowledge, no further study necessary

**K** is computed as the product of the **Correctness Score C** achieved
when last solving the problem, and the **Retention Factor RF**:  
```K = C * RF```

#### Correctness Score C
There are 6 possible values for the correctness score: `C in [0..5]`
These are mapped to the possible problem solving attempt results as
follows:

| Attempt result | Score |
|---|---|
| KNEW_BY_HEART                  | 5 |
| SOLVED_OPTIMALLY_IN_UNDER_25   | 4 |
| SOLVED_OPTIMALLY_SLOWER        | 3 |
| SOLVED_OPTIMALLY_WITH_HINT     | 2 |
| SOLVED_SUBOPTIMALLY            | 1 |
| NO_IDEA                        | 0 |

#### Retention Factor RF
According to literature, humans forget learned content in some
exponential form. Study and repetition algorithms have been developed to
counter forgetting.
For memorizing smaller bits of information (e.g. Flash card style studying),
[SuperMemo_2](https://en.wikipedia.org/wiki/SuperMemo) or SM2 is one of
the most popular ones. This algorithm is used to schedule repetitions
of active recall sessions such that knowledge is committed to memory
with the least amount of effort.

Here however, I am not only interested in scheduling repetition times.
Instead, I want to estimate my knowledge of all studied topics, to study
the most urgent one when I have time.  
Therefore, upon revision of a problem at time t_0, the next intended
repetition time t_1 is calculated via a modified version of SM2.  
Concretly: t_1 = t_0 + T, where T is the spacing interval calculated via SM2.
It is assumed that, when reaching a time t_2 > t_1, the user starts to
forget in an exponential manner.  
Specifically, it is assumed that once another
spacing interval T has passed after the scheduled repetition time t_1,
the user remembers only the fraction '**a**' of the original knowledge
she/ he had at time t_0.
Hence the **Retention Factor RF** is introduced, which calculates
exactly that:

![Alt text](./docs/RF.svg),

Where:
* **a** is the fraction of remembered knowledge **T** days after the
scheduled repetition
* **delta_t** is the time that has gone by since the scheduled
repetition (= max(0, t - t_1))

'a' is currently set to 0.5 -> T after the next scheduled repetition,
the user is assumed to have forgotten half of their knowledge.

### Tags (= Topics)
For every tag, a 'per-tag priority' between 0 (high need to catch up)
and 5 (topic mastered) is calculated. The priority for every tag is
calculated as:

    prio = avg_weighted_problem_prio * experience

#### Avg. weighted problem prio
Problems are rated in three categories: easy, medium, hard.
The avg_weighted_prio is calculated as the weighted sum of the average
priority of each of these degrees of difficulty.
It is reasoned that:
 - easy problems signify the introduction of a topic
 - medium problems are more representative of actual
   topic knowledge as well as interview questions
 - hard problems are rather edge-cases or advanced interview
   questions --> Having strong results here shows that one fully masters
   a topic.

Therefore, the total average score for a tag is determined as:  
weighted_avg_score = 0.25 * avg_easy + 0.5 * avg_med + 0.25 * avg_hard

#### Experience
Algorithms can be applied in a variety of ways and, in some cases, for
very different problem types. To track the knowledge of different
algorithmic topics correctly, it does make sense to choose topics as
fine-grained as possible.
Per such fine-grained topic, a minimum of 5 problems is deemed necessary
to cover it, i.e. to reach full 'experience'. Hence:  
experience = max(1, num_problems/ 5)


### Differences to SM2
See the description of SM2 as reference on
[Wikipedia](https://en.wikipedia.org/wiki/SuperMemo).

##### Learning phase
In typical spaced repetition programs, one first has to complete a
'learning phase' before entering the 'spaced repetition' phase.
This does not seem applicable to studying algorithmic topics, as the tools
to solve the individual problems overlap largely between problems. Hence
the 'learning phase' is skipped.

##### Initial spacing interval T
In SM2, each question starts out with a spacing interval of 1 day,
which is then grown via the 'ease', which in turn is influenced by
the scores achieved when recalling knowledge. Here however, the initial
spacing interval T depends on the score achieved on the initial review
of the problem:

| Attempt result | Score |
|---|---|
| KNEW_BY_HEART                  | 21 |
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
* The database is organized via Django ORM (because I know it best and
wanted to spend as little time as possible here). Core logic accesses
the db via a 'db_gateway_interface' and is completely independent from
the actual implementation. It could be swapped for any other
db or ORM (e.g. SqlAlchemy).
* The directory 'Presenters' contains the tools to display computation
results to the user. These can be exchanged freely as long as they
implement the PresenterInterface. Currently, only a basic 'CLI'
Presenter has been implemented.

