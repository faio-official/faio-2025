## Story

Two interns, **Adilkhan** and **Darkhan**, have just started working as data scientists in the **NLP team** at a large telecom company. Their team lead, suggested their very first task: to improve the company’s customer service chatbot.

Since the telecom has millions of customers speaking in **Kazakh**, **Russian**, and **English**, a crucial requirement is to detect the customer’s language correctly from the very first query. Without accurate language identification, the chatbot might respond in the wrong language, frustrating the user.

To solve this, Adilkhan and Darkhan compiled a dataset of real conversational messages collected from the company’s support system. They prepared two files: `train.csv` and `test.csv`, each containing short conversational texts labeled with one of three languages: `“ru”`, `“kaz”`, or `“eng”`.

Now it is your mission to build a model that can accurately predict the language of any incoming text. Your help is vital, if Adilkhan and Darkhan succeed, they will **pass their internship** and become full-time NLP engineers!

## Formal Problem Statement

You are given two CSV files:

- `train.csv`: Contains training data in the form of text samples with their corresponding labels (`ru`, `kaz`, `eng`).
- `test.csv`: Contains only text samples, without labels. Your model must predict the correct label for each test example.

The dataset can be accessed here:

- [Train dataset](https://drive.google.com/file/d/1XUD55k0pOmVhTXIGqTzqCdNUVowwsiZT/view?usp=sharing)
- [Test dataset](https://drive.google.com/file/d/1kQpO0guFWuVnuBjQB8vzQtS8T6IgzT2-/view?usp=sharing)

## Input

- `train.csv` with columns: `text`, `label`.
- `test.csv` with column: `text`.
- Labels are one of: `ru`, `kaz`, `eng`.

## Output

Participants must submit only a CSV file named **solution.csv**, with the following format:

```
id,label
0,eng
1,kaz
2,ru
...
```

**Important:** Submit only the `solution.csv` file. Source code is not required. The order of `id` values in `solution.csv` must strictly follow the order in `test.csv`, starting from `0` up to the highest ID.

## Evaluation

- Your predictions will be evaluated using the **Macro F1-score**.
- Final competition score is normalized as follows:
  - If F1-score $< 0.6$: score = 0.
  - If F1-score $= 1.0$: score = 100.
  - For values in between: $$\text{score} = \frac{F1 - 0.6}{1.0 - 0.6} \times 100$$

## Example

**Input (`test.csv`):**

```
id,text
0,Hello, how are you?
1,Сәлеметсіз бе?
2,Привет, как дела?
```

**Your Output (`solution.csv`):**

```
id,label
0,eng
1,kaz
2,ru
```
