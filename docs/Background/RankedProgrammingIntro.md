This project is a Python implementation of the concepts introduced in the paper "Ranked Programming" by Tjitze Rienstra. It explores a novel approach to modeling uncertainty that is not based on probability.

### **Core Idea**

While probabilistic programming is a powerful tool, not all uncertainty is probabilistic. Some types of uncertainty are better described by distinguishing between what is "normal" and what is "exceptional". For instance, in fault diagnosis, we might know that a component normally works and only exceptionally fails, without knowing the specific probabilities of failure.

This is where **Ranking Theory** comes in. Instead of probabilities, it uses "ranks" to measure uncertainty as degrees of surprise. A rank is an integer on a scale from 0 to infinity:

* **Rank 0:** Not surprising (a normal occurrence)  
* **Rank 1:** Surprising (an exceptional occurrence)  
* **Rank 2:** Even more surprising  
* **Infinity (∞):** Impossible

### **Ranked Programming**

This project implements a programming model based on these principles, originally proposed in the paper as "Ranked Scheme," an extension of the Scheme programming language. The goal is to provide a simple and flexible way to create models that involve uncertainty, but with a computationally simpler, coarser-grained approach than traditional probabilistic methods.

In this model, expressions can have ranked choices, which normally return one value (with a rank of 0\) but can exceptionally return another (with a rank of 1 or higher). The final rank of a result can be thought of as the number of exceptions that had to occur for that result to be produced. The system can then perform inference on these models to find the least surprising outcomes given certain observations.

This approach has been used to model various problems, including:

* Diagnosing faults in boolean circuits  
* Spelling correction algorithms  
* Ranking-based Hidden Markov Models  
* Ranking networks for diagnostics This project provides a Python implementation of the concepts presented in the paper "Ranked Programming" by Tjitze Rienstra.

While probabilistic programming is a powerful paradigm for handling uncertainty, not all uncertainty is probabilistic. This project explores an alternative approach using **ranking theory**, where uncertainty is expressed in terms of "surprise" rather than probability.

In ranked programming, we distinguish between *normal* and *exceptional* behavior. Events are assigned ranks, which are integer values representing their degree of surprise:

* **Rank 0:** A normal, unsurprising event.  
* **Rank 1, 2, 3...:** Increasingly surprising or exceptional events.  
* **Rank ∞:** An impossible event.

This approach offers a simpler, more coarse-grained way to model and reason about uncertainty, particularly in scenarios where precise probabilities are unknown or irrelevant. Examples include fault diagnosis, where components normally work but exceptionally fail, or processing sensor data that is usually correct but occasionally faulty.

This library, inspired by the *Ranked Scheme* language presented in the paper, extends Python with the ability to:

* Define models that incorporate both normal and exceptional outcomes.  
* Perform inference on these models to determine the least surprising explanation for observed data.

The core idea is to build programs that, instead of returning single values, return ranking functions over a range of possible values. The rank of each value quantifies the number of exceptional occurrences required to produce it. This allows for elegant reasoning about systems with uncertain behaviors.