## Problem Statement

**The correct answer to this problem is worth 10 points.**

You roll a standard 6-sided die **three times** in a row.

## Theory

### Probability of an Event

#### In Simple Terms 🧸

Probability is simply a way to measure chance. Imagine a bag with 10 marbles: 7 blue and 3 red. The chance of drawing a red marble is 3 out of 10. This is its probability. It shows what fraction of all possible outcomes is favorable to us.

#### Formal Definition 🎓

Probability is a numerical measure of the likelihood of a random event occurring. For the classical definition, where all elementary outcomes are equally likely, the probability of an event $A$ is calculated as the ratio of the number of outcomes favorable to the event ($m$) to the total number of possible outcomes ($n$). $$P(A) = \frac{m}{n}$$ The value of a probability is always in the range from 0 (impossible event) to 1 (certain event).

#### Application in ML and Data Analysis 🤖

This is the foundation of everything.

- **Classification:** A model determines the probability that an email is spam. If $P(\text{spam}) > 0.8$, the email is sent to the "Spam" folder.
- **Scoring:** A banking model calculates the probability that a client will default on a loan. A decision on loan issuance is made based on this value.

## Output Format and Question

What is the probability that you will roll **at least one** six?

Submit a **CSV file** with the header `answer` and a **single data row** containing this probability as a decimal fraction with four digits after the decimal point, for example:

```
answer
0.3145
```

The answer is worth **10 points**: you get the full score if your value is within `1e-4` of the correct answer, otherwise 0.
