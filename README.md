## Purpose
* try clean architecture approach
* needed spaced repetition algo for studying algorithmic problems, and
  determining how well I knew each category
  
## Prioritization Algorithm
The spaced-repetition toolbox should let one find out:
* on which topic I need to work most urgently
* on which problem inside a topic I should work most urgently (or add a new one)

### Problems
Problems are ranked via a **knowledge score K** between 1 and 10, where:
* 1  --> no knowledge, highest priority topic
* 10 --> perfect knowledge, no further study necessary  

**K** is computed as the product of the **Correctness Score C** achieved when
solving the problem, and the **Retention Factor RF**:  
```K = C * RF```

#### Correctness Score C
There are 5 possible values for the correctness score: `C in [0..5]`

Todo: move the table below to the 'usage' section:
These are mapped to the possible problem solving attempt results (which can
be selected via the CLI) as follows:

| Attempt result | Score |
|---|---|
| KNEW_BY_HEART                  | 4 |
| SOLVED_OPTIMALLY_IN_UNDER_25   | 3 |
| SOLVED_OPTIMALLY_SLOWER        | 2 |
| SOLVED_OPTIMALLY_WITH_HINT     | 1 |
| SOLVED_SUBOPTIMALLY            | 1 |
| NO_IDEA                        | 0 |


#### Retention Factor RF
According to literature, humans seem to forget learned content in some
exponential form. Study and repetition algorithms have been developed to
counter forgetting.
For memorizing smaller bits of information (e.g. Flash card style studying),
[SuperMemo_2](https://en.wikipedia.org/wiki/SuperMemo) or SM2 is one of the most
popular ones. This algorithm is used to schedule repetitions of active recall
sessions.

Here however, I am less interested in strictly scheduling study times. Instead,
I want to estimate my knowledge of all studied topics, to study the most urgent
one when I have time.  
Therefore, upon revision of a problem at time t_0, I do calculate the intended
spacing interval T via SM2, and assume that I remember the studied problem until
then. When reaching a time t_1 > t_0 + T, I assume that I start to forget
exponentially. Concretely, I assume that I have forgotten half of my knowledge
required to solve the problem when I am one spacing Interval past the intended
repetition time, at:  
```t_0.5 = t_0 + 2 * T```.

Hence the **Retention Factor RF** is introduced, which calculates exactly that:

![Alt text](./docs/RF.svg)

Where:
* **T** is the intended spacing interval after the last repetition as calculated
  by SM2
* **delta_t** is the time that has gone by since the last revision of the problem
 
##### Spacing Interval T
Note: In typical spaced repetition programs, one first has to complete a
'learning phase' before entering the 'spaced repetition' phase.
This does not seem as applicable to studying algorithmic topics, as the tools
to solve the individual problems overlap largely between problems. Hence the
'learning phase' is skipped here. It is replaced by a steep Interval growth

## Setup
- setup venv as in my .sh
  
## How to use
- looking back, not planning forward. If unsure if you should add a new category or do a recent problem, just get the next most urgent problem and see if you handled that topic just a short while ago.
