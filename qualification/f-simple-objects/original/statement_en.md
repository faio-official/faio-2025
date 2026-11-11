## Story

In the bustling city of **Geometria**, young architect-in-training, Adilkhan, has been entrusted with a crucial task: to analyze the blueprints of the new “**PolyPark**” — a futuristic recreational complex designed entirely from basic geometric shapes. The mayor of the city Darkhan needs to know exactly how many distinct geometric figures (triangles, rectangles, circles, etc.) are embedded in each blueprint to estimate material costs, assign construction teams, and schedule 3D-printing robots.

Unfortunately, Adilkhan‘s assistant accidentally saved all blueprints as RGB image files, but not as vector diagrams or CAD files. Thus the automated counting software is down for maintenance! With the deadline looming in 5 hours, Adilkhan turns to **your team**, a brilliant high school problem-solvers.

Each blueprint image contains between **100 and 500** distinct geometric figures. Figures may vary in size, color, and orientation, but they are always cleanly drawn with solid borders and do not overlap or intersect in ambiguous ways (i.e., each figure is clearly separable). Your mission: write a program (or devise a method) that, given an RGB image of a blueprint, outputs the **exact number** of geometric figures present.

## Formal Problem Statement

You are given an image in standard RGB format (e.g., PNG or JPG) with dimensions of $2048 \times 2048$ pixels. The image contains $N$ geometric figures ($100 \leq N \leq 500$), each of which is one of the following: triangle, rectangle, or circle. Figures are drawn with solid colored borders (stroke) and may have transparent or solid-colored interiors. Background is distinguishable from figure borders.

## Input

- One RGB image file per test case.
- The image will be provided in a standard format readable by common image libraries (e.g., OpenCV, PIL).
- Figures do not overlap in a way that merges their borders. Each figure is a single connected component when considering edge pixels.

## Output

- A csv file (submit.csv) with single integer in each row: the total number of geometric figures detected in the image.

**Important:** Submit only the submit.csv file. Source code is not required. The order of id values in submit.csv must strictly follow the order in test.csv, starting from 0 up to the highest ID.

## Evaluation

- Your solution will be tested on 8000 images.
- Evaluation metric is **Customized Accuracy**, which is defined by the formula below

$$\text{Error Rate} = \frac{ \left| \hat{y} - y \right| }{ y }$$

$$\text{Accuracy} = 1 - \min\left(1, \text{Error Rate}\right)$$

$$\text{Final Verdict} = \begin{cases} 0, & \text{if } \text{Accuracy} > 0.55 \\ \frac{\text{Accuracy} - 0.55}{1 - 0.55}, & \text{otherwise} \end{cases}$$

$$\textbf{Legend:} \quad \hat{y} = \text{model prediction}, \quad y = \text{ground-truth count (label)}$$

## Example

**Input Image:**

![image](https://assets.contest.yandex.net/testsys/statement-file?hash=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..NBCYwTitn1Ep-5km.X8hicjATYlClI_1goIeAffL2HWdftKLZqbar9-fkm0gtlOj1Uqixp3Ss5iej2j_ZBNvZB0KGgJMpNuAxD76XJFnHCFfGMPP49PednsCHa79IK8Ijrg.EnGtawx5o3xPVT579pKUog)

Example: contains 1 red triangle, 1 blue circle, 1 green rectangle)

**Your Output:**  
 `3`

Files:

- [train.csv](https://disk.yandex.com/d/mJ2Wqw1VmAS97Q)
- [train images](https://disk.yandex.com/d/_Jyxim1o5Ylzig)
- [test images](https://disk.yandex.com/d/yzaAMlkcbyqStw)
- [submit.csv](https://disk.yandex.com/d/ABq-mBGRiOYOUw)

## Tips for Students

- You may use any programming language and libraries (OpenCV, scikit-image, PIL, etc.).
- Consider edge detection, contour finding, and shape classification using properties like number of corners, aspect ratio, or circularity.
- Remember: you only need to **count** the figures — not classify them by type (unless it helps your counting logic).
- Test your solution on varied examples: small figures, large figures, different colors, rotated shapes.

## Why This Matters

In real-world computer vision, counting and detecting objects in images is essential, from counting cells in medical imaging to detecting vehicles in traffic cameras. This problem simulates a practical engineering challenge while sharpening your skills in image processing and machine learning.

Good Luck!

Sincerely yours,

— *The Geometria City Mayor, Darkhan*
