Here's your complete guide, transformed into **Markdown** format for easy readability and use in tools like Jupyter Notebook or GitHub:

---

# 📘 Comprehensive Guide: Matplotlib, Seaborn, Pandas, NumPy, and Scikit-Learn

---

## 1. 📊 MATPLOTLIB

Matplotlib is a widely used plotting library in Python that provides granular control over figure creation and customization.

### A. Subplots & Figure Creation

#### 1. Mosaic Layout

```python
import matplotlib.pyplot as plt

fig = plt.figure(constrained_layout=True, figsize=(10, 8))
mosaic = {'Top': (0, 0, 1, 2), 'Bottom Left': (1, 0), 'Bottom Right': (1, 1)}
axs = fig.subplot_mosaic(mosaic)

axs['Top'].plot([1,2,3], [4,5,6])
axs['Bottom Left'].bar(['A','B','C'], [3,7,1])
axs['Bottom Right'].scatter([1,2,3], [3,1,4])
plt.show()
```

#### 2. Using `fig.subplots()`

```python
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].plot([1,2,3], [4,5,6])
axes[1].bar(['A','B','C'], [3,7,1])
plt.show()

# Remove extra subplot
fig.delaxes(axes[-1])
```

#### 3. Manually Adding Axes

```python
fig = plt.figure(figsize=(20,7))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
ax.plot([1,2,3], [4,5,6])
plt.show()
```

### B. Axis Customization

#### 1. Labels & Ticks

```python
plt.plot([1,2,3], [4,5,6])
plt.xlabel("Time")
plt.ylabel("Value")
plt.xticks(rotation=45)
plt.show()
```

#### 2. Axis Limits

```python
plt.plot([1,2,3], [4,5,6])
plt.xlim(0, 4)
plt.ylim(3, 7)
plt.show()
```

#### 3. Equal Aspect Ratio

```python
plt.plot([1,2,3], [1,4,9])
plt.axis('equal')
plt.show()
```

### C. Annotations and Legends

#### 1. Text

```python
plt.plot([1,2,3], [4,5,6])
plt.text(2, 5, "Center", fontsize=12, color="blue")
plt.show()
```

#### 2. Annotation

```python
fig, ax = plt.subplots()
ax.plot([1,2,3], [4,5,6], marker='o')
ax.annotate("Peak", xy=(3,6), xytext=(2,7),
            arrowprops=dict(arrowstyle="->"), va="top", ha="left")
plt.show()
```

#### 3. Legend

```python
plt.plot([1,2,3], [4,5,6], label="Line 1")
plt.legend(loc="upper right")
plt.show()
```

### D. Layout Adjustments

#### 1. Manual

```python
fig, axes = plt.subplots(2, 2, figsize=(10,8))
plt.subplots_adjust(hspace=0.3, wspace=0.3)
plt.show()
```

#### 2. Auto

```python
fig, axes = plt.subplots(2, 2, figsize=(10,8))
plt.tight_layout()
plt.show()
```

### E. Pie Chart / Donut Chart

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

newdf = {'Grade': ['A', 'B', 'C'], 'Weekly_Study_Hours': [30, 50, 20]}
newdf = pd.DataFrame(newdf).set_index('Grade')

colors = [plt.cm.viridis(i) for i in np.linspace(0.1, 0.9, len(newdf))]

fig, ax = plt.subplots()
wedges, texts, autotexts = ax.pie(newdf['Weekly_Study_Hours'], startangle=290,
                                  labels=newdf.index, colors=colors,
                                  autopct="%1.1f%%", pctdistance=0.5)

for i, wedge in enumerate(wedges):
    wedge.set_facecolor(colors[i])
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_rotation(50)
    autotext.set_size('small')

plt.title("Grades With Weekly Study Hours Percentage")
plt.axis('equal')
plt.show()
```

---

## 2. 🎨 COLORS

Hexadecimal color codes use `#RRGGBB`.

Example:

```python
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
```

---

## 3. 📅 DATETIME

```python
import datetime as dt
date_obj = dt.datetime.strptime("Jan", "%b")
print(date_obj)
```

---

## 4. 📈 SEABORN PLOTTING

### A. Pairplot

```python
import seaborn as sns
import pandas as pd

df = pd.DataFrame({'A': [1,2,3,4], 'B': [4,3,2,1], 'C': [2,3,4,5]})
sns.pairplot(df)
plt.show()
```

### B. Other Common Plots

- Countplot: `sns.countplot(x="category", data=df)`
    
- Jointplot: `sns.jointplot(x="var1", y="var2", data=df, kind="scatter")`
    
- Heatmap:
    

```python
sns.heatmap(df.corr(), annot=True, cmap="BuGn")
plt.show()
```

### C. Style Settings

```python
sns.set(style="darkgrid", palette="pastel", context="poster")
```

---

## 5. 🔁 CUSTOM VISUALIZATION FUNCTIONS

### A. Stacked Bar Plot

```python
def stack_bar(data, var1, var2, cmap, title):
    ct = pd.crosstab(data[var1], data[var2])
    ct.plot(kind='bar', stacked=True, colormap=cmap)
    plt.title(title)
    plt.show()
```

### B. Donut Chart

```python
def plot_ring_chart(data, labels, colors=None, title="Ring Chart", autopct='%1.1f%%', radius=0.75):
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(data, labels=labels, colors=colors, autopct=autopct,
                                      wedgeprops={'edgecolor': 'white'})
    circle = plt.Circle((0, 0), radius, color='white')
    ax.add_artist(circle)
    plt.title(title)
    ax.axis('equal')
    plt.show()
```

---

## 6. 🐼 PANDAS & NUMPY ESSENTIALS

### A. Pandas

- Sorting: `df.sort_values(by="column")`
    
- Handling Missing: `df.dropna()`, `df.fillna(method='ffill')`
    
- Indexing/Filtering:
    

```python
df.loc[df['Age'] > 28]
df.loc[df['Name'] == 'Alice', 'Age'] = 26
```

- GroupBy:
    

```python
grp = df.groupby('Category')
for key in grp.groups.keys():
    print(grp.get_group(key))
```

- Merge: `pd.merge(df1, df2, on="common_column", how="inner")`
    
- Date Conversion: `pd.to_datetime(series, format='%Y-%m-%d')`
    
- Query: `df.query("Age > 30")`
    

### B. NumPy

- Indexing: `arr[[1,2,3]]`
    
- Linspace: `np.linspace(0, 1, 5)`
    
- Utility: `np.where()`, `np.abs()`, `np.round()`
    

---

## 7. ⚙️ SCIKIT-LEARN TOOLS

### A. Preprocessing

```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### B. ColumnTransformer

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

ct = ColumnTransformer([('encoder', OneHotEncoder(), ['col'])], remainder='passthrough')
X_transformed = ct.fit_transform(X)
```

### C. FunctionTransformer

```python
from sklearn.preprocessing import FunctionTransformer

def logtrans(x): return np.log(x)
transformer = FunctionTransformer(logtrans)
```

### D. Regression

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso

model = RandomForestRegressor()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

### E. Evaluation

```python
from sklearn.metrics import mean_squared_error, r2_score
print(mean_squared_error(y_test, y_pred), r2_score(y_test, y_pred))
```

### F. Classification

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

### G. Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV
param_grid = {'n_estimators': [50,100,150]}
grid = GridSearchCV(RandomForestRegressor(), param_grid, cv=5)
grid.fit(X_train, y_train)
```

### H. Feature Selection

```python
from sklearn.feature_selection import f_regression
F, p = f_regression(X, y)

from statsmodels.stats.outliers_influence import variance_inflation_factor
vif = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
```

### I. Clustering

```python
from sklearn.cluster import KMeans
inertias = []
for i in range(1, 10):
    kmeans = KMeans(n_clusters=i)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)
```

### J. Resampling

```python
from sklearn.utils import resample

# Bootstrap
boot = resample(df, replace=True, n_samples=5, random_state=42)

# Stratified
strat = resample(df, n_samples=6, stratify=df['Label'])

# Oversample
minority_up = resample(minority, replace=True, n_samples=len(majority), random_state=42)
balanced = pd.concat([majority, minority_up])
```

### K. PCA

```python
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
```

### L. Remove Less-Correlated Features

```python
def lesscorr(data, target, thres):
    corr_df = data.corr()
    return {col for col in data.columns if abs(corr_df.loc[col, target]) < thres}
```

### M. Skewness

```python
from scipy.stats import skew
skewness = skew([1,2,2,3,4,5,6,8,10,20])

sns.histplot([1,2,2,3,4,5,6,8,10,20], kde=True)
plt.show()
```

### N. Misc. Pandas/NumPy

```python
pd.cut(), df.value_counts(), df.nunique(), df.duplicated()
df.head(), df.tail(), df.reset_index(), df.set_index()
pd.get_dummies(), df.join(), np.abs(), np.round(), np.where()
```

### O. Cross-Validation

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)

from sklearn.metrics import classification_report, confusion_matrix
print(classification_report(y_true, y_pred))
print(confusion_matrix(y_true, y_pred))
```

---

🧠 **End of Guide**  
Now you can directly copy-paste this Markdown into a `.md` file or a Jupyter Notebook cell for interactive use. Let me know if you want this exported to a downloadable `.md` file or PDF.